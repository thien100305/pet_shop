from django.db import migrations


PRODUCTS = [
    ("Cá cảnh nước ngọt", "Cá Betta Halfmoon đỏ xanh", "Betta Halfmoon nổi bật với bộ vây xòe rộng, màu đỏ xanh rực rỡ; thích hợp nuôi riêng trong bể nhỏ.", 180000, "products/ca-betta.png"),
    ("Cá cảnh nước ngọt", "Cá bảy màu Full Gold", "Cá bảy màu Full Gold khỏe mạnh, dễ nuôi và có sắc vàng ánh kim nổi bật trong bể thủy sinh.", 85000, "products/ca-bay-mau.png"),
    ("Cá cảnh nước ngọt", "Cá thần tiên Koi", "Cá thần tiên Koi có thân dẹt thanh lịch, hoa văn cam trắng đẹp mắt và tính cách tương đối ôn hòa.", 150000, "products/ca-than-tien.png"),
    ("Cá cảnh nước ngọt", "Cá dĩa Red Melon", "Cá dĩa Red Melon dáng tròn cân đối, sắc đỏ cam nổi bật; phù hợp với bể nước ấm được chăm sóc ổn định.", 650000, "products/ca-dia.png"),
    ("Cá cảnh nước ngọt", "Cá rồng Kim Long Quá Bối", "Cá rồng Kim Long có hàng vảy ánh vàng sang trọng, dáng bơi uyển chuyển và được tuyển chọn khỏe mạnh.", 12500000, "products/ca-rong.png"),
    ("Cá cảnh nước ngọt", "Cá Neon vua", "Cá Neon vua có dải màu xanh đỏ óng ánh, thích hợp nuôi theo đàn trong bể thủy sinh yên tĩnh.", 35000, "products/ca-neon.png"),
    ("Cá cảnh biển", "Cá hề Ocellaris", "Cá hề Ocellaris màu cam trắng đặc trưng, năng động và phù hợp với bể cá biển có hệ thống ổn định.", 320000, "products/ca-he.png"),
    ("Cá cảnh biển", "Cá đuôi gai xanh", "Cá đuôi gai xanh mang sắc xanh lam nổi bật, cần không gian bơi rộng và chế độ chăm sóc bể biển phù hợp.", 950000, "products/ca-duoi-gai-xanh.png"),
    ("Cá Koi", "Cá Koi Kohaku", "Koi Kohaku có nền trắng tinh và mảng đỏ cân đối, được tuyển chọn theo dáng bơi và chất lượng màu sắc.", 1800000, "products/ca-koi-kohaku.png"),
    ("Cá Koi", "Cá Koi Showa", "Koi Showa sở hữu ba màu đỏ, trắng, đen tương phản mạnh; phù hợp làm điểm nhấn cho hồ sân vườn.", 2200000, "products/ca-koi-showa.png"),
]


def seed_data(apps, schema_editor):
    Category = apps.get_model("accounts", "Category")
    Product = apps.get_model("accounts", "Product")
    Order = apps.get_model("accounts", "Order")
    OrderStatusHistory = apps.get_model("accounts", "OrderStatusHistory")

    categories = {}
    descriptions = {
        "Cá cảnh nước ngọt": "Các loài cá nhiều màu sắc, phù hợp bể thủy sinh và bể gia đình",
        "Cá cảnh biển": "Những loài cá biển rực rỡ dành cho hệ thống hồ nước mặn",
        "Cá Koi": "Các dòng cá Koi được tuyển chọn cho hồ sân vườn",
    }
    for name, description in descriptions.items():
        categories[name], _ = Category.objects.get_or_create(name=name, defaults={"description": description})

    for category_name, name, description, price, image in PRODUCTS:
        Product.objects.get_or_create(
            name=name,
            defaults={
                "category": categories[category_name],
                "description": description,
                "price": price,
                "image": image,
                "is_active": True,
            },
        )

    for order in Order.objects.all().iterator():
        OrderStatusHistory.objects.get_or_create(
            order=order,
            status=order.status,
            defaults={"note": "Trạng thái được chuyển từ dữ liệu đơn hàng trước đây."},
        )


class Migration(migrations.Migration):
    dependencies = [("accounts", "0010_order_tracking")]

    operations = [migrations.RunPython(seed_data, migrations.RunPython.noop)]
