from flask import Blueprint, abort, jsonify, render_template, request

# Khởi tạo ứng dụng Flask
libraryms_bp = Blueprint("libraryms", __name__)

# 1. Danh sách BOOKS (≥ 4 cuốn)
BOOKS = [
    {
        "id": 1,
        "title": "Lập Trình Python Cơ Bản",
        "author": "Nguyễn Văn A",
        "year": 2023,
        "category": "Lập trình",
        "available": True,
    },
    {
        "id": 2,
        "title": "Cấu Trúc Dữ Liệu và Giải Thuật",
        "author": "Trần Thị B",
        "year": 2022,
        "category": "Lập trình",
        "available": False,
    },
    {
        "id": 3,
        "title": "Lịch Sử Văn Minh Thế Giới",
        "author": "Lê Văn C",
        "year": 2020,
        "category": "Lịch sử",
        "available": True,
    },
    {
        "id": 4,
        "title": "Kinh Tế Học Vi Mô",
        "author": "Phạm Văn D",
        "year": 2021,
        "category": "Kinh tế",
        "available": True,
    },
]


def find_book(book_id):
    """Hàm bổ trợ tìm sách theo id."""
    return next((book for book in BOOKS if book["id"] == book_id), None)


# 2. Trang chủ (/): Thống kê tổng số sách và số sách sẵn sàng cho mượn
@libraryms_bp.route("/")
def home():
    total_books = len(BOOKS)
    available_books = sum(1 for b in BOOKS if b["available"])
    return render_template(
        "projects/libraryms/index.html",
        total_books=total_books,
        available_books=available_books,
    )


# 3. /books : Hiển thị bảng sách, cho phép lọc ?category=...
@libraryms_bp.route("/books")
def book_list():
    selected_category = request.args.get("category", "").strip()

    # Lấy danh sách thể loại duy nhất (Sử dụng Set Comprehension)
    categories = list({b["category"] for b in BOOKS})

    if selected_category:
        filtered_books = [
            b for b in BOOKS if b["category"].lower() == selected_category.lower()
        ]
    else:
        filtered_books = BOOKS

    return render_template(
        "projects/libraryms/books.html",
        books=filtered_books,
        categories=categories,
        selected_category=selected_category,
    )


# 4. /books/<int:book_id> : Chi tiết sách, nếu không tìm thấy sẽ bắn lỗi 404
@libraryms_bp.route("/books/<int:book_id>")
def book_detail(book_id):
    book = find_book(book_id)
    if not book:
        abort(404, description=f"Không có sách với ID = {book_id}")
    return render_template("projects/libraryms/detail.html", book=book)


# 5. API Endpoints (Trả về định dạng JSON)
@libraryms_bp.route("/api/books", methods=["GET"])
def api_books():
    return jsonify(BOOKS), 200


@libraryms_bp.route("/api/books/<int:book_id>", methods=["GET"])
def api_book_detail(book_id):
    book = find_book(book_id)
    if not book:
        return jsonify({"error": f"Không có sách với ID = {book_id}"}), 404
    return jsonify(book), 200


# 6. Xử lý trang lỗi 404 tùy biến
@libraryms_bp.errorhandler(404)
def page_not_found(e):
    error_msg = getattr(e, "description", None)
    return render_template("projects/libraryms/404.html", error_message=error_msg), 404


