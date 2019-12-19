from sqlalchemy import (Table, Column, ForeignKey, String, Integer)
from sqlalchemy.orm import relationships
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Subcategory(Base):
    __tablename__ = 'Subcategories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String, unique=True)
    name = Column(String)
    __category = Column(Integer, ForeignKey('Category.id'))
    category = relationships('Category', backref='Subcategories')

    def __init__(self, code: str, name: str, category):
        self.code = code
        self.name = name
        self.category = category
