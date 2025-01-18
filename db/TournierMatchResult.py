from sqlalchemy import Column, Integer, Date

from db.startup import Base


class TournierMatchResult(Base):
    __tablename__ = "results"

    opponent_a_id = Column(Integer, index=True)
    opponent_b_id = Column(Integer, index=True)

    opponent_a_score = Column(Integer, index=True)
    opponent_b_score = Column(Integer, index=True)

    date = Column(Date, primary_key=True, index=True)
