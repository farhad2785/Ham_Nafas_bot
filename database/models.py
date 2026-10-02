from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    bale_id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # فیلدهای جدید برای ردیابی پیشرفت کاربر
    survey1_submission_id = Column(String(50), nullable=True)
    survey2_submission_id = Column(String(50), nullable=True)
    survey3_submission_id = Column(String(50), nullable=True)
    
    # ارتباط یک‌‌به‌یک با مراقب و بیمار
    caregiver = relationship("Caregiver", back_populates="user", uselist=False)
    patient = relationship("Patient", back_populates="user", uselist=False)

class Caregiver(Base):
    __tablename__ = 'caregivers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.bale_id'), unique=True)
    fullname = Column(String(150))
    phone_number = Column(String(20))
    national_code = Column(String(150))
    age = Column(Integer)
    sex = Column(String(150))
    marital_status = Column(String(50))
    relation = Column(String(50))
    education = Column(String(50))
    job = Column(String(100))
    living_with_patient = Column(String(3))
    special_disease = Column(String(150))
    user = relationship("User", back_populates="caregiver")

class Patient(Base):
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.bale_id'), unique=True)
    fullname = Column(String(150))
    age = Column(Integer)
    sex = Column(String(150))
    stage = Column(String(50))
    disease_duration = Column(String(50))
    user = relationship("User", back_populates="patient")