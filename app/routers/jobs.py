from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.job import Job
from app.schemas.job import JobBase, JobResponse, JobStatus

router = APIRouter(prefix="/jobs", tags=["Jobs"])

# ── DB dependency ─────────────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── GET /jobs ─────────────────────────────────────────────────────────────────
@router.get("/", response_model=list[JobResponse])
def get_jobs(
    status   : str | None = None,
    company  : str | None = None,
    location : str | None = None,
    title    : str | None = None,
    source   : str | None = None,
    db       : Session = Depends(get_db),
):
    query = db.query(Job)

    if status:
        query = query.filter(Job.status == status)
    if company:
        query = query.filter(Job.company.ilike(f"%{company}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if title:
        query = query.filter(Job.title.ilike(f"%{title}%"))   # ← was f"%title%" (bug)
    if source:
        query = query.filter(Job.source == source)

    return query.all()


# ── GET /jobs/{job_id} ────────────────────────────────────────────────────────
@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# ── POST /jobs ────────────────────────────────────────────────────────────────
@router.post("/", response_model=JobResponse)
def create_job(job: JobBase, db: Session = Depends(get_db)):
    data = job.model_dump(exclude={"url"})          # exclude alias field, use apply_link
    new_job = Job(**data)
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job


# ── PUT /jobs/{job_id} ────────────────────────────────────────────────────────
@router.put("/{job_id}", response_model=JobResponse)
def update_job(job_id: int, updated_job: JobBase, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    for key, value in updated_job.model_dump(exclude={"url"}).items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)
    return job


# ── DELETE /jobs/{job_id} ─────────────────────────────────────────────────────
@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully"}


# ── PATCH /jobs/{job_id}/status ───────────────────────────────────────────────
@router.patch("/{job_id}/status", response_model=JobResponse)
def update_job_status(job_id: int, status: JobStatus, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.status = status
    db.commit()
    db.refresh(job)
    return job


# ── Status transition helpers ─────────────────────────────────────────────────
def _transition(job_id: int, new_status: JobStatus, db: Session):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job.status = new_status
    db.commit()
    db.refresh(job)
    return job

@router.post("/{job_id}/apply", response_model=JobResponse)
def mark_as_applied(job_id: int, db: Session = Depends(get_db)):
    return _transition(job_id, JobStatus.applied, db)

@router.post("/{job_id}/interview", response_model=JobResponse)
def mark_as_interviewing(job_id: int, db: Session = Depends(get_db)):
    return _transition(job_id, JobStatus.interview, db)

@router.post("/{job_id}/offer", response_model=JobResponse)
def mark_as_offer(job_id: int, db: Session = Depends(get_db)):
    return _transition(job_id, JobStatus.offer, db)

@router.post("/{job_id}/reject", response_model=JobResponse)
def mark_as_rejected(job_id: int, db: Session = Depends(get_db)):
    return _transition(job_id, JobStatus.rejected, db)
