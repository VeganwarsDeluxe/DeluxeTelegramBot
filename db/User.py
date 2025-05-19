from sqlalchemy import Column, Integer, String, BIGINT

from db.startup import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(BIGINT, primary_key=True, index=True)
    name = Column(String, index=True)
    username = Column(String, index=True)
    tickets = Column(Integer, index=True, default=0)
    rating = Column(Integer, index=True, default=1000)

    locale = Column(String, index=True, default='uk')

    karma = Column(Integer, index=True, default=0)
