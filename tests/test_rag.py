from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app.api.routers import rag


def test_search_returns_answer(monkeypatch):
    search = Mock(return_value="差旅报销需要提供发票。")
    monkeypatch.setattr(rag, "rag_search", search)

    response = rag.search(rag.RagSearchRequest(query="差旅如何报销？"))

    assert response.data == {"answer": "差旅报销需要提供发票。"}
    search.assert_called_once_with("差旅如何报销？")


def test_search_wraps_service_error(monkeypatch):
    monkeypatch.setattr(rag, "rag_search", Mock(side_effect=RuntimeError("vector store down")))

    with pytest.raises(HTTPException) as error:
        rag.search(rag.RagSearchRequest(query="测试"))

    assert error.value.status_code == 500
    assert "知识库检索失败" in error.value.detail


def test_add_file_returns_path_after_success(monkeypatch):
    add_file = Mock()
    monkeypatch.setattr(rag, "rag_add_file", add_file)

    response = rag.add_file(rag.RagFileResponse(file_path="uploads/policy.txt"))

    assert response.data == {"file_path": "uploads/policy.txt"}
    add_file.assert_called_once_with("uploads/policy.txt")


def test_add_file_reports_unsupported_file_as_bad_request(monkeypatch):
    monkeypatch.setattr(rag, "rag_add_file", Mock(side_effect=ValueError("不支持的文件格式：.docx")))

    with pytest.raises(HTTPException) as error:
        rag.add_file(rag.RagFileResponse(file_path="uploads/policy.docx"))

    assert error.value.status_code == 400
    assert ".docx" in error.value.detail


def test_add_files_rejects_empty_list():
    with pytest.raises(HTTPException) as error:
        rag.add_files(rag.RagFilesResponse(file_paths=[]))

    assert error.value.status_code == 400


def test_add_files_returns_batch_result(monkeypatch):
    result = {"success": [{"path": "a.txt"}], "failed": [{"path": "b.pdf", "error": "parse failed"}]}
    add_files = Mock(return_value=result)
    monkeypatch.setattr(rag, "rag_add_files", add_files)

    response = rag.add_files(rag.RagFilesResponse(file_paths=["a.txt", "b.pdf"]))

    assert response.data == result
    add_files.assert_called_once_with(["a.txt", "b.pdf"])


def test_delete_file_returns_deleted_path(monkeypatch):
    delete_file = Mock()
    monkeypatch.setattr(rag, "rag_delete_file", delete_file)

    response = rag.delete_file(rag.RagDeleteRequest(file_path="uploads/old.txt"))

    assert response.data == {"file_path": "uploads/old.txt", "deleted": True}
    delete_file.assert_called_once_with("uploads/old.txt")


def test_stats_returns_vector_count_and_sorted_sources(monkeypatch):
    collection = Mock()
    collection.count.return_value = 3
    collection.get.return_value = {
        "metadatas": [
            {"source": "z.txt"},
            {"source": "a.txt"},
            {"source": "z.txt"},
            None,
        ]
    }
    monkeypatch.setattr(rag, "get_vector_store", lambda: SimpleStore(collection))

    response = rag.stats()

    assert response.data == {"vector_count": 3, "files": ["a.txt", "z.txt"]}


class SimpleStore:
    def __init__(self, collection):
        self._collection = collection
