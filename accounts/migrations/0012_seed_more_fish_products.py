from django.db import migrations


PRODUCTS = [
    ("Cá cảnh nước ngọt", "Cá Oscar Tiger", "Oscar Tiger có hoa văn cam đen mạnh mẽ, thông minh và phù hợp với bể lớn.", 280000, "products/ca-dia.png"),
    ("Cá cảnh nước ngọt", "Cá La Hán King Kamfa", "La Hán King Kamfa có đầu gù cân đối, châu sáng và màu sắc nổi bật.", 1500000, "products/ca-rong.png"),
    ("Cá cảnh nước ngọt", "Cá Phượng Hoàng Bolivian", "Cá Phượng Hoàng Bolivian hiền hòa, có ánh vàng xanh đẹp trong bể thủy sinh.", 120000, "products/ca-than-tien.png"),
    ("Cá cảnh nước ngọt", "Cá Cầu Vồng Boesemani", "Cá Cầu Vồng Boesemani có hai mảng màu xanh cam đặc trưng và thích bơi theo đàn.", 140000, "products/ca-bay-mau.png"),
    ("Cá cảnh nước ngọt", "Cá Mún đỏ", "Cá Mún đỏ nhỏ nhắn, khỏe mạnh, dễ nuôi và phù hợp cho người mới bắt đầu.", 25000, "products/ca-bay-mau.png"),
    ("Cá cảnh nước ngọt", "Cá Kiếm đỏ", "Cá Kiếm đỏ nổi bật với phần đuôi dài hình kiếm và tính cách năng động.", 35000, "products/ca-bay-mau.png"),
    ("Cá cảnh nước ngọt", "Cá Sặc gấm", "Cá Sặc gấm có màu xanh đỏ óng ánh, bơi chậm và thích bể nhiều cây.", 65000, "products/ca-betta.png"),
    ("Cá cảnh nước ngọt", "Cá Chuột Panda", "Cá Chuột Panda sống tầng đáy, hiền lành và hỗ trợ làm sạch thức ăn thừa.", 75000, "products/ca-neon.png"),
    ("Cá cảnh nước ngọt", "Cá Pleco Hoàng Gia", "Pleco Hoàng Gia có sọc đen trắng độc đáo và phù hợp với bể gỗ lũa.", 450000, "products/ca-rong.png"),
    ("Cá cảnh nước ngọt", "Cá Tetra Mũi Đỏ", "Tetra Mũi Đỏ có phần đầu đỏ tươi, bơi đàn đẹp trong bể thủy sinh.", 45000, "products/ca-neon.png"),
    ("Cá cảnh nước ngọt", "Cá Tam Giác", "Cá Tam Giác có mảng đen đặc trưng ở thân và tính cách ôn hòa.", 40000, "products/ca-neon.png"),
    ("Cá cảnh nước ngọt", "Cá Bút Chì", "Cá Bút Chì ăn rêu hại hiệu quả, nhanh nhẹn và thích hợp cho bể thủy sinh.", 55000, "products/ca-neon.png"),
    ("Cá cảnh nước ngọt", "Cá Ranchu", "Cá Ranchu có lưng cong mềm mại, đầu phát triển đẹp và dáng bơi đáng yêu.", 350000, "products/ca-koi-kohaku.png"),
    ("Cá cảnh nước ngọt", "Cá Oranda đầu lân", "Cá Oranda nổi bật với phần đầu lân và bộ vây dài uyển chuyển.", 320000, "products/ca-koi-showa.png"),
    ("Cá cảnh nước ngọt", "Cá vàng Ryukin", "Cá vàng Ryukin có lưng cao, thân ngắn và màu đỏ trắng rực rỡ.", 260000, "products/ca-koi-kohaku.png"),
    ("Cá cảnh nước ngọt", "Cá Thiên Đường", "Cá Thiên Đường có vây dài, màu sắc nổi bật và khả năng thích nghi tốt.", 90000, "products/ca-betta.png"),
    ("Cá cảnh nước ngọt", "Cá Ali Peacock", "Cá Ali Peacock mang sắc xanh lam óng ánh, phù hợp với bể đá phong cách Malawi.", 180000, "products/ca-dia.png"),
    ("Cá cảnh nước ngọt", "Cá Hồng Két", "Cá Hồng Két có thân tròn, màu cam đỏ tươi và tính cách thân thiện.", 240000, "products/ca-dia.png"),
    ("Cá cảnh nước ngọt", "Cá Killi Clown", "Cá Killi Clown nhỏ nhắn với các sọc đen vàng và chiếc đuôi nhiều màu.", 110000, "products/ca-bay-mau.png"),
    ("Cá cảnh nước ngọt", "Cá Ngựa Vằn", "Cá Ngựa Vằn khỏe, bơi nhanh theo đàn và rất phù hợp cho bể cộng đồng.", 20000, "products/ca-neon.png"),
    ("Cá cảnh nước ngọt", "Cá Cánh Buồm", "Cá Cánh Buồm có vây lưng cao, thân màu trang nhã và dễ chăm sóc.", 45000, "products/ca-than-tien.png"),
    ("Cá cảnh nước ngọt", "Cá Bống Mắt Tre", "Cá Bống Mắt Tre có khoang vàng đen bắt mắt và thích sống gần tầng đáy.", 130000, "products/ca-neon.png"),
    ("Cá cảnh nước ngọt", "Cá Tai Tượng Da Beo", "Cá Tai Tượng Da Beo có hoa văn độc đáo, khỏe mạnh và cần bể rộng.", 380000, "products/ca-dia.png"),
    ("Cá cảnh nước ngọt", "Cá Hắc Molly", "Cá Hắc Molly có màu đen tuyền sang trọng, dễ nuôi và sinh sản tốt.", 30000, "products/ca-bay-mau.png"),
    ("Cá cảnh biển", "Cá Đuôi Gai Vàng", "Cá Đuôi Gai Vàng có màu vàng chanh rực rỡ và giúp kiểm soát tảo trong bể biển.", 1200000, "products/ca-duoi-gai-xanh.png"),
    ("Cá cảnh biển", "Cá Royal Gramma", "Royal Gramma có hai nửa tím vàng nổi bật và thích các hốc đá an toàn.", 650000, "products/ca-he.png"),
    ("Cá cảnh biển", "Cá Trạng Nguyên Mandarin", "Cá Mandarin sở hữu hoa văn xanh cam như tranh vẽ và dáng bơi duyên dáng.", 980000, "products/ca-duoi-gai-xanh.png"),
    ("Cá cảnh biển", "Cá Cáo Foxface", "Cá Cáo Foxface có màu vàng đen đặc trưng, ăn tảo tốt và cần bể biển rộng.", 1450000, "products/ca-duoi-gai-xanh.png"),
    ("Cá cảnh biển", "Cá Banggai Cardinal", "Banggai Cardinal có sọc đen trắng và các chấm bạc thanh lịch, tính cách ôn hòa.", 520000, "products/ca-he.png"),
    ("Cá cảnh biển", "Cá Firefish", "Cá Firefish có đầu vàng, thân trắng tím và thường bơi nhẹ nhàng gần hang đá.", 480000, "products/ca-he.png"),
    ("Cá cảnh biển", "Cá Hoàng Đế Emperor", "Cá Hoàng Đế trưởng thành có các sọc xanh vàng sang trọng và cần bể lớn.", 2800000, "products/ca-duoi-gai-xanh.png"),
    ("Cá cảnh biển", "Cá Bướm Mỏ Dài", "Cá Bướm Mỏ Dài có sọc vàng trắng tinh tế và chiếc mõm dài đặc trưng.", 1650000, "products/ca-he.png"),
    ("Cá Koi", "Cá Koi Taisho Sanke", "Koi Taisho Sanke có nền trắng cùng hoa văn đỏ đen cân đối và thanh lịch.", 2500000, "products/ca-koi-kohaku.png"),
    ("Cá Koi", "Cá Koi Shiro Utsuri", "Koi Shiro Utsuri nổi bật với hai màu đen trắng tương phản mạnh.", 2100000, "products/ca-koi-showa.png"),
    ("Cá Koi", "Cá Koi Tancho", "Koi Tancho có chấm đỏ tròn trên đầu, biểu tượng cho vẻ đẹp tối giản.", 3200000, "products/ca-koi-kohaku.png"),
    ("Cá Koi", "Cá Koi Asagi", "Koi Asagi mang lớp vảy xanh dạng lưới cùng sắc đỏ nhẹ ở bụng và vây.", 1900000, "products/ca-koi-showa.png"),
    ("Cá Koi", "Cá Koi Shusui", "Koi Shusui có hàng vảy xanh đậm chạy dọc lưng và thân sáng khỏe khoắn.", 2300000, "products/ca-koi-kohaku.png"),
    ("Cá Koi", "Cá Koi Chagoi", "Koi Chagoi màu nâu trà đồng nhất, lớn nhanh và nổi tiếng với tính cách thân thiện.", 1700000, "products/ca-koi-showa.png"),
    ("Cá Koi", "Cá Koi Yamabuki Ogon", "Koi Yamabuki Ogon có sắc vàng kim toàn thân, tạo điểm nhấn sáng cho hồ.", 2700000, "products/ca-koi-kohaku.png"),
    ("Cá Koi", "Cá Koi Goshiki", "Koi Goshiki kết hợp năm sắc độ với nền vảy tối và mảng đỏ nổi bật.", 2900000, "products/ca-koi-showa.png"),
]


def seed_more_products(apps, schema_editor):
    Category = apps.get_model("accounts", "Category")
    Product = apps.get_model("accounts", "Product")

    categories = {category.name: category for category in Category.objects.all()}
    for category_name, name, description, price, image in PRODUCTS:
        Product.objects.update_or_create(
            name=name,
            defaults={
                "category": categories[category_name],
                "description": description,
                "price": price,
                "image": image,
                "is_active": True,
            },
        )


class Migration(migrations.Migration):
    dependencies = [("accounts", "0011_seed_products_and_order_history")]

    operations = [migrations.RunPython(seed_more_products, migrations.RunPython.noop)]
