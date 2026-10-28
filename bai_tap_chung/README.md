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
| Chương 4 | `/chuong-4/` | Website quán cà phê |
| Chương 5 | `/chuong5/` | Bài tập form, tính điểm học phần và BMI |
| LibraryMS | `/libraryms/` | Quản lý sách và API |
| Bài tập | `/bai-tap/` | Máy tính, route cơ bản và bài quản lý sách |

Trong mục Chương 5, router `/chuong5/` dẫn tới từng bài: `/chuong5/diem-hoc-phan/` và `/chuong5/bmi/`.

Mã nguồn ứng dụng nằm trong `routes/`; router Chương 5 và từng bài con được nhóm trong `routes/chuong5/`. Template của từng dự án được nhóm trong `templates/projects/`.
