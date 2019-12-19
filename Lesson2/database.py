from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models.category import Category
import common
# from models.subcategory import Subcategory

Base = declarative_base()

class MarketDB:
    def __init__(self, base, db_url):
        engine = create_engine(db_url)
        base.metadata.create_all(engine)
        session_db = sessionmaker(bind=engine)
        self.__session = session_db()

    @property
    def session(self):
        return self.__session


if __name__ == '__main__':
    db_url = 'sqlite:///marketplace.sqlite'
    db = MarketDB(Base, db_url)