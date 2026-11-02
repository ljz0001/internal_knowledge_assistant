from sqlalchemy.orm import Session
from app.db.models.leave import Leave
from datetime import date

def get_leave_by_id(db:Session,emp_id:int):
    return db.query(Leave).filter(Leave.emp_id == emp_id).all()

def get_leave_by_record_id(db: Session, leave_id: int):
    return db.query(Leave).filter(Leave.id == leave_id).first()

def get_leave_by_start_date(db:Session,start_date:date):
    return db.query(Leave).filter(Leave.start_date == start_date).all()

def add_leave(db:Session,leave_info:dict):
    new_leave = Leave(**leave_info)
    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)
    return new_leave

def update_leave(db:Session,leave_id:int,update_data:dict):
    leave = get_leave_by_record_id(db,leave_id)
    if not leave:
        return None
    for key,value in update_data.items():
        setattr(leave,key,value)
    db.commit()
    db.refresh(leave)
    return leave
