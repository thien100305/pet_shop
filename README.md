# FishShop

Ứng dụng thương mại điện tử Django dành cho cửa hàng cá cảnh. Dự án có danh mục cá, giỏ hàng, thanh toán, theo dõi đơn hàng, đánh giá và dashboard quản trị.

## Database SQLite

Ứng dụng lưu dữ liệu trong file `db.sqlite3` ở thư mục dự án. Django tạo schema bằng migration:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Khi deploy, ch?p file `db.sqlite3` n?y l?n ? ??a b?n v?ng c?a EC2 v? ??t `SQLITE_PATH` t?i file ?? (v? d? `/data/db.sqlite3`). H?y mount `/data` t? ? ??a b?n v?ng ?? d? li?u c?n nguy?n sau khi c?p nh?t ho?c t?o l?i container. Kh?ng ??a database ch?a d? li?u ng??i d?ng l?n Git.

## Các trang chính

- `/`: danh sách các loài cá và bộ lọc danh mục
- `/cart/`: giỏ hàng
- `/profile/`: hồ sơ và lịch sử đơn hàng
- `/don-hang/`: trung tâm đơn mua, tìm kiếm, lọc trạng thái, hủy đơn và mua lại
- `/order/<id>/`: theo dõi đơn hàng
- `/quan-tri/`: dashboard dành cho tài khoản staff
- `/django-admin/`: trang quản trị Django đầy đủ
- `/api/admin/`: REST API quản trị sản phẩm, danh mục, đơn hàng, khách hàng và đánh giá
- `/api/admin/dashboard/`: API thống kê doanh thu, trạng thái đơn hàng và sản phẩm bán chạy

API quản trị hỗ trợ Session Authentication và Basic Authentication, chỉ tài khoản staff/superuser mới được truy cập. Các danh sách hỗ trợ phân trang; sản phẩm, đơn hàng, khách hàng và đánh giá hỗ trợ tìm kiếm/lọc qua query string `q` cùng các bộ lọc riêng.

Ảnh sản phẩm cá nằm trong `media/products/`; ảnh banner nằm tại `ecommerce/static/images/fishshop-hero.png`.
