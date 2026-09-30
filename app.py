from flask import Flask

from routes.buoi3 import buoi3_bp
from routes.buoi4 import buoi4_bp

app = Flask(__name__)


# Đăng ký blueprint vào ứng dụng
app.register_blueprint(buoi4_bp)
app.register_blueprint(buoi3_bp)


@app.route("/")
def home():
    return ""


if __name__ == "__main__":
    app.run(debug=True)
