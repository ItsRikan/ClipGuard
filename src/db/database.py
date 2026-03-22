from sqlalchemy.orm import declarative_base,sessionmaker
from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///./videos.db"

Base = declarative_base()
engine = create_engine(DATABASE_URL,connect_args={"check_same_thread":False})
SessionLocal = sessionmaker(engine,autoflush=False,autocommit=False)





