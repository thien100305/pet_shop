/*
 FishShop - SQL Server schema
 Run this entire file in SQL Server Management Studio while connected as a
 login that can create databases. The script is idempotent for FishShopDB.
 Change FishShopDB below if you also change DB_NAME in .env.
*/
IF DB_ID(N'FishShopDB') IS NULL CREATE DATABASE [FishShopDB];
GO
USE [FishShopDB];
GO

IF OBJECT_ID(N'dbo.django_migrations', N'U') IS NULL
BEGIN
CREATE TABLE dbo.django_migrations(id BIGINT IDENTITY(1,1) PRIMARY KEY, app NVARCHAR(255) NOT NULL, name NVARCHAR(255) NOT NULL, applied DATETIMEOFFSET(7) NOT NULL);
CREATE TABLE dbo.django_content_type(id INT IDENTITY(1,1) PRIMARY KEY, app_label NVARCHAR(100) NOT NULL, model NVARCHAR(100) NOT NULL, CONSTRAINT uq_content_type UNIQUE(app_label,model));
CREATE TABLE dbo.auth_permission(id INT IDENTITY(1,1) PRIMARY KEY, name NVARCHAR(255) NOT NULL, content_type_id INT NOT NULL, codename NVARCHAR(100) NOT NULL, CONSTRAINT uq_permission UNIQUE(content_type_id,codename), CONSTRAINT fk_permission_content FOREIGN KEY(content_type_id) REFERENCES dbo.django_content_type(id));
CREATE TABLE dbo.auth_group(id INT IDENTITY(1,1) PRIMARY KEY, name NVARCHAR(150) NOT NULL UNIQUE);
CREATE TABLE dbo.auth_user(id INT IDENTITY(1,1) PRIMARY KEY, password NVARCHAR(128) NOT NULL, last_login DATETIMEOFFSET(7) NULL, is_superuser BIT NOT NULL DEFAULT 0, username NVARCHAR(150) NOT NULL UNIQUE, first_name NVARCHAR(150) NOT NULL DEFAULT N'', last_name NVARCHAR(150) NOT NULL DEFAULT N'', email NVARCHAR(254) NOT NULL DEFAULT N'', is_staff BIT NOT NULL DEFAULT 0, is_active BIT NOT NULL DEFAULT 1, date_joined DATETIMEOFFSET(7) NOT NULL DEFAULT SYSDATETIMEOFFSET());
CREATE TABLE dbo.auth_group_permissions(id INT IDENTITY(1,1) PRIMARY KEY, group_id INT NOT NULL, permission_id INT NOT NULL, CONSTRAINT uq_group_permission UNIQUE(group_id,permission_id), CONSTRAINT fk_gp_group FOREIGN KEY(group_id) REFERENCES dbo.auth_group(id) ON DELETE CASCADE, CONSTRAINT fk_gp_permission FOREIGN KEY(permission_id) REFERENCES dbo.auth_permission(id) ON DELETE CASCADE);
CREATE TABLE dbo.auth_user_groups(id INT IDENTITY(1,1) PRIMARY KEY, user_id INT NOT NULL, group_id INT NOT NULL, CONSTRAINT uq_user_group UNIQUE(user_id,group_id), CONSTRAINT fk_ug_user FOREIGN KEY(user_id) REFERENCES dbo.auth_user(id) ON DELETE CASCADE, CONSTRAINT fk_ug_group FOREIGN KEY(group_id) REFERENCES dbo.auth_group(id) ON DELETE CASCADE);
CREATE TABLE dbo.auth_user_user_permissions(id INT IDENTITY(1,1) PRIMARY KEY, user_id INT NOT NULL, permission_id INT NOT NULL, CONSTRAINT uq_user_permission UNIQUE(user_id,permission_id), CONSTRAINT fk_up_user FOREIGN KEY(user_id) REFERENCES dbo.auth_user(id) ON DELETE CASCADE, CONSTRAINT fk_up_permission FOREIGN KEY(permission_id) REFERENCES dbo.auth_permission(id) ON DELETE CASCADE);
CREATE TABLE dbo.django_session(session_key NVARCHAR(40) PRIMARY KEY, session_data NVARCHAR(MAX) NOT NULL, expire_date DATETIMEOFFSET(7) NOT NULL);
CREATE INDEX ix_session_expire ON dbo.django_session(expire_date);

