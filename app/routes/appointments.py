from datetime import date, time, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from ..database import get_db
from ..models import Appointment, Doctor, DoctorSchedule, User, AppointmentStatus
from ..schemas import AppointmentResponse, AppointmentCreate
from ..oauth2 import get_current_user

router = APIRouter(prefix="/api/v1/appointments", tags=["Appointments"])

@router.get("/available-slots", response_model=List[str])
def get_available_slots(doctor_id: int, date_str: str, db: Session = Depends(get_db)):
    """
    Рассчитывает свободные временные слоты врача на выбранную дату,
    исключая уже занятые записи из базы данных.
    """
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Неверный формат даты. Используйте ГГГГ-ММ-ДД")

    # 1. Находим день недели (Python: 1=Пн, 7=Вс. Наша БД совпадает с этим стандартом)
    day_of_week = target_date.isoweekday()

    # 2. Ищем шаблон графика работы этого врача на этот день недели
    schedule = db.scalars(
        select(DoctorSchedule).where(
            DoctorSchedule.doctor_id == doctor_id,
            DoctorSchedule.day_of_week == day_of_week
        )
    ).first()

    if not schedule:
        return []  # Врач не принимает в этот день

    # 3. Генерируем полную сетку времени на смену с шагом в slot_duration минут
    all_slots = []
    current_time = datetime.combine(target_date, schedule.start_time)
    end_time = datetime.combine(target_date, schedule.end_time)

    while current_time < end_time:
        all_slots.append(current_time.time().strftime("%H:%M:%S"))
        current_time += timedelta(minutes=schedule.slot_duration)

    # 4. Вытаскиваем из базы уже занятые активные записи к этому врачу на этот день
    booked_appointments = db.scalars(
        select(Appointment.appointment_time).where(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == target_date,
            Appointment.status == AppointmentStatus.scheduled
        )
    ).all()

    booked_slots = {appt.strftime("%H:%M:%S") for appt in booked_appointments}

    # 5. Исключаем занятые часы из общего списка
    available_slots = [slot for slot in all_slots if slot not in booked_slots]
    return available_slots


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AppointmentResponse)
def create_appointment(
    appointment_data: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Создает новую запись на прием.
    """
    # 1. Проверяем, не занял ли кто-то этот слот прямо сейчас
    existing_booking = db.scalars(
        select(Appointment).where(
            Appointment.doctor_id == appointment_data.doctor_id,
            Appointment.appointment_date == appointment_data.appointment_date,
            Appointment.appointment_time == appointment_data.appointment_time,
            Appointment.status == AppointmentStatus.scheduled
        )
    ).first()

    if existing_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Извините, это время только что было забронировано другим пользователем."
        )

    try:
        new_appointment = Appointment(
            patient_id=appointment_data.patient_id,
            doctor_id=appointment_data.doctor_id,
            appointment_date=appointment_data.appointment_date,
            appointment_time=appointment_data.appointment_time,
            status=AppointmentStatus.scheduled
        )
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)
        return new_appointment

    except Exception:
        db.rollback()
        # Срабатывает, если два человека одновременно нажали кнопку (защита на уровне UNIQUE-индекса БД)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Конфликт планирования. Выбранный слот уже занят."
        )
