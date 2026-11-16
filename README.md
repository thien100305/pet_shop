# FishShop

Ứng dụng thương mại điện tử Django dành cho cửa hàng cá cảnh. Dự án có danh mục cá, giỏ hàng, thanh toán, theo dõi đơn hàng, đánh giá và dashboard quản trị.

## Khởi tạo database bằng SQL Server Management Studio

1. Mở SQL Server Management Studio và kết nối bằng tài khoản có quyền tạo database.
2. Mở file `FishShop.sql`, sau đó chạy toàn bộ script. Script sẽ tạo database `FishShopDB`, schema và 50 sản phẩm cá mẫu.
3. Cài **Microsoft ODBC Driver 18 for SQL Server** trên máy chạy Django.
4. Tạo môi trường Python và cài thư viện:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

5. Sửa các giá trị `DB_HOST`, `DB_USER`, `DB_PASSWORD` trong `.env` cho đúng SQL Server của bạn. Tên database mặc định là `FishShopDB`.
6. Hoàn tất hai migration cuối, tạo tài khoản quản trị và chạy dự án:

   ```powershell
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

Dự án chỉ cấu hình Microsoft SQL Server, không còn dùng SQLite.

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

Ảnh sản phẩm cá nằm trong `media/products/`; ảnh banner nằm tại `fishshop/static/images/fishshop-hero.png`.
