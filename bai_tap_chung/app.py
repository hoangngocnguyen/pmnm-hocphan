from flask import Flask, jsonify, render_template
from routes.chuong03 import chuong03_bp
from routes.chuong04 import chuong04_bp, vnd_format
from routes.chuong05 import chuong05_bp
from routes.libraryms import libraryms_bp

from routes.baitapchuong3 import baitapchuong3_bp
from routes.buoi3 import buoi3_bp
from routes.buoi4 import buoi4_bp

app = Flask(__name__)
app.json.ensure_ascii = False
app.add_template_filter(vnd_format, "vnd")

# Mỗi nhóm bài tập là một blueprint độc lập, đặt dưới một tiền tố URL riêng thống nhất (chuong-03, chuong-04, chuong-05...).
app.register_blueprint(chuong03_bp, url_prefix="/chuong-03")
app.register_blueprint(chuong04_bp, url_prefix="/chuong-04")
app.register_blueprint(chuong05_bp, url_prefix="/chuong-05")
app.register_blueprint(libraryms_bp, url_prefix="/libraryms")
app.register_blueprint(baitapchuong3_bp, url_prefix="/bai-tap/thu-vien")
app.register_blueprint(buoi3_bp, url_prefix="/bai-tap")
app.register_blueprint(buoi4_bp, url_prefix="/bai-tap")


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
