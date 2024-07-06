from uuid import uuid4

from db import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID


class User(Base):
    __tablename__ = "user"
    userId = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid4,
        unique=True,
    )
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    phone = Column(String(50))


    def to_dict(self):
        obj_dict = self.__dict__
        if '_sa_instance_state' in obj_dict:
            del obj_dict['_sa_instance_state']
        del obj_dict['password']
        obj_dict['userId']= str(self.userId)
        
        return {key: value for key, value in obj_dict.items()}
class Organization(Base):
    __tablename__ = "organization"
    orgId = Column(
        String, nullable=False, primary_key=True, default=uuid4(), unique=True
    )
    name = ""
    description = ""
