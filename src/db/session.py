from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src import config

engine = create_engine(config.POSTGRES_URL)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
