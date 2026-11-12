from flask import Flask, render_template
from models import db

from routes import main_bp

# Khởi tạo ứng dụng Flask
app = Flask(__name__)

# Cấu hình SQLite
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///book_management.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "daymakhoabimatcuanguyenhoang12@31"

# Liên kết database với ứng dụng Flask
db.init_app(app)

# 4. Đăng ký Blueprint từ routes.py
app.register_blueprint(main_bp)


# Khởi tạo bảng trong database
with app.app_context():
    db.create_all()


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


# Chạy ứng dụng
if __name__ == "__main__":
    app.run(debug=True)
