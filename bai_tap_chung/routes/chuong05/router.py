from flask import Blueprint, render_template

from .bmi import bmi_bp
from .calc import calc_bp
from .diemhocphan import diemhocphan_bp

chuong05_bp = Blueprint("chuong05", __name__)

# Bài 1: Máy tính (calc)
chuong05_bp.register_blueprint(calc_bp, url_prefix="/calc")

# Bài 2: Tính điểm học phần (diemhocphan)
chuong05_bp.register_blueprint(diemhocphan_bp, url_prefix="/diem-hoc-phan")

# Bài 3: Tính chỉ số BMI (bmi)
chuong05_bp.register_blueprint(bmi_bp, url_prefix="/bmi")

chuong5_bp = chuong05_bp  # Alias for backward compatibility


@chuong05_bp.route("/")
def home():
    return render_template("projects/chuong-05/index.html")
