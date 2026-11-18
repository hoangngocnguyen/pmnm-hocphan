from datetime import UTC, datetime

from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    FloatField,
    IntegerField,
    RadioField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    NumberRange,
    Optional,
    Regexp,
)


class CheckoutForm(FlaskForm):
    customer_name = StringField(
        "Họ tên *",
        validators=[
            DataRequired(message="Vui lòng nhập họ tên người nhận."),
            Length(min=2, max=150, message="Họ tên từ 2 đến 150 ký tự."),
        ],
    )
    customer_phone = StringField(
        "Số điện thoại *",
        validators=[
            DataRequired(message="Vui lòng nhập số điện thoại."),
            Regexp(
                r"^0\d{9}$", message="Số điện thoại gồm 10 chữ số, bắt đầu bằng số 0."
            ),
        ],
    )
    customer_email = StringField(
        "Email",
        validators=[Optional(), Email(message="Địa chỉ email không đúng định dạng.")],
    )
    shipping_address = TextAreaField(
        "Địa chỉ giao hàng *",
        validators=[
            DataRequired(message="Vui lòng nhập địa chỉ nhận hàng chi tiết."),
            Length(min=5, max=255, message="Địa chỉ nhận hàng tối thiểu 5 ký tự."),
        ],
    )
    note = TextAreaField(
        "Ghi chú",
        validators=[Optional(), Length(max=500, message="Ghi chú tối đa 500 ký tự.")],
    )
    payment_method = RadioField(
        "Thanh toán *",
        choices=[
            ("Tiền mặt", "Tiền mặt khi nhận hàng"),
            ("Chuyển khoản", "Chuyển khoản"),
        ],
        default="Tiền mặt",
        validators=[DataRequired(message="Vui lòng chọn phương thức thanh toán.")],
    )
    submit = SubmitField("Xác nhận đặt hàng")


class BookForm(FlaskForm):
    title = StringField(
        "Tên sách *",
        validators=[
            DataRequired(message="Tên sách là bắt buộc."),
            Length(max=255, message="Tên sách tối đa 255 ký tự."),
        ],
    )
    author = StringField(
        "Tác giả *",
        validators=[
            DataRequired(message="Tác giả là bắt buộc."),
            Length(max=150, message="Tác giả tối đa 150 ký tự."),
        ],
    )
    publisher = StringField(
        "Nhà xuất bản",
        validators=[
            Optional(),
            Length(max=150, message="Nhà xuất bản tối đa 150 ký tự."),
        ],
    )
    category_id = SelectField(
        "Danh mục *",
        coerce=int,
        validators=[DataRequired(message="Vui lòng chọn danh mục sách.")],
    )
    publication_year = IntegerField(
        "Năm xuất bản",
        validators=[
            Optional(),
            NumberRange(
                min=1900,
                max=datetime.now(UTC).year,
                message=f"Năm xuất bản từ 1900 đến {datetime.now(UTC).year}.",
            ),
        ],
    )
    price = FloatField(
        "Giá (đồng) *",
        validators=[
            DataRequired(message="Vui lòng nhập giá sách."),
            NumberRange(min=1000, message="Giá sách phải từ 1.000 đ trở lên."),
        ],
    )
    stock = IntegerField(
        "Tồn kho *",
        validators=[
            DataRequired(message="Vui lòng nhập số lượng tồn kho."),
            NumberRange(min=0, message="Tồn kho không âm."),
        ],
    )
    description = TextAreaField("Mô tả", validators=[Optional()])
    cover_image = FileField(
        "Ảnh bìa",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png", "webp"],
                message="Chỉ hỗ trợ file ảnh JPG, PNG, WEBP.",
            )
        ],
    )
    submit = SubmitField("Lưu")


class CategoryForm(FlaskForm):
    name = StringField(
        "Tên *",
        validators=[
            DataRequired(message="Tên danh mục là bắt buộc."),
            Length(min=2, max=100, message="Tên danh mục từ 2 đến 100 ký tự."),
        ],
    )
    description = TextAreaField("Mô tả", validators=[Optional()])
    submit = SubmitField("+ Thêm")


class OrderStatusForm(FlaskForm):
    new_status = SelectField(
        "Chuyển sang *",
        validators=[DataRequired(message="Vui lòng chọn trạng thái mới.")],
    )
    note = StringField(
        "Ghi chú",
        validators=[Optional(), Length(max=255, message="Ghi chú tối đa 255 ký tự.")],
    )
    submit = SubmitField("Cập nhật")
