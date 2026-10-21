from flask import Flask, render_template, request

app = Flask(__name__)

SHOP = {
    "name": "Cà phê Sông Hương",
    "address": "12 Lê Lợi, Huế",
    "open": 7,
    "close": 22,
}
PROMOTIONS = ["Giảm 10% cho sinh viên", "Mua 2 tặng 1 vào thứ 2"]


MENU = [
    {"name": "cà phê đen", "price": 20000, "available": True},
    {"name": "bạc xỉu", "price": 30000, "available": False},
    {"name": "cà phê sữa đá", "price": 25000, "available": True},
    {"name": "trà đào cam sả", "price": 35000, "available": True},
    {"name": "trà matcha latte", "price": 40000, "available": True},
    {"name": "sinh tố bơ", "price": 45000, "available": False},
    {"name": "bánh croissant", "price": 32000, "available": True},
]


@app.template_filter("vnd")
def vnd_format(value):
    try:
        return f"{int(value):,} đ".replace(",", ".")
    except (ValueError, TypeError):
        return f"{value} đ"


@app.route("/")
def home():
    gio_param = request.args.get("gio")

    gio = None
    trang_thai_mo_cua = None

    if gio_param is not None:
        try:
            gio = int(gio_param)
            # Quán mở từ 7h đến trước 22h (7 <= gio < 22)
            if SHOP["open"] <= gio < SHOP["close"]:
                trang_thai_mo_cua = True
            else:
                trang_thai_mo_cua = False
        except ValueError:
            gio = None  # Nhập không phải số hợp lệ

    return render_template(
        "index.html",
        shop=SHOP,
        promotions=PROMOTIONS,
        gio=gio,
        trang_thai_mo_cua=trang_thai_mo_cua,
    )


@app.route("/menu")
def show_menu():
    # Tính toán thông số thống kê
    total_items = len(MENU)
    available_count = sum(1 for item in MENU if item["available"])
    avg_price = (
        sum(item["price"] for item in MENU) / total_items if total_items > 0 else 0
    )

    return render_template(
        "menu.html",
        menu=MENU,
        total_items=total_items,
        available_count=available_count,
        avg_price=avg_price,
    )


if __name__ == "__main__":
    app.run(debug=True)
