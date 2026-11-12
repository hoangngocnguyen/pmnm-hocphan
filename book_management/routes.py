import math

from flask import Blueprint, flash, redirect, render_template, request, url_for
from models import Book, Category, db
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError

main_bp = Blueprint("main", __name__)

PER_PAGE = 8
MAX_PRICE = 1_000_000_000
MAX_STOCK = 1_000_000


# ---------------------------------------------------------------------------
# VALIDATE
# ---------------------------------------------------------------------------
def validate_category(data, current_id=None):
    """Trả về (form, errors). form là giá trị đã trim để hiển thị lại khi lỗi."""
    form = {
        "name": data.get("name", "").strip(),
        "description": data.get("description", "").strip(),
    }
    errors = {}

    if not form["name"]:
        errors["name"] = "Tên danh mục không được để trống."
    elif len(form["name"]) > 100:
        errors["name"] = "Tên danh mục tối đa 100 ký tự."
    else:
        stmt = db.select(Category.id).where(
            func.lower(Category.name) == form["name"].lower()
        )
        if current_id:
            stmt = stmt.where(Category.id != current_id)
        if db.session.scalar(stmt):
            errors["name"] = f'Danh mục "{form["name"]}" đã tồn tại.'

    if len(form["description"]) > 500:
        errors["description"] = "Mô tả tối đa 500 ký tự."

    return form, errors


def validate_book(data):
    """Trả về (form, errors, parsed). parsed chỉ có giá trị khi không có lỗi."""
    form = {
        "title": data.get("title", "").strip(),
        "author": data.get("author", "").strip(),
        "price": data.get("price", "").strip(),
        "stock": data.get("stock", "").strip(),
        "category_id": data.get("category_id", "").strip(),
    }
    errors = {}
    parsed = {}

    # Tên sách
    if not form["title"]:
        errors["title"] = "Tên sách không được để trống."
    elif len(form["title"]) > 200:
        errors["title"] = "Tên sách tối đa 200 ký tự."
    else:
        parsed["title"] = form["title"]

    # Tác giả
    if not form["author"]:
        errors["author"] = "Tác giả không được để trống."
    elif len(form["author"]) > 100:
        errors["author"] = "Tên tác giả tối đa 100 ký tự."
    else:
        parsed["author"] = form["author"]

    # Giá
    try:
        price = float(form["price"])
        if not math.isfinite(price):
            raise ValueError
    except ValueError:
        errors["price"] = "Giá phải là một số."
    else:
        if price < 0:
            errors["price"] = "Giá không được âm."
        elif price > MAX_PRICE:
            errors["price"] = f"Giá tối đa {MAX_PRICE:,}đ."
        else:
            parsed["price"] = price

    # Tồn kho
    try:
        stock = int(form["stock"])
    except ValueError:
        errors["stock"] = "Tồn kho phải là số nguyên."
    else:
        if stock < 0:
            errors["stock"] = "Tồn kho không được âm."
        elif stock > MAX_STOCK:
            errors["stock"] = f"Tồn kho tối đa {MAX_STOCK:,}."
        else:
            parsed["stock"] = stock

    # Danh mục (phải tồn tại)
    try:
        category_id = int(form["category_id"])
    except ValueError:
        errors["category_id"] = "Vui lòng chọn danh mục."
    else:
        if db.session.get(Category, category_id) is None:
            errors["category_id"] = "Danh mục không tồn tại."
        else:
            parsed["category_id"] = category_id

    return form, errors, parsed


# ---------------------------------------------------------------------------
# 1. DASHBOARD
# ---------------------------------------------------------------------------
@main_bp.route("/")
def dashboard():
    total_categories = db.session.scalar(db.select(func.count(Category.id))) or 0
    total_books = db.session.scalar(db.select(func.count(Book.id))) or 0
    total_stock = db.session.scalar(db.select(func.coalesce(func.sum(Book.stock), 0)))

    # Số sách và tồn kho theo từng danh mục
    rows = db.session.execute(
        db.select(
            Category.id,
            Category.name,
            func.count(Book.id),
            func.coalesce(func.sum(Book.stock), 0),
        )
        .outerjoin(Book, Book.category_id == Category.id)
        .group_by(Category.id)
        .order_by(func.count(Book.id).desc(), Category.name)
    ).all()
    category_stats = [
        {"id": r[0], "name": r[1], "books": r[2], "stock": r[3]} for r in rows
    ]

    recent_books = db.session.scalars(
        db.select(Book).order_by(Book.id.desc()).limit(5)
    ).all()

    return render_template(
        "dashboard.html",
        total_categories=total_categories,
        total_books=total_books,
        total_stock=total_stock,
        category_stats=category_stats,
        max_books=max([c["books"] for c in category_stats], default=0),
        recent_books=recent_books,
    )


# ---------------------------------------------------------------------------
# 2. CRUD DANH MỤC SÁCH
# ---------------------------------------------------------------------------
@main_bp.route("/categories")
def list_categories():
    search = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)

    stmt = db.select(Category)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            or_(Category.name.ilike(like), Category.description.ilike(like))
        )
    stmt = stmt.order_by(Category.id.desc())

    pagination = db.paginate(stmt, page=page, per_page=PER_PAGE, error_out=False)
    return render_template("categories/list.html", pagination=pagination, search=search)


