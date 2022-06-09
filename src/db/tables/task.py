from sqlalchemy import Column, String

from src.db.base_class import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
