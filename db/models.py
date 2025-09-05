from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    direction_id = Column(Integer, ForeignKey("directions.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=lambda: datetime.utcnow())

    direction = relationship("Direction", back_populates="students")
    results = relationship("StudentResult", back_populates="student")


class Direction(Base):
    __tablename__ = "directions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    students = relationship("Student", back_populates="direction")
    tests = relationship("Test", back_populates="direction")
    videos = relationship("Video", back_populates="direction")


class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    direction_id = Column(Integer, ForeignKey("directions.id", ondelete="CASCADE"))

    direction = relationship("Direction", back_populates="tests")
    answers = relationship("TestAnswer", back_populates="test")


class TestAnswer(Base):
    __tablename__ = "test_answers"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(255), nullable=False)
    is_correct = Column(Boolean, default=False)

    test_id = Column(Integer, ForeignKey("tests.id", ondelete="CASCADE"))
    test = relationship("Test", back_populates="answers")


class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(String, nullable=False, unique=True)  

    results = relationship("StudentResult", back_populates="rating")
    videos = relationship("Video", back_populates="rating")


class StudentResult(Base):
    __tablename__ = "student_results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    rating_id = Column(Integer, ForeignKey("ratings.id", ondelete="CASCADE"))

    student = relationship("Student", back_populates="results")
    rating = relationship("Rating", back_populates="results")


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)

    direction_id = Column(Integer, ForeignKey("directions.id", ondelete="CASCADE"))
    rating_id = Column(Integer, ForeignKey("ratings.id", ondelete="CASCADE"))

    direction = relationship("Direction", back_populates="videos")
    rating = relationship("Rating", back_populates="videos")
    questions = relationship("VideoQuestion", back_populates="video")


class VideoQuestion(Base):
    __tablename__ = "video_questions"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"))
    question = Column(Text, nullable=False)

    video = relationship("Video", back_populates="questions")
    question_answers = relationship("VideoQuestionAnswer", back_populates="video_question")


class VideoQuestionAnswer(Base):
    __tablename__ = "video_question_answers"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String(255), nullable=False)
    is_correct = Column(Boolean, default=False)

    video_question_id = Column(Integer, ForeignKey("video_questions.id", ondelete="CASCADE"))
    video_question = relationship("VideoQuestion", back_populates="question_answers")