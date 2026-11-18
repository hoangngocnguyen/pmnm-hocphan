import os
import uuid
from datetime import datetime, timedelta

from config import Config
from extensions import db
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from forms import BookForm, CategoryForm, OrderStatusForm
from models import Book, Category, Order, OrderStatusHistory
from sqlalchemy import and_, func, or_, select
from werkzeug.utils import secure_filename

admin_bp = Blueprint("admin", __name__)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    )


def save_book_image(file_storage, old_filename=None):
    """Lưu ảnh bìa với tên ngẫu nhiên duy nhất và xóa ảnh cũ"""
    if not file_storage or not file_storage.filename:
        return old_filename

    ext = os.path.splitext(secure_filename(file_storage.filename))[1].lower()
    new_filename = f"book_{uuid.uuid4().hex[:12]}{ext}"
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, new_filename)
    file_storage.save(file_path)

    # Xóa ảnh cũ nếu có
    if old_filename:
        old_path = os.path.join(upload_folder, old_filename)
        if os.path.exists(old_path) and os.path.isfile(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass

    return new_filename


# ==========================================
# Màn 6: Tổng quan Dashboard
# ==========================================
@admin_bp.route("", strict_slashes=False)
@admin_bp.route("/", strict_slashes=False)
@admin_bp.route("/dashboard", strict_slashes=False)
def dashboard():
    """Màn 6: Tổng quan (4 KPI cards, 5 đơn mới nhất, sách sắp hết, biểu đồ 7 ngày)"""
    # 1. Số đầu sách
    total_books = db.session.scalar(select(func.count(Book.id))) or 0

    # 2. Số đơn Chờ xác nhận
    pending_orders = (
        db.session.scalar(
            select(func.count(Order.id)).where(Order.status == Order.STATUS_PENDING)
        )
        or 0
    )

    # 3. Doanh thu tháng hiện tại (chỉ tính các đơn Hoàn tất trong tháng)
    now = datetime.now()
    current_month_str = f"{now.month:02d}"
    current_year_str = str(now.year)

    monthly_revenue = (
        db.session.scalar(
            select(func.sum(Order.total_amount))
            .where(Order.status == Order.STATUS_COMPLETED)
            .where(func.strftime("%m", Order.created_at) == current_month_str)
            .where(func.strftime("%Y", Order.created_at) == current_year_str)
        )
        or 0.0
    )

    # 4. Số sách tồn kho <= 5
    low_stock_count = (
        db.session.scalar(select(func.count(Book.id)).where(Book.stock <= 5)) or 0
    )

    # 5 đơn mới nhất
    latest_orders = (
        db.session.scalars(select(Order).order_by(Order.created_at.desc()).limit(5))
        .unique()
        .all()
    )

    # Sách sắp hết hàng (<= 5)
    low_stock_books = db.session.scalars(
        select(Book).where(Book.stock <= 5).order_by(Book.stock.asc()).limit(8)
    ).all()

    # Biểu đồ doanh thu 7 ngày gần nhất
    seven_days_ago = now - timedelta(days=6)
    revenue_data_raw = db.session.execute(
        select(
            func.strftime("%d/%m", Order.created_at).label("day"),
            func.sum(Order.total_amount).label("revenue"),
        )
        .where(Order.status == Order.STATUS_COMPLETED)
        .where(Order.created_at >= seven_days_ago)
        .group_by("day")
        .order_by(Order.created_at.asc())
    ).all()

    # Map sang labels & values 7 ngày
    chart_days = [(now - timedelta(days=i)).strftime("%d/%m") for i in range(6, -1, -1)]
    revenue_map = {row.day: float(row.revenue or 0) for row in revenue_data_raw}
    chart_values = [revenue_map.get(day, 0.0) for day in chart_days]

    return render_template(
        "admin/dashboard.html",
        total_books=total_books,
        pending_orders=pending_orders,
        monthly_revenue=monthly_revenue,
        low_stock_count=low_stock_count,
        latest_orders=latest_orders,
        low_stock_books=low_stock_books,
        current_month=now.month,
        chart_days=chart_days,
        chart_values=chart_values,
    )


# ==========================================
# Màn 7: Quản lý sách
# ==========================================
@admin_bp.route("/books", strict_slashes=False)
def books():
    """Màn 7: Quản lý sách (Bảng sách, 5 cuốn/trang, sắp mới nhất trước, bộ lọc)"""
    q = request.args.get("q", "").strip()
    category_id = request.args.get("category_id", type=int)
    stock_filter = request.args.get("stock_filter", "all")
    page = request.args.get("page", 1, type=int)

    query = select(Book)

    if q:
        query = query.where(
            or_(Book.title.ilike(f"%{q}%"), Book.author.ilike(f"%{q}%"))
        )

    if category_id:
        query = query.where(Book.category_id == category_id)

    if stock_filter == "in_stock":
        query = query.where(Book.stock > 5)
    elif stock_filter == "low_stock":
        query = query.where(and_(Book.stock > 0, Book.stock <= 5))
    elif stock_filter == "out_of_stock":
        query = query.where(Book.stock == 0)

    # Sắp mới nhất trước
    query = query.order_by(Book.id.desc())

    books_pagination = db.paginate(
        query, page=page, per_page=Config.ITEMS_PER_PAGE_ADMIN_BOOKS, error_out=False
    )
    categories = db.session.scalars(
        select(Category).order_by(Category.name.asc())
    ).all()

    # Tổng số sách toàn hệ thống
    total_books_count = db.session.scalar(select(func.count(Book.id))) or 0

    return render_template(
        "admin/books/index.html",
        books=books_pagination.items,
        pagination=books_pagination,
        categories=categories,
        current_category=category_id,
        current_stock=stock_filter,
        search_query=q,
        total_books_count=total_books_count,
    )


# ==========================================
# Màn 8: Thêm & Sửa sách (Dùng chung Form & Template)
# ==========================================
@admin_bp.route("/books/new", methods=["GET", "POST"])
def book_new():
    """Màn 8: Thêm sách mới"""
    return handle_book_form()


@admin_bp.route("/books/<int:id>/edit", methods=["GET", "POST"])
def book_edit(id):
    """Màn 8: Sửa sách"""
    book = db.session.get(Book, id)
    if not book:
        abort(404)
    return handle_book_form(book)


def handle_book_form(book=None):
    """Hàm xử lý chung cho Thêm và Sửa sách"""
    is_edit = book is not None
    form = BookForm(obj=book) if is_edit else BookForm()

    # Nạp danh mục từ CSDL
    categories = db.session.scalars(
        select(Category).order_by(Category.name.asc())
    ).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        # Kiểm tra trùng tên sách (không phân biệt hoa thường)
        cleaned_title = (form.title.data or "").strip()
        existing = db.session.scalar(
            select(Book).where(func.lower(Book.title) == cleaned_title.lower())
        )
        if existing and (not is_edit or (book and existing.id != book.id)):
            form.title.errors = list(form.title.errors or ()) + [
                "Tên sách đã tồn tại trong hệ thống."
            ]
            return render_template(
                "admin/books/form.html", form=form, book=book, is_edit=is_edit
            )

        # Xử lý upload ảnh bìa
        cover_filename = book.cover_image if is_edit and book else None
        if form.cover_image.data:
            cover_filename = save_book_image(
                form.cover_image.data, old_filename=cover_filename
            )

        if not is_edit or not book:
            new_book = Book(
                title=cleaned_title,
                author=(form.author.data or "").strip(),
                publisher=form.publisher.data.strip() if form.publisher.data else None,
                category_id=form.category_id.data or 0,
                publication_year=form.publication_year.data,
                price=form.price.data or 0.0,
                stock=form.stock.data or 0,
                description=(
                    form.description.data.strip() if form.description.data else None
                ),
                cover_image=cover_filename,
            )
            db.session.add(new_book)
            flash(f"✓ Đã thêm sách '{new_book.title}' thành công.", "success")
        else:
            book.title = cleaned_title
            book.author = (form.author.data or "").strip()
            book.publisher = (
                form.publisher.data.strip() if form.publisher.data else None
            )
            book.category_id = form.category_id.data or 0
            book.publication_year = form.publication_year.data
            book.price = form.price.data or 0.0
            book.stock = form.stock.data or 0
            book.description = (
                form.description.data.strip() if form.description.data else None
            )
            book.cover_image = cover_filename
            flash(f"✓ Đã cập nhật sách '{book.title}' thành công.", "success")

        db.session.commit()
        return redirect(url_for("admin.books"))

    return render_template(
        "admin/books/form.html", form=form, book=book, is_edit=is_edit
    )


@admin_bp.route("/books/<int:id>/delete", methods=["POST"])
def book_delete(id):
    """Xóa sách (chặn nếu sách đã có trong đơn hàng)"""
    book = db.session.get(Book, id)
    if not book:
        abort(404)

    # Kiểm tra sách đã có trong bất kỳ đơn hàng nào chưa
    if book.is_in_order():
        flash(f"✕ Không thể xoá sách '{book.title}': Đã có trong đơn hàng!", "error")
        return redirect(url_for("admin.books"))

    title = book.title
    # Xóa file ảnh nếu có
    if book.cover_image:
        old_path = os.path.join(current_app.config["UPLOAD_FOLDER"], book.cover_image)
        if os.path.exists(old_path) and os.path.isfile(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass

    db.session.delete(book)
    db.session.commit()
    flash(f"✓ Đã xoá sách '{title}' thành công.", "success")
    return redirect(url_for("admin.books"))


# ==========================================
# Màn 9: Quản lý danh mục sách
# ==========================================
@admin_bp.route("/categories", methods=["GET", "POST"], strict_slashes=False)
def categories():
    """Màn 9: Danh mục sách (Bảng kèm số sách outerjoin + form bên phải)"""
    edit_id = request.args.get("edit_id", type=int)
    edit_category = db.session.get(Category, edit_id) if edit_id else None

    form = CategoryForm(obj=edit_category) if edit_category else CategoryForm()

    if form.validate_on_submit():
        cleaned_name = (form.name.data or "").strip()
        # Kiểm tra trùng tên danh mục
        existing = db.session.scalar(
            select(Category).where(func.lower(Category.name) == cleaned_name.lower())
        )
        if existing and (not edit_category or existing.id != edit_category.id):
            form.name.errors = [*form.name.errors, "Danh mục đã tồn tại."]
        else:
            if edit_category:
                edit_category.name = cleaned_name
                edit_category.description = (
                    form.description.data.strip() if form.description.data else None
                )
                flash(f"✓ Đã cập nhật danh mục '{edit_category.name}'.", "success")
            else:
                new_cat = Category(
                    name=cleaned_name,
                    description=(
                        form.description.data.strip() if form.description.data else None
                    ),
                )
                db.session.add(new_cat)
                flash(f"✓ Đã thêm danh mục '{new_cat.name}'.", "success")

            db.session.commit()
            return redirect(url_for("admin.categories"))

    # Một truy vấn group_by kể cả danh mục chưa có sách (outerjoin)
    categories_with_count = db.session.execute(
        select(Category, func.count(Book.id).label("book_count"))
        .outerjoin(Book, Category.id == Book.category_id)
        .group_by(Category.id)
        .order_by(Category.name.asc())
    ).all()

    return render_template(
        "admin/categories/index.html",
        categories_data=categories_with_count,
        form=form,
        edit_category=edit_category,
    )


@admin_bp.route("/categories/<int:id>/delete", methods=["POST"])
def category_delete(id):
    """Xóa danh mục: Chỉ khi danh mục không còn sách"""
    category = db.session.get(Category, id)
    if not category:
        abort(404)

    book_count = (
        db.session.scalar(select(func.count(Book.id)).where(Book.category_id == id))
        or 0
    )

    if book_count > 0:
        flash(f'✕ Không thể xoá "{category.name}": còn {book_count} sách.', "error")
        return redirect(url_for("admin.categories"))

    cat_name = category.name
    db.session.delete(category)
    db.session.commit()
    flash(f'✓ Đã xoá danh mục "{cat_name}" thành công.', "success")
    return redirect(url_for("admin.categories"))


# ==========================================
# Màn 10: Quản lý đơn hàng
# ==========================================
@admin_bp.route("/orders", strict_slashes=False)
def orders():
    """Màn 10: Danh sách đơn hàng (Tab trạng thái group_by, tìm kiếm, tính tổng chân bảng)"""
    status_tab = request.args.get("status", "all")
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)

    # 1. Đếm số đơn mỗi trạng thái bằng 1 truy vấn group_by
    status_counts_raw = db.session.execute(
        select(Order.status, func.count(Order.id)).group_by(Order.status)
    ).all()
    status_counts = dict(status_counts_raw)
    total_orders = sum(status_counts.values())

    # 2. Xây dựng truy vấn danh sách đơn hàng
    query = select(Order)

    if status_tab != "all" and status_tab in Order.STATUS_CHOICES:
        query = query.where(Order.status == status_tab)

    if q:
        # Tìm theo mã đơn #id, tên khách hàng, số điện thoại
        id_search = int(q.replace("#", "")) if q.replace("#", "").isdigit() else None
        filters = [
            Order.customer_name.ilike(f"%{q}%"),
            Order.customer_phone.ilike(f"%{q}%"),
        ]
        if id_search is not None:
            filters.append(Order.id == id_search)
        query = query.where(or_(*filters))

    query = query.order_by(Order.created_at.desc())

    # 3. Tính toán tổng số đơn và tổng giá trị cho bộ lọc hiện tại (dòng cuối)
    filtered_orders_all = db.session.scalars(query).unique().all()
    filter_total_count = len(filtered_orders_all)
    filter_total_amount = sum(o.total_amount for o in filtered_orders_all)

    # 4. Phân trang 10 đơn/trang
    orders_pagination = db.paginate(
        query, page=page, per_page=Config.ITEMS_PER_PAGE_ADMIN_ORDERS, error_out=False
    )

    return render_template(
        "admin/orders/index.html",
        orders=orders_pagination.items,
        pagination=orders_pagination,
        status_tab=status_tab,
        status_counts=status_counts,
        total_orders=total_orders,
        search_query=q,
        filter_total_count=filter_total_count,
        filter_total_amount=filter_total_amount,
    )


# ==========================================
# Màn 11: Chi tiết đơn hàng & State Machine
# ==========================================
@admin_bp.route("/orders/<int:id>", strict_slashes=False)
def order_detail(id):
    """Màn 11: Chi tiết đơn hàng"""
    order = db.session.get(Order, id)
    if not order:
        abort(404)

    status_form = OrderStatusForm()
    # Nạp các trạng thái hợp lệ có thể chuyển đổi
    valid_transitions = []
    if order.status == Order.STATUS_PENDING:
        valid_transitions = [Order.STATUS_SHIPPING, Order.STATUS_CANCELLED]
    elif order.status == Order.STATUS_SHIPPING:
        valid_transitions = [Order.STATUS_COMPLETED, Order.STATUS_CANCELLED]

    status_form.new_status.choices = [(s, s) for s in valid_transitions]

    return render_template(
        "admin/orders/detail.html",
        order=order,
        status_form=status_form,
        valid_transitions=valid_transitions,
    )


@admin_bp.route("/orders/<int:id>/update-status", methods=["POST"])
def order_update_status(id):
    """Cập nhật trạng thái đơn hàng (chỉ cho chuyển trạng thái hợp lệ, hoàn kho khi hủy)"""
    order = db.session.get(Order, id)
    if not order:
        abort(404)

    if order.is_terminal_status():
        flash(
            "Đơn hàng đã hoàn tất hoặc đã huỷ, không thể thay đổi trạng thái nữa.",
            "warning",
        )
        return redirect(url_for("admin.order_detail", id=order.id))

    new_status = request.form.get("new_status")
    action_type = request.form.get("action_type")  # Có thể là 'cancel' từ nút Huỷ đơn
    note = request.form.get("note", "").strip()

    if action_type == "cancel":
        new_status = Order.STATUS_CANCELLED
        note = note or "Quản trị viên huỷ đơn hàng"

    if not new_status or not order.can_transition_to(new_status):
        flash("Chuyển đổi trạng thái không hợp lệ.", "error")
        return redirect(url_for("admin.order_detail", id=order.id))

    old_status = order.status
    order.status = new_status

    # NẾU HUỶ ĐƠN: TỰ ĐỘNG HOÀN LẠI TỒN KHO CHO CÁC SÁCH TRONG ĐƠN
    if new_status == Order.STATUS_CANCELLED and old_status != Order.STATUS_CANCELLED:
        for item in order.items:
            item.book.stock += item.quantity
        flash(f"✓ Đã huỷ đơn hàng #{order.id} và hoàn lại số lượng tồn kho.", "info")
    else:
        flash(
            f"✓ Đã chuyển trạng thái đơn hàng #{order.id} sang '{new_status}'.",
            "success",
        )

    # Ghi nhận lịch sử thay đổi
    history = OrderStatusHistory(
        order_id=order.id,
        status=new_status,
        note=note or f"Chuyển từ {old_status} sang {new_status}",
    )
    db.session.add(history)
    db.session.commit()

    return redirect(url_for("admin.order_detail", id=order.id))
