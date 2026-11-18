from config import Config
from extensions import db
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from forms import CheckoutForm
from models import Book, Category, Order, OrderItem, OrderStatusHistory
from sqlalchemy import or_, select

shop_bp = Blueprint("shop", __name__)


@shop_bp.route("/")
def home():
    """Trang chủ chuyển hướng sang danh sách sách"""
    return redirect(url_for("shop.index"))


@shop_bp.route("/books")
def index():
    """Màn 1: Danh sách sách (Grid, Tìm kiếm, Lọc danh mục)"""
    q = request.args.get("q", "").strip()
    category_id = request.args.get("category_id", type=int)
    page = request.args.get("page", 1, type=int)

    query = select(Book)

    if q:
        query = query.where(
            or_(Book.title.ilike(f"%{q}%"), Book.author.ilike(f"%{q}%"))
        )

    if category_id:
        query = query.where(Book.category_id == category_id)

    query = query.order_by(Book.id.desc())

    books_pagination = db.paginate(
        query, page=page, per_page=Config.ITEMS_PER_PAGE_SHOP, error_out=False
    )
    categories = db.session.scalars(
        select(Category).order_by(Category.name.asc())
    ).all()

    return render_template(
        "shop/index.html",
        books=books_pagination.items,
        pagination=books_pagination,
        categories=categories,
        current_category=category_id,
        search_query=q,
    )


@shop_bp.route("/books/<int:id>")
def book_detail(id):
    """Màn 2: Chi tiết sách"""
    book = db.session.get(Book, id)
    if not book:
        abort(404)

    cart = session.get("cart", {})
    in_cart = cart.get(str(id), 0)
    max_selectable = max(0, book.stock - in_cart)

    return render_template(
        "shop/detail.html", book=book, in_cart=in_cart, max_selectable=max_selectable
    )


@shop_bp.route("/cart/add-quick", methods=["POST"])
def add_to_cart_quick():
    """Thêm nhanh 1 cuốn vào giỏ từ Màn 1 (PRG)"""
    book_id = request.form.get("book_id", type=int)
    return_url = request.form.get("return_url") or url_for("shop.index")

    if not book_id:
        flash("Sách không hợp lệ.", "error")
        return redirect(return_url)

    book = db.session.get(Book, book_id)
    if not book:
        flash("Sách không tồn tại.", "error")
        return redirect(return_url)

    if book.stock <= 0:
        flash(f"Sách '{book.title}' đã hết hàng.", "error")
        return redirect(return_url)

    cart = session.get("cart", {})
    str_id = str(book_id)
    current_qty = cart.get(str_id, 0)

    if current_qty + 1 > book.stock:
        flash(
            f"Không thể thêm. Bạn đã có {current_qty} cuốn trong giỏ (tồn kho: {book.stock} cuốn).",
            "warning",
        )
    else:
        cart[str_id] = current_qty + 1
        session["cart"] = cart
        session.modified = True
        flash(f"✓ Đã thêm 1 × {book.title} vào giỏ hàng.", "success")

    return redirect(return_url)


@shop_bp.route("/cart/add", methods=["POST"])
def add_to_cart():
    """Thêm sách vào giỏ với số lượng tùy chọn từ Màn 2"""
    book_id = request.form.get("book_id", type=int)
    quantity = request.form.get("quantity", 1, type=int)

    if not book_id:
        flash("Sách không hợp lệ.", "error")
        return redirect(url_for("shop.index"))

    book = db.session.get(Book, book_id)
    if not book:
        abort(404)

    if quantity <= 0:
        flash("Số lượng chọn mua phải lớn hơn 0.", "error")
        return redirect(url_for("shop.book_detail", id=book.id))

    cart = session.get("cart", {})
    str_id = str(book_id)
    current_qty = cart.get(str_id, 0)

    if current_qty + quantity > book.stock:
        available = max(0, book.stock - current_qty)
        flash(f"Số lượng vượt quá tồn kho khả dụng ({available} cuốn).", "error")
        return redirect(url_for("shop.book_detail", id=book.id))

    cart[str_id] = current_qty + quantity
    session["cart"] = cart
    session.modified = True
    flash(f"✓ Đã thêm {quantity} × {book.title} vào giỏ hàng.", "success")

    return redirect(url_for("shop.book_detail", id=book.id))


@shop_bp.route("/cart")
def view_cart():
    """Màn 3: Xem giỏ hàng (Giá lấy MỚI NHẤT từ CSDL)"""
    cart = session.get("cart", {})
    cart_items = []
    total_amount = 0.0

    if cart:
        book_ids = [int(bid) for bid in cart if bid.isdigit()]
        if book_ids:
            books = db.session.scalars(select(Book).where(Book.id.in_(book_ids))).all()
            books_map = {b.id: b for b in books}

            # Duyệt cart và tính toán
            for bid_str, qty in list(cart.items()):
                bid = int(bid_str)
                book = books_map.get(bid)
                if book:
                    # Đảm bảo số lượng không vượt tồn kho hiện hành
                    actual_qty = min(qty, book.stock) if book.stock > 0 else 0
                    if actual_qty == 0 and book.stock == 0:
                        # Tùy chọn: có thể giữ lại với qty 0 hoặc thông báo hết hàng
                        pass
                    subtotal = book.price * qty
                    total_amount += subtotal
                    cart_items.append(
                        {
                            "book": book,
                            "quantity": qty,
                            "unit_price": book.price,
                            "subtotal": subtotal,
                        }
                    )

    return render_template(
        "shop/cart.html", cart_items=cart_items, total_amount=total_amount
    )


