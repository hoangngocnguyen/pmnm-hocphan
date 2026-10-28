from flask import Blueprint, render_template, request

bmi_bp = Blueprint("bmi", __name__)


def kiem_tra_so_do(
    raw: str, ten: str, don_vi: str, toi_thieu: float, toi_da: float
) -> tuple[float | None, str | None]:
    """Đọc và kiểm tra một số đo, chấp nhận dấu phẩy thập phân."""
    value = raw.strip().replace(",", ".")
    if not value:
        return None, f"Vui lòng nhập {ten.lower()}."
    try:
        number = float(value)
    except ValueError:
        return None, "Vui lòng nhập một số."
    if not toi_thieu <= number <= toi_da:
        return None, f"Giá trị phải từ {toi_thieu:g} đến {toi_da:g} {don_vi}."
    return number, None


@bmi_bp.route("/", methods=["GET", "POST"])
def tinh_bmi():
    raw = {"chieu_cao": "", "can_nang": ""}
    errors: dict[str, str | None] = {"chieu_cao": None, "can_nang": None}
    bmi = None
    phan_loai = None
    mau = None
    can_nang_ly_tuong = None

    if request.method == "POST":
        raw["chieu_cao"] = request.form.get("chieu_cao", "")
        raw["can_nang"] = request.form.get("can_nang", "")
        chieu_cao, errors["chieu_cao"] = kiem_tra_so_do(
            raw["chieu_cao"], "chiều cao", "cm (nhập cm, không nhập m)", 50, 250
        )
        can_nang, errors["can_nang"] = kiem_tra_so_do(
            raw["can_nang"], "cân nặng", "kg", 10, 300
        )

        if errors["chieu_cao"] is None and errors["can_nang"] is None:
            assert chieu_cao is not None and can_nang is not None
            chieu_cao_m = chieu_cao / 100
            bmi_chua_lam_tron = can_nang / (chieu_cao_m**2)
            bmi = round(bmi_chua_lam_tron, 1)
            can_nang_ly_tuong = (
                round(18.5 * chieu_cao_m**2, 1),
                round(22.9 * chieu_cao_m**2, 1),
            )

            if bmi_chua_lam_tron < 18.5:
                phan_loai, mau = "Thiếu cân", "yellow"
            elif bmi_chua_lam_tron < 23:
                phan_loai, mau = "Bình thường", "green"
            elif bmi_chua_lam_tron < 25:
                phan_loai, mau = "Thừa cân", "yellow"
            else:
                phan_loai, mau = "Béo phì", "red"

    return render_template(
        "projects/chuong-05/bmi.html",
        raw=raw,
        errors=errors,
        bmi=bmi,
        phan_loai=phan_loai,
        mau=mau,
        can_nang_ly_tuong=can_nang_ly_tuong,
    )
