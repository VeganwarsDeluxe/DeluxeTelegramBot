from sqlalchemy import Column, String, BIGINT, NUMERIC

from db.startup import Base


class Chat(Base):
    __tablename__ = "chats"

    id = Column(BIGINT, primary_key=True, index=True)
    name = Column(String, index=True)
    last_message = Column(NUMERIC, index=True, default=0)
