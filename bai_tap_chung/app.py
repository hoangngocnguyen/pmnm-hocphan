from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from routes.chuong03 import chuong03_bp
from routes.chuong04 import chuong04_bp, vnd_format
from routes.chuong05 import chuong05_bp
from routes.libraryms import libraryms_bp
from sqlalchemy import Float, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from routes.baitapchuong3 import baitapchuong3_bp
from routes.buoi3 import buoi3_bp
from routes.buoi4 import buoi4_bp


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# 3. Cấu hình cơ sở dữ liệu
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///qlsv.db"
app.config["TRACK_MODIFICATIONS"] = False

# 4. Liên kết db với ứng dụng Flask
db.init_app(app)


class Student(db.Model):

    id: Mapped[int] = mapped_column(primary_key=True)
    mssv: Mapped[str] = mapped_column(String(10), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    gpa: Mapped[float | None] = mapped_column(Float, default=0.0)

    def __repr__(self) -> str:
        return f"<Student {self.mssv} - {self.name}>"


with app.app_context():
    db.create_all()


app.json.ensure_ascii = False
app.add_template_filter(vnd_format, "vnd")

# Mỗi nhóm bài tập là một blueprint độc lập, đặt dưới một tiền tố URL riêng thống nhất (chuong-03, chuong-04, chuong-05...).
app.register_blueprint(
    chuong03_bp, url_prefix="/chuong-03"
)  # Đăng ký Blueprint và gom tất cả đường dẫn của nó vào mục /chuong-03
app.register_blueprint(chuong04_bp, url_prefix="/chuong-04")
app.register_blueprint(chuong05_bp, url_prefix="/chuong-05")
app.register_blueprint(libraryms_bp, url_prefix="/libraryms")
app.register_blueprint(baitapchuong3_bp, url_prefix="/bai-tap/thu-vien")
app.register_blueprint(buoi3_bp, url_prefix="/bai-tap")
app.register_blueprint(buoi4_bp, url_prefix="/bai-tap")


@app.get("/them-mau")
def add_sample_data():
    # Kiểm tra tổng số lượng dòng trong bảng student
    total = Student.query.count()

    if total > 0:
        return f"Bảng đã có {total} dòng dữ liệu, bỏ qua bước seed data!", 200

    # Danh sách 5 sinh viên mẫu với MSSV dạng 23T10800xx
    sample_students = [
        Student(mssv="23T1080001", name="Nguyen Van An", gpa=3.2),
        Student(mssv="23T1080002", name="Tran Thi Binh", gpa=3.6),
        Student(mssv="23T1080003", name="Le Hoang Cuong", gpa=2.8),
        Student(mssv="23T1080004", name="Pham Minh Dung", gpa=3.9),
        Student(mssv="23T1080005", name="Vo Thi Em", gpa=3.0),
    ]

    db.session.add_all(sample_students)
    db.session.commit()

    return "Đã seed thành công 5 sinh viên mới vào database!", 201


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/bai-tap/")
def assignment_home():
    return render_template("projects/bai-tap/index.html")


@app.route("/api/hello")
def hello_api():
    return jsonify({"status": "success", "message": "Hello World"})


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