CREATE TABLE dbo.accounts_category(id BIGINT IDENTITY(1,1) PRIMARY KEY, name NVARCHAR(100) NOT NULL UNIQUE, description NVARCHAR(MAX) NOT NULL DEFAULT N'', created_at DATETIMEOFFSET(7) NOT NULL DEFAULT SYSDATETIMEOFFSET(), updated_at DATETIMEOFFSET(7) NOT NULL DEFAULT SYSDATETIMEOFFSET());
CREATE TABLE dbo.accounts_product(id BIGINT IDENTITY(1,1) PRIMARY KEY, name NVARCHAR(200) NOT NULL, description NVARCHAR(MAX) NOT NULL, price DECIMAL(12,0) NOT NULL, image NVARCHAR(100) NOT NULL, created_at DATETIMEOFFSET(7) NOT NULL DEFAULT SYSDATETIMEOFFSET(), updated_at DATETIMEOFFSET(7) NOT NULL DEFAULT SYSDATETIMEOFFSET(), is_active BIT NOT NULL DEFAULT 1, category_id BIGINT NOT NULL, CONSTRAINT ck_product_price CHECK(price>=0), CONSTRAINT fk_product_category FOREIGN KEY(category_id) REFERENCES dbo.accounts_category(id));
CREATE INDEX ix_product_category ON dbo.accounts_product(category_id);
CREATE TABLE dbo.accounts_cart(id BIGINT IDENTITY(1,1) PRIMARY KEY, created_at DATETIMEOFFSET(7) NOT NULL DEFAULT SYSDATETIMEOFFSET(), updated_at DATETIMEOFFSET(7) NOT NULL DEFAULT SYSDATETIMEOFFSET(), user_id INT NOT NULL UNIQUE, CONSTRAINT fk_cart_user FOREIGN KEY(user_id) REFERENCES dbo.auth_user(id) ON DELETE CASCADE);
CREATE TABLE dbo.accounts_cartitem(id BIGINT IDENTITY(1,1) PRIMARY KEY, quantity INT NOT NULL DEFAULT 1, created_at DATETIMEOFFSET(7) NOT NULL DEFAULT SYSDATETIMEOFFSET(), updated_at DATETIMEOFFSET(7) NOT NULL DEFAULT SYSDATETIMEOFFSET(), cart_id BIGINT NOT NULL, product_id BIGINT NOT NULL, CONSTRAINT ck_cart_quantity CHECK(quantity BETWEEN 1 AND 99), CONSTRAINT uq_cart_product UNIQUE(cart_id,product_id), CONSTRAINT fk_cartitem_cart FOREIGN KEY(cart_id) REFERENCES dbo.accounts_cart(id) ON DELETE CASCADE, CONSTRAINT fk_cartitem_product FOREIGN KEY(product_id) REFERENCES dbo.accounts_product(id) ON DELETE CASCADE);
CREATE INDEX ix_cartitem_product ON dbo.accounts_cartitem(product_id);
CREATE TABLE dbo.accounts_order(id BIGINT IDENTITY(1,1) PRIMARY KEY, full_name NVARCHAR(100) NOT NULL, email NVARCHAR(254) NOT NULL, phone NVARCHAR(20) NOT NULL, address NVARCHAR(MAX) NOT NULL, payment_method NVARCHAR(10) NOT NULL, total_amount DECIMAL(12,0) NOT NULL, created_at DATETIMEOFFSET(7) NOT NULL DEFAULT SYSDATETIMEOFFSET(), updated_at DATETIMEOFFSET(7) NOT NULL DEFAULT SYSDATETIMEOFFSET(), user_id INT NOT NULL, status NVARCHAR(20) NOT NULL DEFAULT N'pending', delivery_date DATE NULL, delivery_time TIME(7) NULL, is_auto_delivered BIT NOT NULL DEFAULT 0, CONSTRAINT ck_order_payment CHECK(payment_method IN(N'cod',N'bank')), CONSTRAINT ck_order_status CHECK(status IN(N'pending',N'confirmed',N'preparing',N'shipping',N'delivered',N'review',N'cancelled')), CONSTRAINT ck_order_total CHECK(total_amount>=0), CONSTRAINT fk_order_user FOREIGN KEY(user_id) REFERENCES dbo.auth_user(id));
CREATE INDEX ix_order_user ON dbo.accounts_order(user_id);
CREATE TABLE dbo.accounts_orderitem(id BIGINT IDENTITY(1,1) PRIMARY KEY, quantity INT NOT NULL, price DECIMAL(12,0) NOT NULL, created_at DATETIMEOFFSET(7) NOT NULL DEFAULT SYSDATETIMEOFFSET(), updated_at DATETIMEOFFSET(7) NOT NULL DEFAULT SYSDATETIMEOFFSET(), order_id BIGINT NOT NULL, product_id BIGINT NOT NULL, CONSTRAINT ck_orderitem_quantity CHECK(quantity>=1), CONSTRAINT ck_orderitem_price CHECK(price>=0), CONSTRAINT fk_orderitem_order FOREIGN KEY(order_id) REFERENCES dbo.accounts_order(id) ON DELETE CASCADE, CONSTRAINT fk_orderitem_product FOREIGN KEY(product_id) REFERENCES dbo.accounts_product(id));
CREATE INDEX ix_orderitem_order ON dbo.accounts_orderitem(order_id); CREATE INDEX ix_orderitem_product ON dbo.accounts_orderitem(product_id);
CREATE TABLE dbo.accounts_userprofile(id BIGINT IDENTITY(1,1) PRIMARY KEY, phone NVARCHAR(20) NOT NULL DEFAULT N'', address NVARCHAR(MAX) NOT NULL DEFAULT N'', city NVARCHAR(100) NOT NULL DEFAULT N'', country NVARCHAR(100) NOT NULL DEFAULT N'Việt Nam', postal_code NVARCHAR(20) NOT NULL DEFAULT N'', created_at DATETIMEOFFSET(7) NOT NULL DEFAULT SYSDATETIMEOFFSET(), updated_at DATETIMEOFFSET(7) NOT NULL DEFAULT SYSDATETIMEOFFSET(), user_id INT NOT NULL UNIQUE, CONSTRAINT fk_profile_user FOREIGN KEY(user_id) REFERENCES dbo.auth_user(id) ON DELETE CASCADE);
CREATE TABLE dbo.accounts_review(id BIGINT IDENTITY(1,1) PRIMARY KEY, rating INT NOT NULL, comment NVARCHAR(MAX) NOT NULL, created_at DATETIMEOFFSET(7) NOT NULL DEFAULT SYSDATETIMEOFFSET(), updated_at DATETIMEOFFSET(7) NOT NULL DEFAULT SYSDATETIMEOFFSET(), order_id BIGINT NULL, product_id BIGINT NULL, user_id INT NOT NULL, CONSTRAINT ck_review_rating CHECK(rating BETWEEN 1 AND 5), CONSTRAINT uq_review_user_product UNIQUE(user_id,product_id), CONSTRAINT fk_review_order FOREIGN KEY(order_id) REFERENCES dbo.accounts_order(id) ON DELETE CASCADE, CONSTRAINT fk_review_product FOREIGN KEY(product_id) REFERENCES dbo.accounts_product(id) ON DELETE CASCADE, CONSTRAINT fk_review_user FOREIGN KEY(user_id) REFERENCES dbo.auth_user(id) ON DELETE CASCADE);
CREATE INDEX ix_review_order ON dbo.accounts_review(order_id); CREATE INDEX ix_review_product ON dbo.accounts_review(product_id);
CREATE TABLE dbo.django_admin_log(id INT IDENTITY(1,1) PRIMARY KEY, action_time DATETIMEOFFSET(7) NOT NULL, object_id NVARCHAR(MAX) NULL, object_repr NVARCHAR(200) NOT NULL, action_flag SMALLINT NOT NULL, change_message NVARCHAR(MAX) NOT NULL, content_type_id INT NULL, user_id INT NOT NULL, CONSTRAINT fk_log_content FOREIGN KEY(content_type_id) REFERENCES dbo.django_content_type(id), CONSTRAINT fk_log_user FOREIGN KEY(user_id) REFERENCES dbo.auth_user(id) ON DELETE CASCADE);

