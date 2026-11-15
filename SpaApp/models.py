import enum

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Boolean, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from SpaApp import app, db
from datetime import datetime as dt

class UserRole(enum.Enum):
    MANAGER = "MANAGER"
    RECEPTIONIST = "RECEPTIONIST"
    TECHNICIAN = "TECHNICIAN"
    CASHIER = "CASHIER"
    CUSTOMER = "CUSTOMER"

class BookingChannel(enum.Enum):
    ONLINE = "ONLINE"
    WALK_IN = "WALK_IN"

class AppointmentStatus(enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW_PENDING = "NO_SHOW_PENDING"
    NO_SHOW = "NO_SHOW"

class PaymentMethod(enum.Enum):
    CASH = "CASH"
    TRANSFER = "TRANSFER"


class PaymentStatus(enum.Enum):
    UNPAID = "UNPAID"
    PAID = "PAID"

class Category(db.Model):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    services = relationship("Service", backref="category",lazy=True)
    def __str__(self):
        return self.name

class Service(db.Model):
    __tablename__ = "service"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    price = Column(Float, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    image = Column(String(255), default="https://res.cloudinary.com/ducouuixg/image/upload/f_auto/q_auto/782936ea-9d24-4d10-a669-36d10bf012fe.png")
    __table_args__ = (
        CheckConstraint("price>=0", name = "ck_service_price"),
        CheckConstraint("duration_minutes>0", name = "ck_service_duration_minutes"),
    )
    def __str__(self):
        return self.name

class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(30), nullable=False,unique=True)
    password = Column(String(255), nullable=False)
    fullname = Column(String(45), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    is_active = Column(Boolean, default=True,nullable=False)
    created_at = Column(DateTime, default=dt.now)

    def __str__(self):
        return self.fullname

class Customer(db.Model):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True,unique=True)
    fullname = Column(String(45), nullable=False)
    phone = Column(String(30), nullable=False)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=dt.now)

class Appointment(db.Model):
    __tablename__ = "appointment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customer.id'), nullable=False)
    service_id = Column(Integer, ForeignKey('service.id'), nullable=False)
    technician_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime,nullable=False)
    booking_channel = Column(Enum(BookingChannel), nullable=False)
    status = Column(Enum(AppointmentStatus), nullable=False)
    created_at = Column(DateTime, default=dt.now)
    updated_at = Column(DateTime, default=dt.now, onupdate=dt.now)
    __table_args__ = (
        CheckConstraint("end_time > start_time",name="ck_appointment_time"),
    )

class ServiceRecord(db.Model):
    __tablename__ = "service_record"
    id = Column(Integer, primary_key=True, autoincrement=True)
    appointment_id = Column(Integer, ForeignKey('appointment.id'), nullable=False,unique=True)
    technician_note = Column(String(255), nullable=True)
    customer_feedback = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=dt.now)

class Bill(db.Model):
    __tablename__ = "bill"
    id = Column(Integer, primary_key=True, autoincrement=True)
    service_record_id = Column(Integer, ForeignKey('service_record.id'), nullable=False,unique=True)
    cashier_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    service_price = Column(Float, nullable=False)
    discount_percent = Column(Integer, nullable=False)
    discount_amount = Column(Float, nullable=False)
    vat_percent = Column(Integer, nullable=False)
    vat_amount = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_status = Column(Enum(PaymentStatus), nullable=False)
    created_at = Column(DateTime, default=dt.now)

class Notification(db.Model):
    __tablename__ = "notification"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    appointment_id = Column(Integer, ForeignKey('appointment.id'), nullable=False)
    bill_id = Column(Integer, ForeignKey('bill.id'), nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(String(255), nullable=False)
    is_read = Column(Boolean, nullable=False)
    created_at = Column(DateTime, default=dt.now)

class SystemConfig(db.Model):
    __tablename__ = "system_config"
    id = Column(Integer, primary_key=True, autoincrement=True)
    vat_percent = Column(Integer, nullable=False)
    max_discount_percent = Column(Integer, nullable=False)
    max_appointment_per_tech_per_day = Column(Integer, nullable=False)
    updated_by = Column(Integer, ForeignKey('user.id'), nullable=False)
    updated_at = Column(DateTime, default=dt.now,onupdate=dt.now)
    __table_args__ = (
        CheckConstraint("vat_percent BETWEEN 0 AND 100", name="ck_vat_percent"),
        CheckConstraint("max_discount_percent BETWEEN 0 AND 100", name="ck_max_discount_percent"),
        CheckConstraint("max_appointment_per_tech_per_day BETWEEN 0 AND 100",name="ck_max_appointment_per_tech_per_day"),
    )

if __name__=='__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()




