from typing import Generator

from src.db.base_class import Base
from src.db.session import Session, engine


def get_session() -> Generator:
    """yield Session instance in context manager for provide closing connection"""
    with Session() as session:
        yield session
        session.commit()


def init_db() -> None:
    """
    Initialize database
    """
    Base.metadata.create_all(engine)
