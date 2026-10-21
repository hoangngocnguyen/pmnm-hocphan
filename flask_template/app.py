from flask import Flask, jsonify, render_template

app = Flask(__name__)


# Route 1: Trả về giao diện HTML
@app.route("/")
def home():
    return render_template("index.html")


# Route 2: Trả về dữ liệu JSON (ví dụ API)
@app.route("/api/hello")
def hello_api():
    return jsonify({"status": "success", "message": "Hello World"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
