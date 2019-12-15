from sqlalchemy import (Table, Column, ForeignKey, String, Integer)
from sqlalchemy.orm import relationships
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Subcategory(Base):
    __tablename__ = 'Subategories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    Code = Column(String, unique=True)
    Name = Column(String)

    def __init__(self, code: str, name: str):
        self.Code = code
        self.Name = name
