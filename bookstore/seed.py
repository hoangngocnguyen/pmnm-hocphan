from datetime import datetime, timedelta
import os
from app import create_app
from extensions import db
from models import Category, Book, Order, OrderItem, OrderStatusHistory


def seed():
    app = create_app()
    with app.app_context():
        # Tạo bảng nếu chưa có
        db.create_all()

        # Kiểm tra nếu đã có dữ liệu thì không seed trùng
        if db.session.scalar(db.select(Category).limit(1)):
            print("Dữ liệu đã tồn tại, bỏ qua seed.")
            return

        print("Đang khởi tạo dữ liệu mẫu cho Nhà sách Sông Hương...")

        # 1. Tạo Danh mục (6 danh mục theo slide bài giảng)
        cat_laptrinh = Category(name="Lập trình", description="Sách học lập trình từ cơ bản đến nâng cao.")
        cat_csdl = Category(name="Cơ sở dữ liệu", description="Hệ quản trị CSDL, thiết kế CSDL quan hệ và NoSQL.")
        cat_congcu = Category(name="Công cụ", description="Các công cụ quản lý mã nguồn, triển khai.")
        cat_mang = Category(name="Mạng", description="Mạng máy tính, an toàn thông tin và viễn thông.")
        cat_kynang = Category(name="Kỹ năng lập trình", description="Kỹ năng viết code sạch, kiến trúc phần mềm.")
        cat_thietke = Category(name="Thiết kế", description="Thiết kế UI/UX, đồ họa phần mềm.")  # 0 sách để test xóa

        db.session.add_all([cat_laptrinh, cat_csdl, cat_congcu, cat_mang, cat_kynang, cat_thietke])
        db.session.flush()

        # 2. Tạo Sách (Chuẩn theo các màn hình trong slide)
        books_data = [
            Book(
                title="Lập trình Python cơ bản",
                author="Nguyễn Văn A",
                publisher="NXB Đại học Huế",
                publication_year=2024,
                price=95000.0,
                stock=28,  # Ban đầu 30, đã trừ đơn #12 (2 cuốn) còn 28
                category_id=cat_laptrinh.id,
                description="Cuốn sách cung cấp kiến thức nền tảng về ngôn ngữ Python, từ cú pháp cơ bản, cấu trúc dữ liệu đến lập trình hướng đối tượng và xử lý tệp tin."
            ),
            Book(
                title="Giáo trình Flask",
                author="Miguel Grinberg",
                publisher="NXB Đại học Huế",
                publication_year=2023,
                price=120000.0,
                stock=19,  # Ban đầu 20, đã trừ đơn #12 (1 cuốn) còn 19
                category_id=cat_laptrinh.id,
                description="Hướng dẫn toàn diện về xây dựng ứng dụng web hiện đại với Flask framework, SQLAlchemy và Jinja2."
            ),
            Book(
                title="Cơ sở dữ liệu",
                author="Trần Văn B",
                publisher="NXB Khoa học Tự nhiên",
                publication_year=2022,
                price=85000.0,
                stock=0,  # Hết hàng để test màn hình ① và ⑦
                category_id=cat_csdl.id,
                description="Giáo trình nhập môn cơ sở dữ liệu quan hệ, đại số quan hệ và chuẩn hóa dữ liệu."
            ),
            Book(
                title="Pro Git",
                author="Scott Chacon",
                publisher="NXB Thông tin & Truyền thông",
                publication_year=2021,
                price=150000.0,
                stock=14,  # Ban đầu 15, đã trừ đơn #12 (1 cuốn) còn 14
                category_id=cat_congcu.id,
                description="Cẩm nang chuyên sâu về Git, quản lý phân nhánh, rebase và làm việc nhóm hiệu quả."
            ),
            Book(
                title="Mạng máy tính",
                author="Lê Văn C",
                publisher="NXB Đại học Quốc gia",
                publication_year=2023,
                price=110000.0,
                stock=12,
                category_id=cat_mang.id,
                description="Kiến trúc mạng TCP/IP, định tuyến, giao thức tầng ứng dụng và bảo mật kết nối mạng."
            ),
            Book(
                title="Clean Code",
                author="Robert C. Martin",
                publisher="NXB Trẻ",
                publication_year=2008,
                price=180000.0,
                stock=5,  # Sắp hết hàng (<= 5) để test Dashboard và lọc kho
                category_id=cat_kynang.id,
                description="Kinh điển về nghệ thuật viết mã nguồn rõ ràng, dễ bảo trì và tái cấu trúc code chuyên nghiệp."
            ),
            Book(
                title="Design Patterns: Mẫu thiết kế",
                author="Gang of Four",
                publisher="NXB Khoa học",
                publication_year=2020,
                price=210000.0,
                stock=8,
                category_id=cat_kynang.id,
                description="Tổng hợp 23 mẫu thiết kế phần mềm hướng đối tượng kinh điển."
            ),
            Book(
                title="Học máy cơ bản",
                author="Vũ Hữu Tiệp",
                publisher="NXB Đại học Quốc gia",
                publication_year=2022,
                price=165000.0,
                stock=10,
                category_id=cat_laptrinh.id,
                description="Giới thiệu các thuật toán Machine Learning phổ biến và ứng dụng thực tiễn với Python."
            ),
        ]

        db.session.add_all(books_data)
        db.session.flush()

        # Tạo mapping sách để gán vào đơn hàng
        python_book = books_data[0]
        flask_book = books_data[1]
        git_book = books_data[3]

        now = datetime.utcnow()

        # 3. Tạo Đơn hàng mẫu (Khớp với các màn hình trong slide)
        # Đơn #12: Nguyễn Văn An - Chờ xác nhận (460.000 đ)
        order_12 = Order(
            customer_name="Nguyễn Văn An",
            customer_phone="0912345678",
            customer_email="nguyenvanan@example.com",
            shipping_address="12 Lê Lợi, phường Thuận Hoá, Huế",
            note="Giao giờ hành chính",
            payment_method="Tiền mặt",
            shipping_fee=0.0,  # >= 200k freeship
            total_amount=460000.0,
            status=Order.STATUS_PENDING,
            created_at=now - timedelta(hours=2)
        )
        db.session.add(order_12)
        db.session.flush()

        item_12_1 = OrderItem(order_id=order_12.id, book_id=python_book.id, quantity=2, unit_price=95000.0, subtotal=190000.0)
        item_12_2 = OrderItem(order_id=order_12.id, book_id=flask_book.id, quantity=1, unit_price=120000.0, subtotal=120000.0)
        item_12_3 = OrderItem(order_id=order_12.id, book_id=git_book.id, quantity=1, unit_price=150000.0, subtotal=150000.0)
        db.session.add_all([item_12_1, item_12_2, item_12_3])

        hist_12 = OrderStatusHistory(order_id=order_12.id, status=Order.STATUS_PENDING, note="Khách hàng đặt hàng trực tuyến", created_at=now - timedelta(hours=2))
        db.session.add(hist_12)

        # Đơn #11: Trần Thị Bình - Đang giao (215.000 đ)
        order_11 = Order(
            customer_name="Trần Thị Bình",
            customer_phone="0987654321",
            shipping_address="45 Hùng Vương, phường Phú Nhuận, Huế",
            payment_method="Chuyển khoản",
            shipping_fee=0.0,
            total_amount=215000.0,
            status=Order.STATUS_SHIPPING,
            created_at=now - timedelta(days=1, hours=3)
        )
        db.session.add(order_11)
        db.session.flush()
        db.session.add(OrderStatusHistory(order_id=order_11.id, status=Order.STATUS_PENDING, note="Đặt hàng", created_at=now - timedelta(days=1, hours=3)))
        db.session.add(OrderStatusHistory(order_id=order_11.id, status=Order.STATUS_SHIPPING, note="Đã bàn giao cho đơn vị vận chuyển", created_at=now - timedelta(days=1, hours=1)))

        # Đơn #10: Lê Hoàng Cường - Hoàn tất (180.000 đ)
        order_10 = Order(
            customer_name="Lê Hoàng Cường",
            customer_phone="0901234567",
            shipping_address="88 Nguyễn Huệ, phường Vĩnh Ninh, Huế",
            payment_method="Tiền mặt",
            shipping_fee=20000.0,
            total_amount=180000.0,
            status=Order.STATUS_COMPLETED,
            created_at=now - timedelta(days=2)
        )
        db.session.add(order_10)
        db.session.flush()
        db.session.add(OrderStatusHistory(order_id=order_10.id, status=Order.STATUS_PENDING, note="Đặt hàng", created_at=now - timedelta(days=2)))
        db.session.add(OrderStatusHistory(order_id=order_10.id, status=Order.STATUS_SHIPPING, note="Đang giao", created_at=now - timedelta(days=1, hours=10)))
        db.session.add(OrderStatusHistory(order_id=order_10.id, status=Order.STATUS_COMPLETED, note="Khách đã nhận và thanh toán đủ", created_at=now - timedelta(days=1)))

        # Đơn #9: Phạm Minh Dũng - Đã huỷ (95.000 đ)
        order_9 = Order(
            customer_name="Phạm Minh Dũng",
            customer_phone="0934567890",
            shipping_address="120 Đinh Tiên Hoàng, Huế",
            payment_method="Tiền mặt",
            shipping_fee=20000.0,
            total_amount=95000.0,
            status=Order.STATUS_CANCELLED,
            created_at=now - timedelta(days=3)
        )
        db.session.add(order_9)
        db.session.flush()
        db.session.add(OrderStatusHistory(order_id=order_9.id, status=Order.STATUS_PENDING, note="Đặt hàng", created_at=now - timedelta(days=3)))
        db.session.add(OrderStatusHistory(order_id=order_9.id, status=Order.STATUS_CANCELLED, note="Khách hàng yêu cầu đổi địa chỉ nhưng sau đó huỷ đơn", created_at=now - timedelta(days=2, hours=12)))

        # Đơn #8: Hoàng Thu Hà - Chờ xác nhận (300.000 đ)
        order_8 = Order(
            customer_name="Hoàng Thu Hà",
            customer_phone="0987654321",
            shipping_address="32 Trần Hưng Đạo, Huế",
            payment_method="Tiền mặt",
            shipping_fee=0.0,
            total_amount=300000.0,
            status=Order.STATUS_PENDING,
            created_at=now - timedelta(days=1)
        )
        db.session.add(order_8)
        db.session.flush()
        db.session.add(OrderStatusHistory(order_id=order_8.id, status=Order.STATUS_PENDING, note="Đặt hàng trực tuyến", created_at=now - timedelta(days=1)))

        # Đơn #5: Võ Quốc Khánh - Chờ xác nhận (215.000 đ)
        order_5 = Order(
            customer_name="Võ Quốc Khánh",
            customer_phone="0901234567",
            shipping_address="15 Bến Nghé, Huế",
            payment_method="Chuyển khoản",
            shipping_fee=0.0,
            total_amount=215000.0,
            status=Order.STATUS_PENDING,
            created_at=now - timedelta(days=2)
        )
        db.session.add(order_5)
        db.session.flush()
        db.session.add(OrderStatusHistory(order_id=order_5.id, status=Order.STATUS_PENDING, note="Đặt hàng trực tuyến", created_at=now - timedelta(days=2)))

        # Thêm một vài đơn Hoàn tất trong 7 ngày để biểu đồ doanh thu hiển thị sinh động
        for i, amt in enumerate([250000.0, 480000.0, 320000.0, 200000.0]):
            o = Order(
                customer_name=f"Khách hàng {i+1}",
                customer_phone="0911223344",
                shipping_address="Thành phố Huế",
                payment_method="Tiền mặt",
                shipping_fee=0.0,
                total_amount=amt,
                status=Order.STATUS_COMPLETED,
                created_at=now - timedelta(days=i+1)
            )
            db.session.add(o)

        db.session.commit()
        print("✓ Khởi tạo dữ liệu mẫu thành công!")


if __name__ == '__main__':
    seed()
