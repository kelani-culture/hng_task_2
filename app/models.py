from uuid import uuid4

from db import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


association_table = Table(
    "association",
    Base.metadata,
    Column('user_id', ForeignKey('user.userId')),
    Column('org_id', ForeignKey('organization.orgId'))
)

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

    organizations = relationship('Organization', secondary=association_table, back_populates='users')

    def to_dict(self):
        obj_dict = self.__dict__
        if '_sa_instance_state' in obj_dict:
            del obj_dict['_sa_instance_state']
        del obj_dict['password']
        obj_dict['userId']= str(self.userId)
        
        return {key: value for key, value in obj_dict.items()}

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Organization(Base):
    __tablename__ = "organization"
    orgId = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid4,
        unique=True,
    )
    name = Column(String(50), nullable=False)
    description = Column(String(500), nullable=True)
    users = relationship("User", secondary=association_table, back_populates='organizations')

    def to_dict(self):
        obj_dict = self.__dict__
        if '_sa_instance_state' in obj_dict:
            del obj_dict['_sa_instance_state']

        obj_dict['orgId'] = str(self.orgId)
        return obj_dict
    def __str__(self):
        return self.name
