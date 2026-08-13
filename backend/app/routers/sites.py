from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db

router = APIRouter()


@router.get("/sites", response_model=list[schemas.SiteRead])
def list_sites(db: Session = Depends(get_db)):
    return db.query(models.Site).order_by(models.Site.created_at.desc()).all()


@router.post("/sites", response_model=schemas.SiteRead, status_code=201)
def create_site(payload: schemas.SiteCreate, db: Session = Depends(get_db)):
    site = models.Site(**payload.model_dump())
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@router.delete("/sites/{site_id}", status_code=204)
def delete_site(site_id: int, db: Session = Depends(get_db)):
    site = db.get(models.Site, site_id)
    if site is None:
        raise HTTPException(status_code=404, detail="Site not found")
    db.delete(site)
    db.commit()


@router.get("/sites/{site_id}/assessments", response_model=list[schemas.AssessmentReport])
def list_site_assessments(site_id: int, db: Session = Depends(get_db)):
    site = db.get(models.Site, site_id)
    if site is None:
        raise HTTPException(status_code=404, detail="Site not found")
    return sorted(site.assessments, key=lambda a: a.created_at, reverse=True)
