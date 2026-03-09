from enum import Enum
from pydantic import BaseModel, Field
from datetime import date

class JobStatus(str, Enum):
    saved      = "saved"
    applied    = "applied"
    interview  = "interview"
    offer      = "offer"
    rejected   = "rejected"

class JobBase(BaseModel):
    title       : str
    company     : str
    location    : str | None        = None
    posted_date : date | None       = None
    description : str | None        = None
    apply_link  : str | None        = None   # optional — scrapers use 'url' alias below
    url         : str | None        = Field(default=None, exclude=True)  # scraper-friendly alias
    source      : str | None        = None   # e.g. "indeed", "linkedin"
    status      : JobStatus         = JobStatus.saved

    def model_post_init(self, __context):
        # If scraper sends 'url' instead of 'apply_link', map it over
        if self.url and not self.apply_link:
            self.apply_link = self.url

class JobResponse(BaseModel):
    id          : int
    title       : str
    company     : str
    location    : str | None        = None
    posted_date : date | None       = None
    description : str | None        = None
    apply_link  : str | None        = None
    source      : str | None        = None
    status      : str

    class Config:
        from_attributes = True
