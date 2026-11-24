from flask import render_template, request, redirect
from flask_login import current_user, login_user, logout_user
from sqlalchemy.exc import SQLAlchemyError

import dao
from SpaApp import app, login, db
from SpaApp.models import User, Customer, UserRole

@app.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role == UserRole.MANAGER:
            return redirect('/manager')
        elif current_user.role == UserRole.RECEPTIONIST:
            return redirect('/receptionist')
        elif current_user.role == UserRole.TECHNICIAN:
            return redirect('/technician')
        elif current_user.role == UserRole.CASHIER:
            return redirect('/cashier')
    q = request.args.get('q','')
    cate_id = request.args.get('cate_id')
    page = request.args.get('page',type=int)
    page_size = request.args.get('page_size',10)
    pagination = dao.load_services(q=q, cate_id=cate_id, page=page)
    return render_template("customer/index.html",
                           services=pagination.items,
                           pagination=pagination,
                           cates=dao.load_categories(),
                           q=q,
                           cate_id=cate_id)

@app.route("/login", methods = ['get','post'])
def login_my_user():
    if current_user.is_authenticated:
        return redirect('/')
    err_msg = None
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username, password)
        if user:
            login_user(user)
            return redirect('/')

        err_msg = 'Tài khoản hoặc mật khẩu không chính xác!'
    return render_template('auth/login.html', err_msg = err_msg)

@app.route("/register", methods = ['get','post'])
def register_my_user():
    if current_user.is_authenticated:
        return redirect('/')
    err_msg = None
    suc_msg = None
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        phone = request.form.get('phone')
        fullname = request.form.get('fullname')
        if dao.get_user_by_username(username):
            err_msg = "Tài khoản đã tồn tại!"
            return render_template('auth/register.html',
                                   err_msg=err_msg,
                                   phone=phone,
                                   fullname=fullname)
        if password != confirm_password:
            err_msg = "Mật khẩu xác nhận không khớp"
            return render_template('auth/register.html',
                                   err_msg=err_msg,
                                   fullname=fullname,
                                   username=username,
                                   phone=phone)
        else:
            u=dao.add_user(fullname,username,password)
            cus = Customer(fullname=fullname, phone=phone, user_id=u.id)
            db.session.add(cus)
            db.session.commit()
            suc_msg = "Đăng ký thành công, quay lại trang Đăng nhập"
    return render_template('auth/register.html', suc_msg=suc_msg)
@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)

@app.route("/logout")
def logout_my_user():
    logout_user()
    return redirect('/login')

@app.route("/profile", methods = ['GET','POST'])
def my_profile():
    if not current_user.is_authenticated:
        return redirect('/login')
    err_msg = None
    suc_msg = None
    phone = None
    if request.method.__eq__('POST'):
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        try:
            dao.update_user(current_user.id, fullname, email)
            if current_user.role.name.__eq__('CUSTOMER'):
                phone = request.form.get('phone')
                dao.update_customer(current_user.id, fullname, phone)
                db.session.commit()
            suc_msg = "Cập nhật thông tin thành công!"
        except SQLAlchemyError:
            db.session.rollback()
            err_msg = "Cập nhật thất bại, vui lòng thử lại sau!"
    if request.method.__eq__('GET'):
        if current_user.role.name.__eq__('CUSTOMER'):
            cus = dao.get_customer_by_user_id(current_user.id)
            phone = cus.phone
    return render_template('auth/profile.html',phone=phone, err_msg=err_msg, suc_msg=suc_msg)

@app.route('/password',methods=['GET','POST'])
def change_my_password():
    if not current_user.is_authenticated:
        return redirect('/login')
    err_msg = None
    suc_msg = None
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    if request.method.__eq__('POST'):
        try:
            if new_password.__ne__(confirm_password):
                err_msg='Xác nhận mật khẩu không chính xác!'
            else:
                dao.change_password(current_user.id,old_password, new_password)
                suc_msg = 'Đổi mật khẩu thành công.'
        except ValueError as ex:
            db.session.rollback()
            err_msg = str(ex)
        except SQLAlchemyError:
            db.session.rollback()
            err_msg = 'Cập nhật thất bại, vui lòng thử lại sau!'
    return render_template('auth/change_password.html',suc_msg=suc_msg, err_msg=err_msg)

if __name__=="__main__":
    app.run(debug=True, port=5001)