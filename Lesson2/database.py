from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.category import Base
from models.category import Category


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
    db_url = 'mysql:///localhost.mysql'
    db = MarketDB(Base, db_url)
    print(1)
