import cloudinary
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "ashdbajshdbaskdbajskdbahj34234sdb"
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@localhost/spadb?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

cloudinary.config(
    cloud_name = "ducouuixg",
    api_key = "222724154773865",
    api_secret = "im6x_Bg68qbbPgx9RYalYAm5iwY"
)

db = SQLAlchemy(app)