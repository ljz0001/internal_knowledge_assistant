from datetime import date, time

from app.db.crud import att_crud, emp_crud, leave_crud
from app.db.models.attendance import Attendance
from app.db.models.employee import Employee
from app.db.models.leave import Leave


def test_employee_crud_functions(db_session):
    employee = emp_crud.add_employee(
        db_session,
        {"emp_name": "CRUD员工", "emp_no": "CRUD-001", "department": "研发部"},
    )
    assert emp_crud.get_employee_by_id(db_session, employee.id).emp_no == "CRUD-001"

    updated = emp_crud.update_employee(db_session, employee.id, {"department": "平台部"})
    assert updated.department == "平台部"

    assert emp_crud.delete_employee(db_session, employee.id) is True
    assert emp_crud.get_employee_by_id(db_session, employee.id) is None


def test_attendance_update_targets_one_record_id(db_session):
    first = Attendance(
        emp_id=7,
        attend_date=date(2026, 11, 1),
        check_in=time(9, 0),
        check_out=time(18, 0),
        status="正常",
    )
    second = Attendance(
        emp_id=7,
        attend_date=date(2026, 11, 2),
        check_in=time(9, 5),
        check_out=time(18, 0),
        status="迟到",
    )
    db_session.add_all([first, second])
    db_session.commit()

    updated = att_crud.update_attendance(db_session, second.id, {"status": "已修正"})

    assert updated.id == second.id
    assert att_crud.get_attendance_by_id(db_session, first.id).status == "正常"
    assert att_crud.get_attendance_by_id(db_session, second.id).status == "已修正"


def test_leave_update_targets_one_record_id(db_session):
    first = Leave(
        emp_id=9,
        leave_type="年假",
        start_date=date(2026, 11, 1),
        end_date=date(2026, 11, 1),
        reason="第一条",
        audit_status="待审核",
    )
    second = Leave(
        emp_id=9,
        leave_type="事假",
        start_date=date(2026, 11, 2),
        end_date=date(2026, 11, 2),
        reason="第二条",
        audit_status="待审核",
    )
    db_session.add_all([first, second])
    db_session.commit()

    updated = leave_crud.update_leave(db_session, second.id, {"audit_status": "通过"})

    assert updated.id == second.id
    assert leave_crud.get_leave_by_record_id(db_session, first.id).audit_status == "待审核"
    assert leave_crud.get_leave_by_record_id(db_session, second.id).audit_status == "通过"


def test_create_and_read_employee(client):
    create_response = client.post(
        "/db/employees",
        json={
            "emp_name": "测试员工",
            "emp_no": "TEST-001",
            "department": "测试部",
            "phone": "13800000000",
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()["data"]
    assert created["emp_no"] == "TEST-001"

    read_response = client.get(f"/db/employees/{created['id']}")

    assert read_response.status_code == 200
    assert read_response.json()["data"]["emp_name"] == "测试员工"


def test_update_employee_changes_only_provided_fields(client):
    create_response = client.post(
        "/db/employees",
        json={"emp_name": "原姓名", "emp_no": "TEST-002", "department": "研发部", "phone": "123"},
    )
    employee_id = create_response.json()["data"]["id"]

    update_response = client.patch(f"/db/employees/{employee_id}", json={"phone": "456"})

    assert update_response.status_code == 200
    assert update_response.json()["data"]["phone"] == "456"
    assert update_response.json()["data"]["emp_name"] == "原姓名"


def test_update_employee_rejects_empty_payload(client):
    response = client.patch("/db/employees/1", json={})

    assert response.status_code == 400
    assert "至少提供一个" in response.json()["detail"]


def test_read_missing_employee_returns_404(client):
    response = client.get("/db/employees/999")

    assert response.status_code == 404


def test_delete_employee_route(client):
    created = client.post(
        "/db/employees",
        json={"emp_name": "待删除员工", "emp_no": "DELETE-001", "department": "测试部"},
    ).json()["data"]

    response = client.delete(f"/db/employees/{created['id']}")

    assert response.status_code == 200
    assert response.json()["data"] == {"deleted": True}
    assert client.get(f"/db/employees/{created['id']}").status_code == 404


def test_list_employees_obeys_pagination(client, db_session):
    db_session.add_all(
        [
            Employee(emp_name="员工甲", emp_no="PAGE-001", department="测试部"),
            Employee(emp_name="员工乙", emp_no="PAGE-002", department="测试部"),
        ]
    )
    db_session.commit()

    response = client.get("/db/employees", params={"skip": 1, "limit": 1})

    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert response.json()["data"][0]["emp_no"] == "PAGE-002"


def test_leave_rejects_end_date_before_start_date(client):
    response = client.post(
        "/db/leaves",
        json={
            "emp_id": 1,
            "leave_type": "年假",
            "start_date": "2026-11-10",
            "end_date": "2026-11-09",
            "reason": "测试",
        },
    )

    assert response.status_code == 400
    assert "end_date不能早于start_date" in response.json()["detail"]


def test_attendance_requires_employee_or_date_filter(client):
    response = client.get("/db/attendance")

    assert response.status_code == 400
    assert "emp_id或attend_date" in response.json()["detail"]


def test_attendance_validates_date_format(client):
    response = client.get("/db/attendance", params={"attend_date": "not-a-date"})

    assert response.status_code == 422


def test_attendance_create_query_and_update_routes(client):
    created = client.post(
        "/db/attendance",
        json={
            "emp_id": 22,
            "attend_date": "2026-11-02",
            "check_in": "09:00:00",
            "check_out": "18:00:00",
        },
    )

    assert created.status_code == 201
    attendance = created.json()["data"]
    assert attendance["attend_date"] == "2026-11-02"

    listed = client.get("/db/attendance", params={"emp_id": 22})
    updated = client.patch(f"/db/attendance/{attendance['id']}", json={"status": "迟到"})

    assert len(listed.json()["data"]) == 1
    assert updated.status_code == 200
    assert updated.json()["data"]["status"] == "迟到"


def test_leave_create_list_and_update_routes(client):
    created = client.post(
        "/db/leaves",
        json={
            "emp_id": 23,
            "leave_type": "年假",
            "start_date": "2026-11-10",
            "end_date": "2026-11-11",
            "reason": "测试申请",
        },
    )

    assert created.status_code == 201
    leave = created.json()["data"]
    assert leave["start_date"] == "2026-11-10"

    listed = client.get("/db/leaves", params={"emp_id": 23})
    updated = client.patch(f"/db/leaves/{leave['id']}", json={"audit_status": "通过"})

    assert len(listed.json()["data"]) == 1
    assert updated.status_code == 200
    assert updated.json()["data"]["audit_status"] == "通过"


def test_contact_create_search_update_and_delete_routes(client):
    created = client.post(
        "/db/contacts",
        json={"name": "测试联系人", "phone": "13900000000", "department": "测试部"},
    )

    assert created.status_code == 201
    contact = created.json()["data"]
    searched = client.get("/db/contacts", params={"name": "测试联系人"})
    updated = client.patch(f"/db/contacts/{contact['id']}", json={"remark": "已核验"})
    deleted = client.delete(f"/db/contacts/{contact['id']}")

    assert searched.status_code == 200
    assert searched.json()["data"][0]["phone"] == "13900000000"
    assert updated.json()["data"]["remark"] == "已核验"
    assert deleted.json()["data"] == {"deleted": True}
