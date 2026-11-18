import os

from config import Config
from extensions import csrf, db, migrate
from flask import Flask, render_template, session
from models import Order
from routes.admin import admin_bp
from routes.shop import shop_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Đảm bảo các thư mục cần thiết tồn tại
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

    # Khởi tạo extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Đăng ký Blueprints
    app.register_blueprint(shop_bp)  # Prefix: / (Khách hàng)
    app.register_blueprint(admin_bp, url_prefix="/admin")  # Prefix: /admin (Quản trị)

    # Helper lọc query params cho phân trang đưa vào jinja globals
    def filtered_args(args_dict, exclude_key="page"):
        if hasattr(args_dict, "to_dict"):
            d = args_dict.to_dict(flat=True)
        else:
            d = dict(args_dict)
        d.pop(exclude_key, None)
        return d

    app.jinja_env.globals["filtered_args"] = filtered_args

    # Context Processors toàn cục
    @app.context_processor
    def inject_global_data():
        # 1. Tổng số lượng sách trong giỏ hàng từ Session (Badge cam)
        cart = session.get("cart", {})
        total_cart_items = sum(cart.values()) if isinstance(cart, dict) else 0

        # 2. Số đơn hàng Chờ xác nhận (Badge cam menu Admin)
        try:
            pending_orders_count = Order.query.filter_by(status="Chờ xác nhận").count()
        except Exception:
            pending_orders_count = 0

        return {
            "total_cart_items": total_cart_items,
            "pending_orders_count": pending_orders_count,
        }

    # Custom Jinja2 Filter: format tiền tệ VNĐ
    @app.template_filter("vnd")
    def format_vnd(amount):
        if amount is None:
            return "0 đ"
        try:
            return f"{int(amount):,} đ".replace(",", ".")
        except (ValueError, TypeError):
            return f"{amount} đ"

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    return app


app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
