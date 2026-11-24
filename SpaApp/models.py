import enum
import hashlib
import json

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, Boolean, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from SpaApp import app, db
from datetime import datetime as dt

class UserRole(enum.Enum):
    MANAGER = 1
    RECEPTIONIST = 2
    TECHNICIAN = 3
    CASHIER = 4
    CUSTOMER = 5

class BookingChannel(enum.Enum):
    ONLINE = 1
    WALK_IN = 2

class AppointmentStatus(enum.Enum):
    PENDING = 1
    CONFIRMED = 2
    IN_PROGRESS = 3
    COMPLETED = 4
    CANCELLED = 5
    NO_SHOW_PENDING = 6
    NO_SHOW = 7

class PaymentMethod(enum.Enum):
    CASH = 1
    TRANSFER = 2


class PaymentStatus(enum.Enum):
    UNPAID = 1
    PAID = 2

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
    description = Column(String(500), nullable=True)
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
    email = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER, nullable=False)
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
        with open("data/categories.json", encoding="utf-8") as f:
            cates = json.load(f)
            for c in cates:
                db.session.add(Category(**c))
        with open("data/services.json", encoding="utf-8") as f:
            services = json.load(f)
            for s in services:
                db.session.add(Service(**s))
        with open("data/users.json", encoding="utf-8") as f:
            users = json.load(f)
            for u in users:
                password = hashlib.md5(u["password"].encode("utf-8")).hexdigest()
                user = User(username=u["username"], password=password, fullname=u["fullname"], email=u.get("email"), role=UserRole[u["role"]])
                db.session.add(user)
            db.session.flush()
        with open("data/customers.json", encoding="utf-8") as f:
            customers = json.load(f)

            for c in customers:
                db.session.add(Customer(**c))
        db.session.commit()




