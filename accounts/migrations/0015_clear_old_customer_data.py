
from django.db import migrations, transaction


def clear_old_customer_data(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Order = apps.get_model("accounts", "Order")

    database = schema_editor.connection.alias

    with transaction.atomic(using=database):
        # Xóa đơn hàng của tài khoản khách hàng
        Order.objects.using(database).filter(
            user__is_staff=False,
            user__is_superuser=False,
        ).delete()

        # Xóa tài khoản khách hàng, giữ lại staff và superuser
        User.objects.using(database).filter(
            is_staff=False,
            is_superuser=False,
        ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0014_order_user_set_null"),
    ]

    operations = [
        migrations.RunPython(clear_old_customer_data),
    ]
