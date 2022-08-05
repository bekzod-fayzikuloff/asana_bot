from src.db.base_class import Base
from src.db.session import engine


def init_db() -> None:
    """
    Initialize database
    """
    Base.metadata.create_all(engine)
