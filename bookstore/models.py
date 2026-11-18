from datetime import datetime

from extensions import db
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Category(db.Model):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Quan hệ 1-N tới Book
    books: Mapped[list["Book"]] = relationship(
        "Book", back_populates="category", lazy="select"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        return f"<Category {self.name}>"


class Book(db.Model):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(150), nullable=False)
    publisher: Mapped[str | None] = mapped_column(String(150), nullable=True)
    publication_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image: Mapped[str | None] = mapped_column(String(255), nullable=True)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Quan hệ
    category: Mapped["Category"] = relationship("Category", back_populates="books")
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="book"
    )

    def is_in_order(self) -> bool:
        """Kiểm tra sách đã có trong bất kỳ đơn hàng nào chưa để chặn xoá"""
        return len(self.order_items) > 0

    def __repr__(self) -> str:
        return f"<Book {self.title}>"


class Order(db.Model):
    __tablename__ = "orders"

    STATUS_PENDING = "Chờ xác nhận"
    STATUS_SHIPPING = "Đang giao"
    STATUS_COMPLETED = "Hoàn tất"
    STATUS_CANCELLED = "Đã huỷ"

    STATUS_CHOICES = (
        STATUS_PENDING,
        STATUS_SHIPPING,
        STATUS_COMPLETED,
        STATUS_CANCELLED,
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(150), nullable=False)
    customer_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    customer_email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    shipping_address: Mapped[str] = mapped_column(String(255), nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    payment_method: Mapped[str] = mapped_column(
        String(50), nullable=False, default="Tiền mặt"
    )
    shipping_fee: Mapped[float] = mapped_column(Float, nullable=False, default=20000.0)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=STATUS_PENDING
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Quan hệ
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan", lazy="joined"
    )
    status_history: Mapped[list["OrderStatusHistory"]] = relationship(
        "OrderStatusHistory",
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="OrderStatusHistory.created_at.asc()",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def subtotal(self) -> float:
        """Tạm tính tiền sách chưa tính phí ship"""
        return sum(item.subtotal for item in self.items)

    def can_transition_to(self, new_status: str) -> bool:
        """Kiểm tra tính hợp lệ của luồng chuyển trạng thái"""
        transitions = {
            self.STATUS_PENDING: [self.STATUS_SHIPPING, self.STATUS_CANCELLED],
            self.STATUS_SHIPPING: [self.STATUS_COMPLETED, self.STATUS_CANCELLED],
            self.STATUS_COMPLETED: [],
            self.STATUS_CANCELLED: [],
        }
        return new_status in transitions.get(self.status, [])

    def is_terminal_status(self) -> bool:
        """Đơn đã ở trạng thái cuối cùng, không thể sửa đổi nữa"""
        return self.status in [self.STATUS_COMPLETED, self.STATUS_CANCELLED]

    def __repr__(self) -> str:
        return f"<Order #{self.id} - {self.status}>"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Quan hệ
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    book: Mapped["Book"] = relationship("Book", back_populates="order_items")

    def __repr__(self) -> str:
        return f"<OrderItem #{self.id} book={self.book_id} qty={self.quantity}>"


class OrderStatusHistory(db.Model):
    __tablename__ = "order_status_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Quan hệ
    order: Mapped["Order"] = relationship("Order", back_populates="status_history")

    def __repr__(self) -> str:
        return f"<OrderStatusHistory order={self.order_id} status='{self.status}'>"
