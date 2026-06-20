from datetime import date, time
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from .models import AppointmentStatus

# ============================================================================
# 1. CORE & SPECIALTY SCHEMAS
# ============================================================================
class SpecialtyResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# 2. USER / PARENT SCHEMAS
# ============================================================================
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Plain text password")
    phone: str = Field(..., max_length=20)

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    phone: str
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# 3. PATIENT / CHILD SCHEMAS
# ============================================================================
class PatientCreate(BaseModel):
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    birth_date: date
    snils: Optional[str] = Field(None, max_length=20)

class PatientResponse(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: str
    birth_date: date
    snils: Optional[str]
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# 4. DOCTOR & SCHEDULE SCHEMAS
# ============================================================================
class DoctorScheduleResponse(BaseModel):
    id: int
    day_of_week: int
    start_time: time
    end_time: time
    slot_duration: int
    model_config = ConfigDict(from_attributes=True)

class DoctorResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    room_number: str
    phone: Optional[str]
    specialty: SpecialtyResponse  # Nested object to automatically include specialty name
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# 5. APPOINTMENT SCHEMAS (Booking)
# ============================================================================
class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time
    status: AppointmentStatus
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# 6. MEDICAL RECORD & REFERRAL SCHEMAS
# ============================================================================
class ReferralResponse(BaseModel):
    id: int
    patient_id: int
    from_doctor_id: int
    target_specialty_id: int
    issue_date: date
    is_used: bool
    model_config = ConfigDict(from_attributes=True)

class MedicalRecordCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None
    visit_date: date
    complaints: str
    diagnosis: str
    treatment_plan: Optional[str] = None

class MedicalRecordResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int]
    visit_date: date
    complaints: str
    diagnosis: str
    treatment_plan: Optional[str]
    model_config = ConfigDict(from_attributes=True)
