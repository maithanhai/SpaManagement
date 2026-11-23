from flask import render_template, request, redirect
from flask_login import current_user, login_user, logout_user

import dao
from SpaApp import app, login, db
from SpaApp.models import User, Customer

@app.route("/")
def index():
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
        else:
            err_msg = 'Tài khoản hoặc mật khẩu không chính xác!'
    return render_template('auth/login.html', err_msg = err_msg)

@app.route("/register", methods = ['get','post'])
def register_my_user():
    if current_user.is_authenticated:
        return redirect('/')
    err_msg = None
    succ = None
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
            succ = "Đăng ký thành công, quay lại trang Đăng nhập"
    return render_template('auth/register.html', succ=succ)
@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)

@app.route("/logout")
def logout_my_user():
    logout_user()
    return redirect('/login')

if __name__=="__main__":
    app.run(debug=True, port=5001)