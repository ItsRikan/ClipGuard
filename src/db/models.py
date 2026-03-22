from .database import Base
from sqlalchemy import Column,Boolean,String,DateTime
from datetime import datetime


class Video(Base):
    __tablename__ = "videos"

    id = Column(String,primary_key=True)
    url = Column(String,nullable=False)
    ingested = Column(Boolean,default=False)
    created_at = Column(DateTime,default=datetime.utcnow)
    ingested_at = Column(DateTime,nullable=True)