DECLARE @now DATETIMEOFFSET(7)=SYSDATETIMEOFFSET();
INSERT dbo.django_migrations(app,name,applied) VALUES
(N'contenttypes',N'0001_initial',@now),(N'contenttypes',N'0002_remove_content_type_name',@now),
(N'auth',N'0001_initial',@now),(N'auth',N'0002_alter_permission_name_max_length',@now),(N'auth',N'0003_alter_user_email_max_length',@now),(N'auth',N'0004_alter_user_username_opts',@now),(N'auth',N'0005_alter_user_last_login_null',@now),(N'auth',N'0006_require_contenttypes_0002',@now),(N'auth',N'0007_alter_validators_add_error_messages',@now),(N'auth',N'0008_alter_user_username_max_length',@now),(N'auth',N'0009_alter_user_last_name_max_length',@now),(N'auth',N'0010_alter_group_name_max_length',@now),(N'auth',N'0011_update_proxy_permissions',@now),(N'auth',N'0012_alter_user_first_name_max_length',@now),
(N'accounts',N'0001_initial',@now),(N'accounts',N'0002_cart_cartitem_order_orderitem',@now),(N'accounts',N'0003_userprofile',@now),(N'accounts',N'0004_order_status',@now),(N'accounts',N'0005_order_delivery_date_order_delivery_time_review',@now),(N'accounts',N'0006_order_is_auto_delivered',@now),(N'accounts',N'0007_review_product_review_updated_at',@now),(N'accounts',N'0008_alter_order_status_alter_review_order',@now),(N'accounts',N'0009_alter_category_options_alter_order_options_and_more',@now),
(N'admin',N'0001_initial',@now),(N'admin',N'0002_logentry_remove_auto_add',@now),(N'admin',N'0003_logentry_add_action_flag_choices',@now),(N'sessions',N'0001_initial',@now);

