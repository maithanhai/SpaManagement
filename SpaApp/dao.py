import json
import hashlib

from flask_sqlalchemy.model import Model

from SpaApp import db, app
from SpaApp.models import User, UserRole, Category, Service, Customer


def auth_user(username, password):
    password = hashlib.md5(password.encode("utf-8")).hexdigest()
    return User.query.filter(User.username==username, User.password==password).first()

def add_user(fullname, username, password):
    password = hashlib.md5(password.encode("utf-8")).hexdigest()
    u = User(username=username, password=password, fullname=fullname, role = UserRole.CUSTOMER)
    db.session.add(u)
    db.session.flush()
    return u

def get_user_by_id(user_id):
    return User.query.get(user_id)

def load_categories():
    return Category.query

def load_services(q, cate_id=None,page=1):
    query = Service.query
    if q:
        query = query.filter(Service.name.contains(q))
    if cate_id:
        query = query.filter(Service.category_id.__eq__(int(cate_id)))
    return query.order_by(Service.id).paginate(page=page,per_page=12,error_out=False)

def update_user(user_id, fullname, email):
    u = User.query.get(user_id)
    u.fullname = fullname
    u.email = email


def update_customer(user_id, fullname, phone):
    cus = Customer.query.filter(Customer.user_id.__eq__(user_id)).first()
    cus.fullname = fullname
    cus.phone = phone

def change_password(user_id,old_password ,new_password):
    u = User.query.get(user_id)
    old_hash = hashlib.md5(old_password.encode("utf-8")).hexdigest()
    if u.password.__ne__(old_hash):
        raise ValueError("Mật khẩu cũ không chính xác!")
    u.password = hashlib.md5(new_password.encode("utf-8")).hexdigest()
    db.session.commit()
def get_customer_by_user_id(user_id):
    return Customer.query.filter_by(user_id=user_id).first()
def get_user_by_username(username):
    return User.query.filter(User.username==username).first()
