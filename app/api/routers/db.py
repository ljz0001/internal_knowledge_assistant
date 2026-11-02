from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.schemas import (
    ApiResponse,
    AttendanceCreate,
    AttendanceUpdate,
    ContactCreate,
    ContactUpdate,
    EmployeeCreate,
    EmployeeUpdate,
    LeaveCreate,
    LeaveUpdate,
)
from app.db.crud import att_crud, contact_crud, emp_crud, leave_crud

router = APIRouter(prefix="/db", tags=["业务数据管理"])


def _dump(value: Any) -> Any:
    if isinstance(value, list):
        return [_dump(item) for item in value]
    if hasattr(value, "__table__"):
        return {column.name: getattr(value, column.name) for column in value.__table__.columns}
    return value


def _created(call):
    try:
        return call()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"数据库写入失败：{exc}") from exc


def _not_found(value, resource: str):
    if value is None:
        raise HTTPException(status_code=404, detail=f"未找到{resource}")
    return value


@router.get("/employees", response_model=ApiResponse, summary="分页查询员工")
def list_employees(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    return ApiResponse(data=_dump(emp_crud.get_employee_list(db, skip, limit)))


@router.get("/employees/{emp_id}", response_model=ApiResponse, summary="查询员工")
def get_employee(emp_id: int, db: Session = Depends(get_db)):
    return ApiResponse(data=_dump(_not_found(emp_crud.get_employee_by_id(db, emp_id), "员工")))


@router.post("/employees", response_model=ApiResponse, summary="新增员工", status_code=201)
def create_employee(request: EmployeeCreate, db: Session = Depends(get_db)):
    return ApiResponse(data=_dump(_created(lambda: emp_crud.add_employee(db, request.model_dump(exclude_unset=True)))))


@router.patch("/employees/{emp_id}", response_model=ApiResponse, summary="更新员工")
def update_employee(emp_id: int, request: EmployeeUpdate, db: Session = Depends(get_db)):
    changes = request.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="至少提供一个需要更新的字段")
    result = _created(lambda: emp_crud.update_employee(db, emp_id, changes))
    return ApiResponse(data=_dump(_not_found(result, "员工")))


@router.delete("/employees/{emp_id}", response_model=ApiResponse, summary="删除员工")
def delete_employee(emp_id: int, db: Session = Depends(get_db)):
    result = _created(lambda: emp_crud.delete_employee(db, emp_id))
    _not_found(result, "员工")
    return ApiResponse(data={"deleted": True})


@router.get("/attendance", response_model=ApiResponse, summary="查询考勤记录")
def list_attendance(emp_id: int | None = None, attend_date: date | None = None, db: Session = Depends(get_db)):
    if emp_id is not None:
        records = att_crud.get_attendance_by_emp_id(db, emp_id)
    elif attend_date is not None:
        records = att_crud.get_attendance_by_date(db, attend_date)
    else:
        raise HTTPException(status_code=400, detail="请提供emp_id或attend_date")
    return ApiResponse(data=_dump(records))


@router.post("/attendance", response_model=ApiResponse, summary="新增考勤记录", status_code=201)
def create_attendance(request: AttendanceCreate, db: Session = Depends(get_db)):
    return ApiResponse(data=_dump(_created(lambda: att_crud.add_attendance(db, request.model_dump()))))


@router.patch("/attendance/{attendance_id}", response_model=ApiResponse, summary="更新考勤记录")
def update_attendance(attendance_id: int, request: AttendanceUpdate, db: Session = Depends(get_db)):
    changes = request.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="至少提供一个需要更新的字段")
    result = _created(lambda: att_crud.update_attendance(db, attendance_id, changes))
    return ApiResponse(data=_dump(_not_found(result, "考勤记录")))


@router.get("/leaves", response_model=ApiResponse, summary="查询请假记录")
def list_leaves(emp_id: int | None = None, start_date: date | None = None, db: Session = Depends(get_db)):
    if emp_id is not None:
        records = leave_crud.get_leave_by_id(db, emp_id)
    elif start_date is not None:
        records = leave_crud.get_leave_by_start_date(db, start_date)
    else:
        raise HTTPException(status_code=400, detail="请提供emp_id或start_date")
    return ApiResponse(data=_dump(records))


@router.post("/leaves", response_model=ApiResponse, summary="创建请假申请", status_code=201)
def create_leave(request: LeaveCreate, db: Session = Depends(get_db)):
    if request.end_date < request.start_date:
        raise HTTPException(status_code=400, detail="end_date不能早于start_date")
    return ApiResponse(data=_dump(_created(lambda: leave_crud.add_leave(db, request.model_dump()))))


@router.patch("/leaves/{leave_id}", response_model=ApiResponse, summary="更新请假申请")
def update_leave(leave_id: int, request: LeaveUpdate, db: Session = Depends(get_db)):
    changes = request.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="至少提供一个需要更新的字段")
    result = _created(lambda: leave_crud.update_leave(db, leave_id, changes))
    return ApiResponse(data=_dump(_not_found(result, "请假申请")))


@router.get("/contacts", response_model=ApiResponse, summary="按姓名查询联系人")
def list_contacts(name: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    return ApiResponse(data=_dump(contact_crud.get_contact_by_name(db, name)))


@router.get("/contacts/{contact_id}", response_model=ApiResponse, summary="查询联系人")
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    return ApiResponse(data=_dump(_not_found(contact_crud.get_contact_by_id(db, contact_id), "联系人")))


@router.post("/contacts", response_model=ApiResponse, summary="新增联系人", status_code=201)
def create_contact(request: ContactCreate, db: Session = Depends(get_db)):
    return ApiResponse(data=_dump(_created(lambda: contact_crud.add_contact(db, request.model_dump()))))


@router.patch("/contacts/{contact_id}", response_model=ApiResponse, summary="更新联系人")
def update_contact(contact_id: int, request: ContactUpdate, db: Session = Depends(get_db)):
    changes = request.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="至少提供一个需要更新的字段")
    result = _created(lambda: contact_crud.update_contact(db, contact_id, changes))
    return ApiResponse(data=_dump(_not_found(result, "联系人")))


@router.delete("/contacts/{contact_id}", response_model=ApiResponse, summary="删除联系人")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    result = _created(lambda: contact_crud.delete_contact(db, contact_id))
    _not_found(result, "联系人")
    return ApiResponse(data={"deleted": True})
