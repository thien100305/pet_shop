from urllib.parse import parse_qs, urlparse

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Category, Order, Product, UserProfile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email này đã được sử dụng.")
        return email


class AdminProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("name", "description", "price", "image", "image_link", "category", "is_active")
        labels = {
            "name": "Tên sản phẩm",
            "description": "Mô tả",
            "price": "Giá bán",
            "image": "Tải ảnh lên",
            "image_link": "Hoặc URL ảnh (Google Drive / URL trực tiếp)",
            "category": "Danh mục",
            "is_active": "Đang bán",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "image_link": forms.URLInput(attrs={"placeholder": "https://..."}),
        }

    def clean_image_link(self):
        image_link = self.cleaned_data["image_link"].strip()
        parsed = urlparse(image_link)
        if parsed.hostname in {"drive.google.com", "www.drive.google.com"}:
            file_id = parse_qs(parsed.query).get("id", [""])[0]
            if not file_id:
                parts = parsed.path.strip("/").split("/")
                if len(parts) >= 3 and parts[0] == "file" and parts[1] == "d":
                    file_id = parts[2]
            if file_id:
                return f"https://drive.google.com/uc?export=view&id={file_id}"
        return image_link

    def clean(self):
        cleaned = super().clean()
        if self.files.get("image") and cleaned.get("image_link"):
            raise forms.ValidationError("Chọn tải ảnh lên hoặc nhập URL ảnh, không nhập cả hai.")
        if not self.instance.pk and not cleaned.get("image") and not cleaned.get("image_link"):
            self.add_error("image_link", "Vui lòng tải ảnh lên hoặc nhập URL ảnh.")
        return cleaned

    def save(self, commit=True):
        product = super().save(commit=False)
        if self.cleaned_data.get("image_link"):
            product.image = None
        elif self.files.get("image"):
            product.image_link = ""
        if commit:
            product.save()
            self.save_m2m()
        return product


class AdminCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name", "description")
        labels = {"name": "Tên danh mục", "description": "Mô tả"}
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}


class AdminCustomerForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active")
        labels = {
            "username": "Tên đăng nhập",
            "first_name": "Tên",
            "last_name": "Họ",
            "email": "Email",
            "is_active": "Tài khoản đang hoạt động",
        }


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=100, label="Họ và tên")
    email = forms.EmailField(label="Email")
    phone = forms.CharField(max_length=20, label="Số điện thoại")
    address = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), label="Địa chỉ nhận hàng")
    payment_method = forms.ChoiceField(choices=Order.PAYMENT_METHODS, label="Phương thức thanh toán")
    product_id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    quantity = forms.IntegerField(required=False, min_value=1, max_value=99, initial=1, widget=forms.HiddenInput)


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=False, label="Tên")
    last_name = forms.CharField(max_length=150, required=False, label="Họ")
    email = forms.EmailField(label="Email")

    class Meta:
        model = UserProfile
        fields = ("phone", "address", "city", "country", "postal_code")

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.exclude(pk=self.user.pk).filter(email__iexact=email).exists():
            raise forms.ValidationError("Email này đã được sử dụng.")
        return email

    def save(self, commit=True):
        profile = super().save(commit=False)
        self.user.first_name = self.cleaned_data["first_name"]
        self.user.last_name = self.cleaned_data["last_name"]
        self.user.email = self.cleaned_data["email"]
        if commit:
            self.user.save(update_fields=["first_name", "last_name", "email"])
            profile.save()
        return profile