@main_bp.route("/categories/add", methods=["GET", "POST"])
def add_category():
    form, errors = {"name": "", "description": ""}, {}

    if request.method == "POST":
        form, errors = validate_category(request.form)
        if not errors:
            try:
                db.session.add(
                    Category(name=form["name"], description=form["description"] or None)
                )
                db.session.commit()
            except IntegrityError:  # trùng tên do hai người thêm cùng lúc
                db.session.rollback()
                errors["name"] = f'Danh mục "{form["name"]}" đã tồn tại.'
            else:
                flash("Thêm danh mục thành công!", "success")
                return redirect(url_for("main.list_categories"))

    return render_template(
        "categories/form.html", category=None, form=form, errors=errors
    )


@main_bp.route("/categories/edit/<int:id>", methods=["GET", "POST"])
def edit_category(id: int):
    category = db.get_or_404(Category, id)
    form, errors = {
        "name": category.name,
        "description": category.description or "",
    }, {}

    if request.method == "POST":
        form, errors = validate_category(request.form, current_id=id)
        if not errors:
            try:
                category.name = form["name"]
                category.description = form["description"] or None
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                errors["name"] = f'Danh mục "{form["name"]}" đã tồn tại.'
            else:
                flash("Cập nhật danh mục thành công!", "success")
                return redirect(url_for("main.list_categories"))

    return render_template(
        "categories/form.html", category=category, form=form, errors=errors
    )


@main_bp.route("/categories/delete/<int:id>", methods=["POST"])
def delete_category(id: int):
    category = db.get_or_404(Category, id)

    if category.books:
        flash(
            f'Không thể xóa danh mục "{category.name}" vì đang có {len(category.books)} cuốn sách!',
            "danger",
        )
        return redirect(url_for("main.list_categories"))

    db.session.delete(category)
    db.session.commit()
    flash(f'Đã xóa danh mục "{category.name}"!', "success")
    return redirect(url_for("main.list_categories"))


# ---------------------------------------------------------------------------
# 3. CRUD SÁCH THEO DANH MỤC
# ---------------------------------------------------------------------------
@main_bp.route("/books")
def list_books():
    category_id = request.args.get("category_id", type=int)
    search = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)

    categories = db.session.scalars(db.select(Category).order_by(Category.name)).all()
    stmt = db.select(Book)

    if category_id:
        stmt = stmt.where(Book.category_id == category_id)

    if search:
        like = f"%{search}%"
        stmt = stmt.where(or_(Book.title.ilike(like), Book.author.ilike(like)))

    stmt = stmt.order_by(Book.id.desc())
    pagination = db.paginate(stmt, page=page, per_page=PER_PAGE, error_out=False)

    return render_template(
        "books/list.html",
        pagination=pagination,
        categories=categories,
        selected_cat=category_id,
        search=search,
    )


@main_bp.route("/books/add", methods=["GET", "POST"])
def add_book():
    categories = db.session.scalars(db.select(Category).order_by(Category.name)).all()
    if not categories:
        flash("Hãy tạo ít nhất một danh mục trước khi thêm sách.", "warning")
        return redirect(url_for("main.add_category"))

    # Mở từ trang lọc theo danh mục thì chọn sẵn danh mục đó
    preselect = request.args.get("category_id", type=int)
    form = {
        "title": "",
        "author": "",
        "price": "0",
        "stock": "0",
        "category_id": str(preselect) if preselect else "",
    }
    errors = {}

    if request.method == "POST":
        form, errors, parsed = validate_book(request.form)
        if not errors:
            db.session.add(Book(**parsed))
            db.session.commit()
            flash("Thêm sách mới thành công!", "success")
            return redirect(url_for("main.list_books"))

    return render_template(
        "books/form.html", book=None, categories=categories, form=form, errors=errors
    )


@main_bp.route("/books/edit/<int:id>", methods=["GET", "POST"])
def edit_book(id: int):
    book = db.get_or_404(Book, id)
    categories = db.session.scalars(db.select(Category).order_by(Category.name)).all()
    form = {
        "title": book.title,
        "author": book.author,
        "price": f"{book.price:.0f}",
        "stock": str(book.stock),
        "category_id": str(book.category_id),
    }
    errors = {}

    if request.method == "POST":
        form, errors, parsed = validate_book(request.form)
        if not errors:
            for key, value in parsed.items():
                setattr(book, key, value)
            db.session.commit()
            flash("Cập nhật sách thành công!", "success")
            return redirect(url_for("main.list_books"))

    return render_template(
        "books/form.html", book=book, categories=categories, form=form, errors=errors
    )


@main_bp.route("/books/delete/<int:id>", methods=["POST"])
def delete_book(id: int):
    book = db.get_or_404(Book, id)
    db.session.delete(book)
    db.session.commit()
    flash("Đã xóa sách!", "success")
    return redirect(url_for("main.list_books"))
