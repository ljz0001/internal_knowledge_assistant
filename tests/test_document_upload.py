from unittest.mock import Mock

import pytest

from app.api.routers import rag
from app.api.main import app
from app.db.crud import knowledge_document_crud
from app.db.models.knowledge_document import DocumentStatus
from app.rag import document_manager, rag_server


def test_file_hash_is_stable_and_content_sensitive():
    first_hash = document_manager.calculate_file_hash(b"same content")

    assert first_hash == document_manager.calculate_file_hash(b"same content")
    assert first_hash != document_manager.calculate_file_hash(b"different content")


def test_upload_openapi_schema_uses_binary_file_input():
    schema = app.openapi()["paths"]["/rag/uploads"]["post"]["requestBody"]
    file_items = schema["content"]["multipart/form-data"]["schema"]["properties"]["files"]["items"]

    assert file_items == {"type": "string", "format": "binary"}


def test_file_size_limit_is_enforced(monkeypatch):
    monkeypatch.setattr(document_manager, "MAX_UPLOAD_SIZE", 4)

    with pytest.raises(ValueError, match="超过大小限制"):
        document_manager.validate_file("large.txt", b"12345")


@pytest.fixture
def document_storage(tmp_path, monkeypatch):
    """让文件测试只读写 pytest 的临时目录，绝不影响项目真实 docs/uploads。"""
    uploads_dir = tmp_path / "uploads"
    docs_dir = tmp_path / "docs"
    uploads_dir.mkdir()
    docs_dir.mkdir()
    monkeypatch.setattr(document_manager, "UPLOADS_DIR", uploads_dir)
    monkeypatch.setattr(document_manager, "DOCS_DIR", docs_dir)
    return {"uploads": uploads_dir, "docs": docs_dir}


def test_upload_single_file_creates_pending_record(client, document_storage):
    response = client.post(
        "/rag/uploads",
        files=[("files", ("制度.txt", "企业制度正文", "text/plain"))],
    )

    assert response.status_code == 201
    result = response.json()["data"]
    assert result["failed"] == []
    assert len(result["uploaded"]) == 1
    document = result["uploaded"][0]
    assert document["original_name"] == "制度.txt"
    assert document["status"] == DocumentStatus.PENDING
    assert (document_storage["uploads"] / document["stored_name"]).read_text(encoding="utf-8") == "企业制度正文"


def test_upload_multiple_files_creates_one_record_per_file(client, document_storage):
    response = client.post(
        "/rag/uploads",
        files=[
            ("files", ("a.txt", "A", "text/plain")),
            ("files", ("b.md", "# B", "text/markdown")),
        ],
    )

    assert response.status_code == 201
    documents = response.json()["data"]["uploaded"]
    assert {item["original_name"] for item in documents} == {"a.txt", "b.md"}
    assert len(list(document_storage["uploads"].iterdir())) == 2


def test_upload_rejects_unsupported_type(client, document_storage):
    response = client.post(
        "/rag/uploads",
        files=[("files", ("制度.docx", b"not supported", "application/octet-stream"))],
    )

    assert response.status_code == 201
    assert response.json()["data"]["uploaded"] == []
    assert "不支持的文件格式" in response.json()["data"]["failed"][0]["error"]
    assert list(document_storage["uploads"].iterdir()) == []


def test_upload_rejects_same_content_as_duplicate(client, document_storage):
    first = client.post("/rag/uploads", files=[("files", ("a.txt", "相同内容", "text/plain"))])
    second = client.post("/rag/uploads", files=[("files", ("b.txt", "相同内容", "text/plain"))])

    assert len(first.json()["data"]["uploaded"]) == 1
    assert second.json()["data"]["uploaded"] == []
    assert "文件内容重复" in second.json()["data"]["failed"][0]["error"]


def test_list_filter_and_delete_pending_document(client, document_storage):
    created = client.post("/rag/uploads", files=[("files", ("待删除.txt", "删除我", "text/plain"))])
    document = created.json()["data"]["uploaded"][0]

    listed = client.get("/rag/uploads", params={"status": "pending"})
    deleted = client.delete(f"/rag/uploads/{document['id']}")

    assert listed.status_code == 200
    assert listed.json()["data"][0]["id"] == document["id"]
    assert deleted.json()["data"]["status"] == DocumentStatus.DELETED
    assert not (document_storage["uploads"] / document["stored_name"]).exists()


def test_batch_delete_reports_each_document_result(client, document_storage):
    first = client.post("/rag/uploads", files=[("files", ("a.txt", "A", "text/plain"))]).json()["data"]["uploaded"][0]
    second = client.post("/rag/uploads", files=[("files", ("b.txt", "B", "text/plain"))]).json()["data"]["uploaded"][0]

    response = client.post("/rag/uploads/delete-batch", json={"document_ids": [first["id"], second["id"], 999]})

    assert {item["id"] for item in response.json()["data"]["deleted"]} == {first["id"], second["id"]}
    assert response.json()["data"]["failed"][0]["id"] == 999


def test_approve_moves_file_to_docs_and_marks_approved(client, document_storage, monkeypatch):
    created = client.post("/rag/uploads", files=[("files", ("审核.txt", "审核正文", "text/plain"))])
    document = created.json()["data"]["uploaded"][0]
    add_file = Mock(return_value=2)
    monkeypatch.setattr(rag_server, "rag_add_file", add_file)

    response = client.post(f"/rag/uploads/{document['id']}/approve")

    assert response.status_code == 200
    assert response.json()["data"] == {"id": document["id"], "status": DocumentStatus.APPROVED, "chunks": 2}
    assert not (document_storage["uploads"] / document["stored_name"]).exists()
    assert (document_storage["docs"] / document["stored_name"]).exists()
    add_file.assert_called_once()
    assert add_file.call_args.kwargs["metadata"]["document_id"] == document["id"]


def test_approve_failure_restores_file_and_marks_failed(client, db_session, document_storage, monkeypatch):
    created = client.post("/rag/uploads", files=[("files", ("失败.txt", "失败正文", "text/plain"))])
    document = created.json()["data"]["uploaded"][0]
    monkeypatch.setattr(rag_server, "rag_add_file", Mock(side_effect=RuntimeError("embedding failed")))
    monkeypatch.setattr(rag_server, "rag_delete_document_vectors", Mock())

    response = client.post(f"/rag/uploads/{document['id']}/approve")
    record = knowledge_document_crud.get_document_by_id(db_session, document["id"])

    assert response.status_code == 500
    assert "文件入库失败" in response.json()["detail"]
    assert record.status == DocumentStatus.FAILED
    assert "embedding failed" in record.error_message
    assert (document_storage["uploads"] / document["stored_name"]).exists()
    assert not (document_storage["docs"] / document["stored_name"]).exists()


def test_batch_approve_returns_success_and_failure(client, document_storage, monkeypatch):
    first = client.post("/rag/uploads", files=[("files", ("a.txt", "A", "text/plain"))]).json()["data"]["uploaded"][0]
    second = client.post("/rag/uploads", files=[("files", ("b.txt", "B", "text/plain"))]).json()["data"]["uploaded"][0]
    monkeypatch.setattr(rag_server, "rag_add_file", Mock(side_effect=[1, RuntimeError("broken")]))
    monkeypatch.setattr(rag_server, "rag_delete_document_vectors", Mock())

    response = client.post("/rag/uploads/approve-batch", json={"document_ids": [first["id"], second["id"]]})

    result = response.json()["data"]
    assert result["approved"] == [{"id": first["id"], "status": DocumentStatus.APPROVED, "chunks": 1}]
    assert result["failed"][0]["id"] == second["id"]
