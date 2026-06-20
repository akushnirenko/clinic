from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from ..database import get_db
from ..models import Patient, User
from ..schemas import PatientResponse, PatientCreate
from ..oauth2 import get_current_user

router = APIRouter(prefix="/api/v1/patients", tags=["Patients"])

@router.get("/", response_model=List[PatientResponse])
def get_my_children(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetches all patient profiles linked specifically
    to the currently authenticated parent account.
    """
    stmt = select(Patient).where(Patient.user_id == current_user.id)
    patients = db.scalars(stmt).all()
    return patients

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PatientResponse)
def add_child(
    patient_data: PatientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Allows an authenticated parent to add a new child profile
    to their dashboard.
    """
    # Verify unique constraint edge case if SNILS is provided
    if patient_data.snils:
        existing = db.query(Patient).filter(Patient.snils == patient_data.snils).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="A child with this SNILS identifier is already registered"
            )

    new_patient = Patient(
        user_id=current_user.id,
        first_name=patient_data.first_name,
        last_name=patient_data.last_name,
        birth_date=patient_data.birth_date,
        snils=patient_data.snils
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    return new_patient