INSERT dbo.accounts_category(name,description) VALUES
(N'Cá cảnh nước ngọt',N'Các loài cá nhiều màu sắc, phù hợp bể thủy sinh và bể gia đình'),
(N'Cá cảnh biển',N'Những loài cá biển rực rỡ dành cho hệ thống hồ nước mặn'),
(N'Cá Koi',N'Các dòng cá Koi được tuyển chọn cho hồ sân vườn');

INSERT dbo.accounts_product(name,description,price,image,is_active,category_id) VALUES
(N'Cá Betta Halfmoon đỏ xanh',N'Betta Halfmoon nổi bật với bộ vây xòe rộng, màu đỏ xanh rực rỡ; thích hợp nuôi riêng trong bể nhỏ.',180000,N'products/ca-betta.png',1,(SELECT id FROM dbo.accounts_category WHERE name=N'Cá cảnh nước ngọt')),
(N'Cá bảy màu Full Gold',N'Cá bảy màu Full Gold khỏe mạnh, dễ nuôi và có sắc vàng ánh kim nổi bật trong bể thủy sinh.',85000,N'products/ca-bay-mau.png',1,(SELECT id FROM dbo.accounts_category WHERE name=N'Cá cảnh nước ngọt')),
(N'Cá thần tiên Koi',N'Cá thần tiên Koi có thân dẹt thanh lịch, hoa văn cam trắng đẹp mắt và tính cách tương đối ôn hòa.',150000,N'products/ca-than-tien.png',1,(SELECT id FROM dbo.accounts_category WHERE name=N'Cá cảnh nước ngọt')),
(N'Cá dĩa Red Melon',N'Cá dĩa Red Melon dáng tròn cân đối, sắc đỏ cam nổi bật; phù hợp với bể nước ấm được chăm sóc ổn định.',650000,N'products/ca-dia.png',1,(SELECT id FROM dbo.accounts_category WHERE name=N'Cá cảnh nước ngọt')),
(N'Cá rồng Kim Long Quá Bối',N'Cá rồng Kim Long có hàng vảy ánh vàng sang trọng, dáng bơi uyển chuyển và được tuyển chọn khỏe mạnh.',12500000,N'products/ca-rong.png',1,(SELECT id FROM dbo.accounts_category WHERE name=N'Cá cảnh nước ngọt')),
(N'Cá Neon vua',N'Cá Neon vua có dải màu xanh đỏ óng ánh, thích hợp nuôi theo đàn trong bể thủy sinh yên tĩnh.',35000,N'products/ca-neon.png',1,(SELECT id FROM dbo.accounts_category WHERE name=N'Cá cảnh nước ngọt')),
(N'Cá hề Ocellaris',N'Cá hề Ocellaris màu cam trắng đặc trưng, năng động và phù hợp với bể cá biển có hệ thống ổn định.',320000,N'products/ca-he.png',1,(SELECT id FROM dbo.accounts_category WHERE name=N'Cá cảnh biển')),
(N'Cá đuôi gai xanh',N'Cá đuôi gai xanh mang sắc xanh lam nổi bật, cần không gian bơi rộng và chế độ chăm sóc bể biển phù hợp.',950000,N'products/ca-duoi-gai-xanh.png',1,(SELECT id FROM dbo.accounts_category WHERE name=N'Cá cảnh biển')),
(N'Cá Koi Kohaku',N'Koi Kohaku có nền trắng tinh và mảng đỏ cân đối, được tuyển chọn theo dáng bơi và chất lượng màu sắc.',1800000,N'products/ca-koi-kohaku.png',1,(SELECT id FROM dbo.accounts_category WHERE name=N'Cá Koi')),
(N'Cá Koi Showa',N'Koi Showa sở hữu ba màu đỏ, trắng, đen tương phản mạnh; phù hợp làm điểm nhấn cho hồ sân vườn.',2200000,N'products/ca-koi-showa.png',1,(SELECT id FROM dbo.accounts_category WHERE name=N'Cá Koi'));
END

