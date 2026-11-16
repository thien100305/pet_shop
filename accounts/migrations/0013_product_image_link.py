from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0012_seed_more_fish_products")]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="image",
            field=models.ImageField(blank=True, upload_to="products/", verbose_name="Ảnh tải lên"),
        ),
        migrations.AddField(
            model_name="product",
            name="image_link",
            field=models.URLField(blank=True, max_length=1000, verbose_name="URL hình ảnh"),
        ),
    ]
