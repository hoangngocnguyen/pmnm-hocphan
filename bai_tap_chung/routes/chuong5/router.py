from flask import Blueprint, render_template

from .bmi import bmi_bp
from .diemhocphan import diemhocphan_bp

chuong5_bp = Blueprint("chuong5", __name__)
chuong5_bp.register_blueprint(diemhocphan_bp, url_prefix="/diem-hoc-phan")
chuong5_bp.register_blueprint(bmi_bp, url_prefix="/bmi")


@chuong5_bp.route("/")
def home():
    return render_template("projects/chuong5/index.html")
