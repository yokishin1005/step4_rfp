from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# 多対多の関係のための中間テーブル
device_symptoms = Table('device_symptoms', Base.metadata,
    Column('device_id', Integer, ForeignKey('device_master.device_id')),
    Column('symptoms_id', Integer, ForeignKey('symptoms.symptoms_id'))
)

device_effects = Table('device_effects', Base.metadata,
    Column('device_id', Integer, ForeignKey('device_master.device_id')),
    Column('effect_id', Integer, ForeignKey('effects.effect_id'))
)

class ClinicDevice(Base):
    __tablename__ = 'clinic_device'
    clinic_id = Column(Integer, ForeignKey('clinic_master.clinic_id'), primary_key=True)
    device_id = Column(Integer, ForeignKey('device_master.device_id'), primary_key=True)
    clinic = relationship("ClinicMaster", back_populates="devices")
    device = relationship("DeviceMaster", back_populates="clinics")

class ClinicDeviceRentalPrice(Base):
    __tablename__ = 'clinic_device_rental_price'
    clinic_id = Column(Integer, ForeignKey('clinic_master.clinic_id'), primary_key=True)
    device_id = Column(Integer, ForeignKey('device_master.device_id'), primary_key=True)
    rental_duration = Column(String)
    rental_price = Column(Integer)
    clinic = relationship("ClinicMaster", back_populates="rentals")
    device = relationship("DeviceMaster", back_populates="rentals")

class ClinicMaster(Base):
    __tablename__ = 'clinic_master'
    clinic_id = Column(Integer, primary_key=True)
    clinic_name = Column(String)
    register_date = Column(Date)
    address = Column(String)
    building = Column(String)
    email = Column(String)
    tel = Column(String)
    devices = relationship("ClinicDevice", back_populates="clinic")
    rentals = relationship("ClinicDeviceRentalPrice", back_populates="clinic")

class DeviceMaster(Base):
    __tablename__ = 'device_master'
    device_id = Column(Integer, primary_key=True)
    device_name = Column(String)
    manufacture = Column(String)
    basic_price = Column(Integer)
    picture_code = Column(String)
    clinics = relationship("ClinicDevice", back_populates="device")
    rentals = relationship("ClinicDeviceRentalPrice", back_populates="device")
    symptoms = relationship("Symptoms", secondary=device_symptoms, back_populates="devices")
    effects = relationship("Effects", secondary=device_effects, back_populates="devices")

class Effects(Base):
    __tablename__ = 'effects'
    effect_id = Column(Integer, primary_key=True)
    effect_name = Column(String)
    devices = relationship("DeviceMaster", secondary=device_effects, back_populates="effects")

class ReservationRecords(Base):
    __tablename__ = 'reservation_records'
    reserve_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user_master.user_id'))
    clinic_id = Column(Integer, ForeignKey('clinic_master.clinic_id'))
    device_id = Column(Integer, ForeignKey('device_master.device_id'))
    reservation_date = Column(Date)
    start_time = Column(String)
    rental_duration = Column(String)
    payment = Column(Integer)
    after_service = Column(Integer)
    evaluation_service = Column(Integer)
    evaluation_device = Column(Integer)
    user = relationship("UserMaster", back_populates="reservations")
    clinic = relationship("ClinicMaster")
    device = relationship("DeviceMaster")

class Symptoms(Base):
    __tablename__ = 'symptoms'
    symptoms_id = Column(Integer, primary_key=True)
    symptom_name = Column(String)
    devices = relationship("DeviceMaster", secondary=device_symptoms, back_populates="symptoms")

class UserMaster(Base):
    __tablename__ = 'user_master'
    user_id = Column(Integer, primary_key=True)
    user_name = Column(String)
    login_id = Column(String)
    password = Column(String)
    register_date = Column(Date)
    birthday = Column(Date)
    gender = Column(String)
    postcode = Column(String)
    address_pref = Column(String)
    address_town = Column(String)
    address_detail = Column(String)
    email = Column(String)
    tel = Column(String)
    profession = Column(String)
    reservations = relationship("ReservationRecords", back_populates="user")