@shop_bp.route("/cart/update/<int:book_id>", methods=["POST"])
def update_cart_item(book_id):
    """Cập nhật số lượng (+ / -)"""
    action = request.form.get("action")
    cart = session.get("cart", {})
    str_id = str(book_id)

    if str_id in cart:
        book = db.session.get(Book, book_id)
        if not book:
            cart.pop(str_id, None)
        else:
            if action == "increase":
                if cart[str_id] < book.stock:
                    cart[str_id] += 1
                else:
                    flash(
                        f"Không thể tăng: Đã chạm giới hạn tồn kho ({book.stock} cuốn).",
                        "warning",
                    )
            elif action == "decrease":
                cart[str_id] -= 1
                if cart[str_id] <= 0:
                    cart.pop(str_id, None)
                    flash(f"Đã xoá '{book.title}' khỏi giỏ hàng.", "info")

        session["cart"] = cart
        session.modified = True

    return redirect(url_for("shop.view_cart"))


@shop_bp.route("/cart/remove/<int:book_id>", methods=["POST"])
def remove_cart_item(book_id):
    """Xóa một đầu sách khỏi giỏ hàng"""
    cart = session.get("cart", {})
    str_id = str(book_id)

    if str_id in cart:
        cart.pop(str_id, None)
        session["cart"] = cart
        session.modified = True
        flash("Đã xoá sách khỏi giỏ hàng.", "info")

    return redirect(url_for("shop.view_cart"))


@shop_bp.route("/cart/clear", methods=["POST"])
def clear_cart():
    """Xóa toàn bộ giỏ hàng"""
    session.pop("cart", None)
    session.modified = True
    flash("Đã làm trống giỏ hàng.", "info")
    return redirect(url_for("shop.view_cart"))


@shop_bp.route("/checkout", methods=["GET", "POST"])
def checkout():
    """Màn 4: Thông tin thanh toán (Form Flask-WTF + Tóm tắt)"""
    cart = session.get("cart", {})
    if not cart:
        flash(
            "Giỏ hàng của bạn đang trống. Vui lòng chọn sách trước khi thanh toán.",
            "warning",
        )
        return redirect(url_for("shop.view_cart"))

    # Lấy thông tin sách & tính toán giá trị đơn
    book_ids = [int(bid) for bid in cart if bid.isdigit()]
    books = db.session.scalars(select(Book).where(Book.id.in_(book_ids))).all()
    books_map = {b.id: b for b in books}

    items_summary = []
    subtotal = 0.0

    for bid_str, qty in cart.items():
        bid = int(bid_str)
        book = books_map.get(bid)
        if book:
            line_subtotal = book.price * qty
            subtotal += line_subtotal
            items_summary.append(
                {
                    "book": book,
                    "quantity": qty,
                    "unit_price": book.price,
                    "subtotal": line_subtotal,
                }
            )

    # Tính phí giao hàng: 20k, miễn phí nếu tạm tính >= 200k
    shipping_fee = (
        0.0 if subtotal >= Config.FREE_SHIPPING_THRESHOLD else Config.SHIPPING_FEE
    )
    total_amount = subtotal + shipping_fee

    form = CheckoutForm()

    if form.validate_on_submit():
        # Kiểm tra tồn kho lần cuối trong Database Transaction
        for item in items_summary:
            current_book = db.session.get(Book, item["book"].id)
            if not current_book or current_book.stock < item["quantity"]:
                db.session.rollback()
                flash(
                    f"Rất tiếc, sách '{item['book'].title}' chỉ còn tồn {current_book.stock if current_book else 0} cuốn. Vui lòng cập nhật giỏ hàng.",
                    "error",
                )
                return redirect(url_for("shop.view_cart"))

        # Tạo Order
        customer_name = (form.customer_name.data or "").strip()
        customer_phone = (form.customer_phone.data or "").strip()
        customer_email = (
            form.customer_email.data.strip() if form.customer_email.data else None
        )
        shipping_address = (form.shipping_address.data or "").strip()
        note = form.note.data.strip() if form.note.data else None
        payment_method = form.payment_method.data or "Tiền mặt"

        order = Order(
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            shipping_address=shipping_address,
            note=note,
            payment_method=payment_method,
            shipping_fee=shipping_fee,
            total_amount=total_amount,
            status=Order.STATUS_PENDING,
        )
        db.session.add(order)
        db.session.flush()  # Sinh order.id

        # Tạo OrderItem và trừ tồn kho
        for item in items_summary:
            current_book = db.session.get(Book, item["book"].id)
            if current_book is not None:
                order_item = OrderItem(
                    order_id=order.id,
                    book_id=current_book.id,
                    quantity=item["quantity"],
                    unit_price=current_book.price,  # Lưu giá cố định tại thời điểm đặt
                    subtotal=item["subtotal"],
                )
                # Trừ tồn kho
                current_book.stock -= item["quantity"]
                db.session.add(order_item)

        # Ghi nhận lịch sử trạng thái đầu tiên
        history = OrderStatusHistory(
            order_id=order.id,
            status=Order.STATUS_PENDING,
            note="Khách hàng đặt hàng trực tuyến",
        )
        db.session.add(history)

        db.session.commit()

        # Xóa giỏ hàng khỏi session
        session.pop("cart", None)
        session.modified = True

        flash(
            "Đặt hàng thành công! Mã đơn hàng của bạn là #" + str(order.id), "success"
        )
        return redirect(url_for("shop.order_success", id=order.id))

    return render_template(
        "shop/checkout.html",
        form=form,
        items=items_summary,
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        total_amount=total_amount,
        free_shipping_threshold=Config.FREE_SHIPPING_THRESHOLD,
    )


@shop_bp.route("/orders/<int:id>")
def order_success(id):
    """Màn 5: Đặt thành công"""
    order = db.session.get(Order, id)
    if not order:
        abort(404)

    return render_template("shop/order_success.html", order=order)
