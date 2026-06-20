from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from ..database import get_db
from ..models import Appointment, MedicalRecord, Patient, AppointmentStatus, Doctor
from ..schemas import MedicalRecordResponse, MedicalRecordCreate, AppointmentResponse

router = APIRouter(prefix="/api/v1/doctors", tags=["Doctor Panel"])

@router.get("/all")
def get_all_doctors(db: Session = Depends(get_db)):
    """
    Возвращает список всех врачей клиники с их специальностями.
    """
    stmt = select(Doctor)
    doctors = db.scalars(stmt).all()

    result = []
    for doc in doctors:
        result.append({
            "id": doc.id,
            "full_name": f"{doc.first_name} {doc.last_name}",
            "room": doc.room_number,
            "specialty": doc.specialty.name
        })
    return result


@router.get("/journal", response_model=List[AppointmentResponse])
def get_doctor_journal(doctor_id: int, date_str: str, db: Session = Depends(get_db)):
    """
    JOURNAL OF ENTRIES: Fetches all scheduled or completed appointments
    for a specific doctor on a chosen date (used for the doctor's calendar view).
    """
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    stmt = (
        select(Appointment)
        .where(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == target_date
        )
        .order_by(Appointment.appointment_time)
    )
    return db.scalars(stmt).all()


@router.post("/consultation", status_code=status.HTTP_201_CREATED, response_model=MedicalRecordResponse)
def complete_consultation(record_data: MedicalRecordCreate, db: Session = Depends(get_db)):
    """
    PATIENT INTAKE PAGE: Saves an entry into the child's medical record.
    If linked to an online appointment, it automatically updates its status to 'completed'.
    """
    # 1. Update appointment status if it exists
    if record_data.appointment_id:
        appointment = db.get(Appointment, record_data.appointment_id)
        if appointment:
            appointment.status = AppointmentStatus.completed

    # 2. Create the EMR record row
    new_record = MedicalRecord(
        patient_id=record_data.patient_id,
        doctor_id=record_data.doctor_id,
        appointment_id=record_data.appointment_id,
        visit_date=record_data.visit_date,
        complaints=record_data.complaints,
        diagnosis=record_data.diagnosis,
        treatment_plan=record_data.treatment_plan
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record


@router.post("/walk-in", status_code=status.HTTP_201_CREATED, response_model=AppointmentResponse)
def create_walk_in(patient_id: int, doctor_id: int, db: Session = Depends(get_db)):
    """
    LIVE QUEUE / WALK-IN: Instantly creates a placeholder appointment
    for a patient standing in line, setting it straight to 'scheduled' at the current moment.
    """
    now = datetime.now()

    new_walk_in = Appointment(
        patient_id=patient_id,
        doctor_id=doctor_id,
        appointment_date=now.date(),
        appointment_time=now.time(),
        status=AppointmentStatus.scheduled
    )

    db.add(new_walk_in)
    db.commit()
    db.refresh(new_walk_in)
    return new_walk_in