/* Bổ sung sản phẩm theo cách idempotent: có thể chạy lại mà không tạo trùng. */
MERGE dbo.accounts_product AS target
USING (
    SELECT v.name,v.description,v.price,v.image,c.id AS category_id
    FROM (VALUES
        (N'Cá cảnh nước ngọt',N'Cá Oscar Tiger',N'Oscar Tiger có hoa văn cam đen mạnh mẽ, thông minh và phù hợp với bể lớn.',280000,N'products/ca-dia.png'),
        (N'Cá cảnh nước ngọt',N'Cá La Hán King Kamfa',N'La Hán King Kamfa có đầu gù cân đối, châu sáng và màu sắc nổi bật.',1500000,N'products/ca-rong.png'),
        (N'Cá cảnh nước ngọt',N'Cá Phượng Hoàng Bolivian',N'Cá Phượng Hoàng Bolivian hiền hòa, có ánh vàng xanh đẹp trong bể thủy sinh.',120000,N'products/ca-than-tien.png'),
        (N'Cá cảnh nước ngọt',N'Cá Cầu Vồng Boesemani',N'Cá Cầu Vồng Boesemani có hai mảng màu xanh cam đặc trưng và thích bơi theo đàn.',140000,N'products/ca-bay-mau.png'),
        (N'Cá cảnh nước ngọt',N'Cá Mún đỏ',N'Cá Mún đỏ nhỏ nhắn, khỏe mạnh, dễ nuôi và phù hợp cho người mới bắt đầu.',25000,N'products/ca-bay-mau.png'),
        (N'Cá cảnh nước ngọt',N'Cá Kiếm đỏ',N'Cá Kiếm đỏ nổi bật với phần đuôi dài hình kiếm và tính cách năng động.',35000,N'products/ca-bay-mau.png'),
        (N'Cá cảnh nước ngọt',N'Cá Sặc gấm',N'Cá Sặc gấm có màu xanh đỏ óng ánh, bơi chậm và thích bể nhiều cây.',65000,N'products/ca-betta.png'),
        (N'Cá cảnh nước ngọt',N'Cá Chuột Panda',N'Cá Chuột Panda sống tầng đáy, hiền lành và hỗ trợ làm sạch thức ăn thừa.',75000,N'products/ca-neon.png'),
        (N'Cá cảnh nước ngọt',N'Cá Pleco Hoàng Gia',N'Pleco Hoàng Gia có sọc đen trắng độc đáo và phù hợp với bể gỗ lũa.',450000,N'products/ca-rong.png'),
        (N'Cá cảnh nước ngọt',N'Cá Tetra Mũi Đỏ',N'Tetra Mũi Đỏ có phần đầu đỏ tươi, bơi đàn đẹp trong bể thủy sinh.',45000,N'products/ca-neon.png'),
        (N'Cá cảnh nước ngọt',N'Cá Tam Giác',N'Cá Tam Giác có mảng đen đặc trưng ở thân và tính cách ôn hòa.',40000,N'products/ca-neon.png'),
        (N'Cá cảnh nước ngọt',N'Cá Bút Chì',N'Cá Bút Chì ăn rêu hại hiệu quả, nhanh nhẹn và thích hợp cho bể thủy sinh.',55000,N'products/ca-neon.png'),
        (N'Cá cảnh nước ngọt',N'Cá Ranchu',N'Cá Ranchu có lưng cong mềm mại, đầu phát triển đẹp và dáng bơi đáng yêu.',350000,N'products/ca-koi-kohaku.png'),
        (N'Cá cảnh nước ngọt',N'Cá Oranda đầu lân',N'Cá Oranda nổi bật với phần đầu lân và bộ vây dài uyển chuyển.',320000,N'products/ca-koi-showa.png'),
        (N'Cá cảnh nước ngọt',N'Cá vàng Ryukin',N'Cá vàng Ryukin có lưng cao, thân ngắn và màu đỏ trắng rực rỡ.',260000,N'products/ca-koi-kohaku.png'),
        (N'Cá cảnh nước ngọt',N'Cá Thiên Đường',N'Cá Thiên Đường có vây dài, màu sắc nổi bật và khả năng thích nghi tốt.',90000,N'products/ca-betta.png'),
        (N'Cá cảnh nước ngọt',N'Cá Ali Peacock',N'Cá Ali Peacock mang sắc xanh lam óng ánh, phù hợp với bể đá phong cách Malawi.',180000,N'products/ca-dia.png'),
        (N'Cá cảnh nước ngọt',N'Cá Hồng Két',N'Cá Hồng Két có thân tròn, màu cam đỏ tươi và tính cách thân thiện.',240000,N'products/ca-dia.png'),
        (N'Cá cảnh nước ngọt',N'Cá Killi Clown',N'Cá Killi Clown nhỏ nhắn với các sọc đen vàng và chiếc đuôi nhiều màu.',110000,N'products/ca-bay-mau.png'),
        (N'Cá cảnh nước ngọt',N'Cá Ngựa Vằn',N'Cá Ngựa Vằn khỏe, bơi nhanh theo đàn và rất phù hợp cho bể cộng đồng.',20000,N'products/ca-neon.png'),
        (N'Cá cảnh nước ngọt',N'Cá Cánh Buồm',N'Cá Cánh Buồm có vây lưng cao, thân màu trang nhã và dễ chăm sóc.',45000,N'products/ca-than-tien.png'),
        (N'Cá cảnh nước ngọt',N'Cá Bống Mắt Tre',N'Cá Bống Mắt Tre có khoang vàng đen bắt mắt và thích sống gần tầng đáy.',130000,N'products/ca-neon.png'),
        (N'Cá cảnh nước ngọt',N'Cá Tai Tượng Da Beo',N'Cá Tai Tượng Da Beo có hoa văn độc đáo, khỏe mạnh và cần bể rộng.',380000,N'products/ca-dia.png'),
        (N'Cá cảnh nước ngọt',N'Cá Hắc Molly',N'Cá Hắc Molly có màu đen tuyền sang trọng, dễ nuôi và sinh sản tốt.',30000,N'products/ca-bay-mau.png'),
        (N'Cá cảnh biển',N'Cá Đuôi Gai Vàng',N'Cá Đuôi Gai Vàng có màu vàng chanh rực rỡ và giúp kiểm soát tảo trong bể biển.',1200000,N'products/ca-duoi-gai-xanh.png'),
        (N'Cá cảnh biển',N'Cá Royal Gramma',N'Royal Gramma có hai nửa tím vàng nổi bật và thích các hốc đá an toàn.',650000,N'products/ca-he.png'),
        (N'Cá cảnh biển',N'Cá Trạng Nguyên Mandarin',N'Cá Mandarin sở hữu hoa văn xanh cam như tranh vẽ và dáng bơi duyên dáng.',980000,N'products/ca-duoi-gai-xanh.png'),
        (N'Cá cảnh biển',N'Cá Cáo Foxface',N'Cá Cáo Foxface có màu vàng đen đặc trưng, ăn tảo tốt và cần bể biển rộng.',1450000,N'products/ca-duoi-gai-xanh.png'),
        (N'Cá cảnh biển',N'Cá Banggai Cardinal',N'Banggai Cardinal có sọc đen trắng và các chấm bạc thanh lịch, tính cách ôn hòa.',520000,N'products/ca-he.png'),
        (N'Cá cảnh biển',N'Cá Firefish',N'Cá Firefish có đầu vàng, thân trắng tím và thường bơi nhẹ nhàng gần hang đá.',480000,N'products/ca-he.png'),
        (N'Cá cảnh biển',N'Cá Hoàng Đế Emperor',N'Cá Hoàng Đế trưởng thành có các sọc xanh vàng sang trọng và cần bể lớn.',2800000,N'products/ca-duoi-gai-xanh.png'),
        (N'Cá cảnh biển',N'Cá Bướm Mỏ Dài',N'Cá Bướm Mỏ Dài có sọc vàng trắng tinh tế và chiếc mõm dài đặc trưng.',1650000,N'products/ca-he.png'),
        (N'Cá Koi',N'Cá Koi Taisho Sanke',N'Koi Taisho Sanke có nền trắng cùng hoa văn đỏ đen cân đối và thanh lịch.',2500000,N'products/ca-koi-kohaku.png'),
        (N'Cá Koi',N'Cá Koi Shiro Utsuri',N'Koi Shiro Utsuri nổi bật với hai màu đen trắng tương phản mạnh.',2100000,N'products/ca-koi-showa.png'),
        (N'Cá Koi',N'Cá Koi Tancho',N'Koi Tancho có chấm đỏ tròn trên đầu, biểu tượng cho vẻ đẹp tối giản.',3200000,N'products/ca-koi-kohaku.png'),
        (N'Cá Koi',N'Cá Koi Asagi',N'Koi Asagi mang lớp vảy xanh dạng lưới cùng sắc đỏ nhẹ ở bụng và vây.',1900000,N'products/ca-koi-showa.png'),
        (N'Cá Koi',N'Cá Koi Shusui',N'Koi Shusui có hàng vảy xanh đậm chạy dọc lưng và thân sáng khỏe khoắn.',2300000,N'products/ca-koi-kohaku.png'),
        (N'Cá Koi',N'Cá Koi Chagoi',N'Koi Chagoi màu nâu trà đồng nhất, lớn nhanh và nổi tiếng với tính cách thân thiện.',1700000,N'products/ca-koi-showa.png'),
        (N'Cá Koi',N'Cá Koi Yamabuki Ogon',N'Koi Yamabuki Ogon có sắc vàng kim toàn thân, tạo điểm nhấn sáng cho hồ.',2700000,N'products/ca-koi-kohaku.png'),
        (N'Cá Koi',N'Cá Koi Goshiki',N'Koi Goshiki kết hợp năm sắc độ với nền vảy tối và mảng đỏ nổi bật.',2900000,N'products/ca-koi-showa.png')
    ) AS v(category_name,name,description,price,image)
    INNER JOIN dbo.accounts_category AS c ON c.name=v.category_name
) AS source ON target.name=source.name
WHEN NOT MATCHED BY TARGET THEN
    INSERT(name,description,price,image,is_active,category_id)
    VALUES(source.name,source.description,source.price,source.image,1,source.category_id);
GO
PRINT N'FishShopDB đã sẵn sàng. Cấu hình file .env rồi chạy: python manage.py migrate';
GO
