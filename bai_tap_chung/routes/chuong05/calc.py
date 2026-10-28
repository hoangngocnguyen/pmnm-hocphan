from flask import Blueprint, render_template, request

calc_bp = Blueprint("calc", __name__)


@calc_bp.route("/", methods=["GET", "POST"])
def tinh_toan():
    a = ""
    b = ""
    op = "+"
    result = None
    errors: dict[str, str | None] = {"a": None, "b": None, "op": None}

    if request.method == "POST":
        a = request.form.get("a", "").strip()
        b = request.form.get("b", "").strip()
        op = request.form.get("op", "+")

        values = {}
        for name, raw in (("a", a), ("b", b)):
            try:
                values[name] = float(raw.replace(",", "."))
            except ValueError:
                errors[name] = "Vui lòng nhập số hợp lệ."

        if op not in ("+", "-", "*", "/", "%"):
            errors["op"] = "Phép toán không hợp lệ."

        if not errors["a"] and not errors["b"] and not errors["op"]:
            left, right = values["a"], values["b"]
            if op == "/" and right == 0:
                errors["b"] = "Không thể chia cho 0."
            elif op == "%" and right == 0:
                errors["b"] = "Không thể chia lấy dư cho 0."
            else:
                calculated = {
                    "+": left + right,
                    "-": left - right,
                    "*": left * right,
                    "/": left / right if right != 0 else 0,
                    "%": left % right if right != 0 else 0,
                }[op]

                display = (
                    str(int(calculated)) if calculated.is_integer() else f"{calculated:g}"
                )
                result = f"{a} {op} {b} = {display}"

    return render_template(
        "projects/chuong-05/calc.html",
        result=result,
        a=a,
        b=b,
        op=op,
        errors=errors,
    )


# Alias
home = tinh_toan

