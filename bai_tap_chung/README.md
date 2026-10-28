# Bài tập chung

Ứng dụng Flask tổng hợp các dự án trong một menu. Mỗi nhóm được đóng gói thành blueprint riêng; trang HTML dùng chung `templates/base.html`, các macro dùng chung nằm trong `templates/macros/ui.html`.

## Chạy ứng dụng

```powershell
.\.venv\Scripts\python.exe app.py
```

Hoặc cài phụ thuộc từ môi trường Python đang dùng:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Mở `http://127.0.0.1:5000/` để xem menu chính.

## Các dự án

| Menu | Đường dẫn | Nội dung |
| --- | --- | --- |
| Chương 03 | `/chuong-03/` | Sổ điểm sinh viên và API |
| Chương 04 | `/chuong-04/` | Website quán cà phê |
| Chương 05 | `/chuong-05/` | Bài tập form và dữ liệu người dùng (Máy tính, Điểm học phần, BMI) |
| LibraryMS | `/libraryms/` | Quản lý sách và API |
| Bài tập | `/bai-tap/` | Máy tính, route cơ bản và bài quản lý sách |

Trong mục Chương 05, router `/chuong-05/` dẫn tới từng bài:
- **Bài 1**: `/chuong-05/calc/` (Máy tính)
- **Bài 2**: `/chuong-05/diem-hoc-phan/` (Tính điểm học phần)
- **Bài 3**: `/chuong-05/bmi/` (Tính chỉ số BMI)

Mã nguồn ứng dụng nằm trong `routes/`; router Chương 05 và từng bài con được nhóm trong `routes/chuong05/`. Template của từng dự án được nhóm trong `templates/projects/` (`chuong-03`, `chuong-04`, `chuong-05`, `bai-tap`, `libraryms`).
