from django.db import migrations


PRODUCTS = [
    ("Chó cảnh", "Chó Poodle Toy nâu đỏ", "Poodle nhỏ nhắn, thông minh, đã tiêm phòng và quen ăn hạt.", 6500000, "products/1.jpg"),
    ("Chó cảnh", "Chó Corgi Pembroke", "Corgi chân ngắn khỏe mạnh, thân thiện và phù hợp với gia đình.", 12500000, "products/2.jpg"),
    ("Chó cảnh", "Chó Golden Retriever", "Golden hiền lành, năng động, có sổ theo dõi sức khỏe.", 9800000, "products/3.jpg"),
    ("Chó cảnh", "Chó Pomeranian trắng", "Phốc sóc lông trắng dày, lanh lợi và quấn chủ.", 8900000, "products/4.jpg"),
    ("Chó cảnh", "Chó Shiba Inu vàng", "Shiba thuần chủng, nhanh nhẹn, đã được huấn luyện cơ bản.", 14500000, "products/5.jpg"),
    ("Mèo cảnh", "Mèo Anh lông dài", "Bé mèo lông dài mềm mượt, tính cách điềm tĩnh và dễ gần.", 7200000, "products/6.jpg"),
    ("Mèo cảnh", "Mèo Scottish tai cụp", "Mèo tai cụp đáng yêu, khỏe mạnh, thích nghi tốt trong căn hộ.", 6800000, "products/7.jpg"),
    ("Mèo cảnh", "Mèo Ragdoll mắt xanh", "Ragdoll hiền, bộ lông hai màu đẹp và đôi mắt xanh nổi bật.", 11000000, "products/8.jpg"),
    ("Mèo cảnh", "Mèo Bengal vân báo", "Bengal năng động với bộ lông vân báo đặc trưng.", 13500000, "products/9.jpg"),
    ("Mèo cảnh", "Mèo Munchkin chân ngắn", "Munchkin chân ngắn, vui vẻ và thân thiện với trẻ nhỏ.", 10500000, "products/10.jpg"),
    ("Phụ kiện", "Balo phi hành gia cho thú cưng", "Balo thoáng khí, cửa sổ trong suốt, phù hợp chó mèo dưới 8 kg.", 459000, "products/1.jpg"),
    ("Phụ kiện", "Đệm ngủ tròn lông mềm", "Đệm êm, giữ ấm tốt, vỏ có thể tháo giặt.", 329000, "products/2.jpg"),
    ("Phụ kiện", "Dây dắt phản quang cao cấp", "Dây dắt chắc chắn, có dải phản quang và tay cầm êm.", 189000, "products/3.jpg"),
    ("Phụ kiện", "Trụ cào móng cho mèo", "Trụ cào móng bọc sợi sisal bền, có đồ chơi treo.", 549000, "products/4.jpg"),
    ("Phụ kiện", "Bát ăn đôi chống trượt", "Bộ hai bát inox tháo rời, đế chống trượt dễ vệ sinh.", 159000, "products/5.jpg"),
    ("Thức ăn", "Hạt cho mèo trưởng thành 2 kg", "Công thức giàu đạm, hỗ trợ tiêu hóa và giảm búi lông.", 385000, "products/6.jpg"),
    ("Thức ăn", "Hạt cho chó con 3 kg", "Dinh dưỡng cân bằng giúp chó con phát triển xương và cơ bắp.", 425000, "products/7.jpg"),
    ("Thức ăn", "Pate cá ngừ cho mèo 12 hộp", "Pate cá ngừ mềm, bổ sung nước và taurine cho mèo.", 288000, "products/8.jpg"),
    ("Thức ăn", "Snack thịt gà sấy 500 g", "Thịt gà sấy ít béo, dùng làm phần thưởng khi huấn luyện.", 219000, "products/9.jpg"),
    ("Thức ăn", "Sữa dinh dưỡng cho thú cưng", "Sữa dễ tiêu hóa, bổ sung canxi cho chó mèo nhỏ.", 175000, "products/10.jpg"),
]


def seed_data(apps, schema_editor):
    Category = apps.get_model("accounts", "Category")
    Product = apps.get_model("accounts", "Product")
    Order = apps.get_model("accounts", "Order")
    OrderStatusHistory = apps.get_model("accounts", "OrderStatusHistory")

    categories = {}
    descriptions = {
        "Chó cảnh": "Những người bạn trung thành và năng động",
        "Mèo cảnh": "Những người bạn nhỏ đáng yêu",
        "Phụ kiện": "Phụ kiện chăm sóc thú cưng",
        "Thức ăn": "Dinh dưỡng phù hợp cho thú cưng",
    }
    for name, description in descriptions.items():
        categories[name], _ = Category.objects.get_or_create(name=name, defaults={"description": description})

    for category_name, name, description, price, image in PRODUCTS:
        Product.objects.get_or_create(
            name=name,
            defaults={
                "category": categories[category_name], "description": description,
                "price": price, "image": image, "is_active": True,
            },
        )

    for order in Order.objects.all().iterator():
        OrderStatusHistory.objects.get_or_create(
            order=order, status=order.status,
            defaults={"note": "Trạng thái được chuyển từ dữ liệu đơn hàng trước đây."},
        )


class Migration(migrations.Migration):
    dependencies = [("accounts", "0010_order_tracking")]

    operations = [migrations.RunPython(seed_data, migrations.RunPython.noop)]
