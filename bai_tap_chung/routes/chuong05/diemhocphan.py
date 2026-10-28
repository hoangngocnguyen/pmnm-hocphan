from flask import Blueprint, render_template, request

diemhocphan_bp = Blueprint("diemhocphan", __name__)


def kiem_tra_diem(raw: str) -> tuple[float | None, str | None]:
    """Kiểm tra một điểm và trả về (giá trị, thông báo lỗi)."""
    value = raw.strip().replace(",", ".")
    if not value:
        return None, "Vui lòng nhập điểm."
    try:
        score = float(value)
    except ValueError:
        return None, "Vui lòng nhập một số."
    if not 0 <= score <= 10:
        return None, "Điểm phải từ 0 đến 10."
    return score, None


@diemhocphan_bp.route("/", methods=["GET", "POST"])
def tinh_diem():
    raw_scores = {name: "" for name in ("cc", "gk", "ck")}
    errors: dict[str, str | None] = {name: None for name in raw_scores}
    total = None
    grade = None
    ghi_chu = None

    if request.method == "POST":
        scores: dict[str, float] = {}
        for name in raw_scores:
            raw_scores[name] = request.form.get(name, "")
            score, error = kiem_tra_diem(raw_scores[name])
            errors[name] = error
            if score is not None:
                scores[name] = score

        if all(error is None for error in errors.values()):
            total = round(
                scores["cc"] * 0.1 + scores["gk"] * 0.3 + scores["ck"] * 0.6, 1
            )
            if scores["ck"] < 1:
                grade = "F"
                ghi_chu = "điểm thi dưới 1"
            elif total >= 8.5:
                grade = "A"
            elif total >= 7.0:
                grade = "B"
            elif total >= 5.5:
                grade = "C"
            elif total >= 4.0:
                grade = "D"
            else:
                grade = "F"

    return render_template(
        "projects/chuong-05/diemhocphan.html",
        scores=raw_scores,
        errors=errors,
        total=total,
        grade=grade,
        ghi_chu=ghi_chu,
    )
