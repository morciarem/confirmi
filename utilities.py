# add to the object to the db session and commit the changes
from sqlmodel import Session


def add_to_db(obj, db: Session):
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj