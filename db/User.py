from sqlalchemy import Column, Integer, String

from db.startup import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    tickets = Column(Integer, index=True, default=0)
    rating = Column(Integer, index=True, default=1000)

    locale = Column(String, index=True, default='uk')
