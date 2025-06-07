from sqlalchemy import Column, DateTime, Integer, Boolean, String
from services.database import Base


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, index=True)
    tutor_id = Column(Integer)
    start_time = Column(DateTime, nullable=False)
    duration = Column(Integer, default=60)
    topic = Column(String(255))
    is_completed = Column(Boolean, default=False)