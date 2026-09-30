from flask import Flask, abort, jsonify, render_template, request

# Khởi tạo ứng dụng Flask
app = Flask(__name__)

# Bật hiển thị Unicode tiếng Việt cho response JSON
app.json.ensure_ascii = False  # type: ignore

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
@app.route("/")
def home():
    total_books = len(BOOKS)
    available_books = sum(1 for b in BOOKS if b["available"])
    return render_template(
        "index.html",
        total_books=total_books,
        available_books=available_books,
    )


# 3. /books : Hiển thị bảng sách, cho phép lọc ?category=...
@app.route("/books")
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
        "books.html",
        books=filtered_books,
        categories=categories,
        selected_category=selected_category,
    )


# 4. /books/<int:book_id> : Chi tiết sách, nếu không tìm thấy sẽ bắn lỗi 404
@app.route("/books/<int:book_id>")
def book_detail(book_id):
    book = find_book(book_id)
    if not book:
        abort(404, description=f"Không có sách với ID = {book_id}")
    return render_template("detail.html", book=book)


# 5. API Endpoints (Trả về định dạng JSON)
@app.route("/api/books", methods=["GET"])
def api_books():
    return jsonify(BOOKS), 200


@app.route("/api/books/<int:book_id>", methods=["GET"])
def api_book_detail(book_id):
    book = find_book(book_id)
    if not book:
        return jsonify({"error": f"Không có sách với ID = {book_id}"}), 404
    return jsonify(book), 200


# 6. Xử lý trang lỗi 404 tùy biến
@app.errorhandler(404)
def page_not_found(e):
    error_msg = getattr(e, "description", None)
    return render_template("404.html", error_message=error_msg), 404


if __name__ == "__main__":
    app.run(debug=True)
