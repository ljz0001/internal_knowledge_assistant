from sqlalchemy.orm import Session
from app.db.models.contact import Contact

def get_contact_by_name(db:Session,name:str):
    return db.query(Contact).filter(Contact.name == name).all()

def get_contact_by_id(db:Session,id:int):
    return db.query(Contact).filter(Contact.id == id).first()



def add_contact(db:Session,contact_info:dict):
    new_contact = Contact(**contact_info)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact

def update_contact(db:Session,id:int,update_data:dict):
    contact = get_contact_by_id(db,id)
    if not contact:
        return None
    for key,value in update_data.items():
        if hasattr(contact,key):
            setattr(contact,key,value)
    db.commit()
    db.refresh(contact)
    return contact

def delete_contact(db:Session,id:int):
    contact = get_contact_by_id(db,id)
    if not contact:
        return None
    db.delete(contact)
    db.commit()
    return True
