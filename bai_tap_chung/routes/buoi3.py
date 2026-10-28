from flask import Blueprint, render_template, request

buoi3_bp = Blueprint("buoi3", __name__)


@buoi3_bp.route("/calc", methods=["GET", "POST"])
def home():
    a = ""
    b = ""
    op = "+"
    result = None
    errors: dict[str, str | None] = {"a": None, "b": None, "op": None}

    if request.method == "POST":
        a = request.form.get("a", "").strip()
        b = request.form.get("b", "").strip()
        op = request.form.get("op", "")

        values = {}
        for name, raw in (("a", a), ("b", b)):
            try:
                # Chấp nhận dấu phẩy, dấu chấm
                values[name] = float(raw.replace(",", "."))
            except ValueError:
                errors[name] = "Vui lòng nhập số hợp lệ."

        if op not in ("+", "-", "*", "/"):
            errors["op"] = "Phép toán không hợp lệ."

        if not errors["a"] and not errors["b"] and not errors["op"]:
            left, right = values["a"], values["b"]
            if op == "/" and right == 0:
                errors["b"] = "Không thể chia cho 0."
            else:
                calculated = {
                    "+": left + right,
                    "-": left - right,
                    "*": left * right,
                    "/": left / right if right != 0 else None,
                }[op]

                display = (
                    str(int(calculated)) if calculated.is_integer() else str(calculated)
                )
                result = f"{a} {op} {b} = {display}"

    return render_template(
        "projects/bai-tap/math.html", result=result, a=a, b=b, op=op, errors=errors
    )
