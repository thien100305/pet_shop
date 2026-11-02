# PetHouse Ecommerce

Ứng dụng thương mại điện tử Django dành cho cửa hàng thú cưng, có giỏ hàng, thanh toán, quản lý đơn hàng, đánh giá sản phẩm và dashboard quản trị dùng dữ liệu thật.

## Chạy với SQL Server

1. Mở SQL Server Management Studio, mở file `sql.data` và chạy toàn bộ script.
2. Cài **Microsoft ODBC Driver 18 for SQL Server** trên máy chạy Django.
3. Tạo môi trường Python và cài thư viện:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. Sao chép `.env.example` thành `.env`, sau đó sửa `DB_PASSWORD`, `DB_HOST` và các giá trị kết nối phù hợp.
5. Tạo tài khoản quản trị và chạy dự án:

   ```powershell
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

`sql.data` đã tạo toàn bộ schema và đánh dấu các migration hiện có. Khi model thay đổi trong tương lai, chạy `python manage.py makemigrations` và `python manage.py migrate` như bình thường.

## Chạy nhanh bằng SQLite

Trong PowerShell:

```powershell
$env:DB_ENGINE='sqlite'
python manage.py migrate
python manage.py runserver
```

## Các trang chính

- `/`: cửa hàng và lọc danh mục
- `/cart/`: giỏ hàng
- `/profile/`: hồ sơ và lịch sử đơn
- `/order/<id>/`: theo dõi tiến trình, mã vận đơn và ngày giao dự kiến
- `/quan-tri/`: dashboard cho tài khoản staff
- `/admin/`: Django Admin để quản lý toàn bộ dữ liệu

Ảnh sản phẩm được lưu trong `media/products/`. Không đưa mật khẩu thật hoặc `DJANGO_SECRET_KEY` vào Git.

Migration `0011` tự động bổ sung 20 sản phẩm mẫu và không tạo trùng khi chạy lại.
