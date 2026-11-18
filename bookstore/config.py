import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'songhuong-bookstore-secret-key-2026-nhasachsonghuong')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'bookstore.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'books')
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}

    # Business Rules
    SHIPPING_FEE = 20000.0
    FREE_SHIPPING_THRESHOLD = 200000.0
    ITEMS_PER_PAGE_SHOP = 12
    ITEMS_PER_PAGE_ADMIN_BOOKS = 5
    ITEMS_PER_PAGE_ADMIN_ORDERS = 10
