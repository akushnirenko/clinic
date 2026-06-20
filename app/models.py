import enum
from datetime import date, time
from typing import List, Optional
from sqlalchemy import ForeignKey, Integer, String, Text, Date, Time, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Base class for all modern SQLAlchemy 2.0 models
class Base(DeclarativeBase):
    pass

# ============================================================================
# ENUMS (PostgreSQL Custom Types mapping)
# ============================================================================
class AppointmentStatus(str, enum.Enum):
    scheduled = "scheduled"
    completed = "completed"
    canceled = "canceled"

# ============================================================================
# 1. CORE & USER MODELS
# ============================================================================

class Specialty(Base):
    __tablename__ = "specialties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # Relationships
    doctors: Mapped[List["Doctor"]] = relationship("Doctor", back_populates="specialty")
    referrals: Mapped[List["Referral"]] = relationship("Referral", back_populates="target_specialty")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)

    # Relationships
    patients: Mapped[List["Patient"]] = relationship("Patient", back_populates="user", cascade="all, delete-orphan")


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    specialty_id: Mapped[int] = mapped_column(ForeignKey("specialties.id", ondelete="RESTRICT"), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    room_number: Mapped[str] = mapped_column(String(10), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Relationships
    specialty: Mapped["Specialty"] = relationship("Specialty", back_populates="doctors")
    schedules: Mapped[List["DoctorSchedule"]] = relationship("DoctorSchedule", back_populates="doctor", cascade="all, delete-orphan")
    appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="doctor", cascade="all, delete-orphan")
    medical_records: Mapped[List["MedicalRecord"]] = relationship("MedicalRecord", back_populates="doctor")
    issued_referrals: Mapped[List["Referral"]] = relationship("Referral", back_populates="from_doctor")


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    snils: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="patients")
    appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    referrals: Mapped[List["Referral"]] = relationship("Referral", back_populates="patient", cascade="all, delete-orphan")
    medical_records: Mapped[List["MedicalRecord"]] = relationship("MedicalRecord", back_populates="patient", cascade="all, delete-orphan")


# ============================================================================
# 2. SCHEDULING & APPOINTMENT MODELS
# ============================================================================

class DoctorSchedule(Base):
    __tablename__ = "doctor_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    slot_duration: Mapped[int] = mapped_column(Integer, nullable=False, default=20)

    # Relationships
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="schedules")

    __table_args__ = (
        CheckConstraint("day_of_week BETWEEN 1 AND 7", name="check_day_of_week"),
        CheckConstraint("start_time < end_time", name="check_time_order"),
    )


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    appointment_date: Mapped[date] = mapped_column(Date, nullable=False)
    appointment_time: Mapped[time] = mapped_column(Time, nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(default=AppointmentStatus.scheduled, nullable=False)

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="appointments")
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="appointments")
    medical_record: Mapped[Optional["MedicalRecord"]] = relationship("MedicalRecord", back_populates="appointment")

    # CRITICAL UNIQUE CONSTRAINT: Prevents double booking at the database engine level
    __table_args__ = (
        UniqueConstraint("doctor_id", "appointment_date", "appointment_time", name="unique_doctor_time_slot"),
    )


# ============================================================================
# 3. MEDICAL HISTORY & REFERRALS
# ============================================================================

class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    from_doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False)
    target_specialty_id: Mapped[int] = mapped_column(ForeignKey("specialties.id", ondelete="RESTRICT"), nullable=False)
    issue_date: Mapped[date] = mapped_column(Date, nullable=False, server_default=text("CURRENT_DATE") if 'text' in globals() else None)
    is_used: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="referrals")
    from_doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="issued_referrals")
    target_specialty: Mapped["Specialty"] = relationship("Specialty", back_populates="referrals")


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False)
    appointment_id: Mapped[Optional[int]] = mapped_column(ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    visit_date: Mapped[date] = mapped_column(Date, nullable=False)
    complaints: Mapped[str] = mapped_column(Text, nullable=False)
    diagnosis: Mapped[str] = mapped_column(Text, nullable=False)
    treatment_plan: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="medical_records")
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="medical_records")
    appointment: Mapped[Optional["Appointment"]] = relationship("Appointment", back_populates="medical_record")

