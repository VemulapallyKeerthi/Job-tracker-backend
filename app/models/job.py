from sqlalchemy import Column, Integer, String, Date
from app.database import Base

class Job(Base):
    __tablename__ = "jobs"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String, nullable=False)
    company     = Column(String, nullable=False)
    location    = Column(String)
    posted_date = Column(Date)
    description = Column(String)
    apply_link  = Column(String)          # nullable — scrapers may not always get a direct link
    source      = Column(String)          # e.g. "indeed", "linkedin", "dice"
    status      = Column(String, default="saved")