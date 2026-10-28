"""Router and exercises for Chapter 05."""

from .bmi import bmi_bp
from .calc import calc_bp
from .diemhocphan import diemhocphan_bp
from .router import chuong05_bp

chuong5_bp = chuong05_bp  # Alias for backward compatibility

__all__ = ["chuong05_bp", "chuong5_bp", "calc_bp", "diemhocphan_bp", "bmi_bp"]
