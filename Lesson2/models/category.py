from sqlalchemy import (Table, Column, ForeignKey, String, Integer)
from sqlalchemy.orm import relationships
from common import Base


class Category(Base):
    __tablename__ = 'Categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True)
    name = Column(String)

    def __init__(self, code: str, name: str):
        self.code = code
        self.name = name
