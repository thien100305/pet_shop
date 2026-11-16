from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "output" / "report"
OUT_DIR = ROOT / "output" / "presentation"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "FishShop_LeThanhThien_ST23D_105693.pptx"

NAVY = RGBColor(8, 37, 59)
NAVY_2 = RGBColor(13, 58, 82)
TEAL = RGBColor(0, 153, 153)
TEAL_DARK = RGBColor(0, 112, 121)
CYAN = RGBColor(54, 211, 205)
ORANGE = RGBColor(255, 154, 61)
RED = RGBColor(224, 77, 77)
GREEN = RGBColor(40, 167, 105)
WHITE = RGBColor(255, 255, 255)
INK = RGBColor(28, 44, 54)
MUTED = RGBColor(91, 111, 123)
LIGHT = RGBColor(241, 247, 248)
PALE = RGBColor(222, 241, 241)
LINE = RGBColor(206, 222, 225)

prs = Presentation()
prs.slide_width = Inches(13.333333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def rect(slide, x, y, w, h, fill, radius=False, line=None, line_width=1):
    shape_type = MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE if radius else MSO_AUTO_SHAPE_TYPE.RECTANGLE
    shp = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    shp.line.color.rgb = line if line else fill
    shp.line.width = Pt(line_width)
    return shp


def text_box(slide, text, x, y, w, h, size=18, color=INK, bold=False,
             font="Aptos", align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP,
             margin=0.04, linesp=1.0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    p.line_spacing = linesp
    run = p.runs[0]
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return box


def rich_text(slide, runs, x, y, w, h, size=18, color=INK, align=PP_ALIGN.LEFT,
              valign=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    for value, bold, run_color in runs:
        r = p.add_run()
        r.text = value
        r.font.name = "Aptos"
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = run_color or color
    return box


def bullet_list(slide, items, x, y, w, h, size=18, color=INK, bullet_color=TEAL,
                gap=9, level_indent=0.25):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    for idx, item in enumerate(items):
        if isinstance(item, tuple):
            lead, rest = item
        else:
            lead, rest = "", item
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.text = ""
        p.space_after = Pt(gap)
        p.level = 0
        p.margin_left = Inches(level_indent)
        p.first_line_indent = Inches(-0.2)
        r = p.add_run()
        r.text = "● "
        r.font.name = "Aptos"
        r.font.size = Pt(max(size - 3, 10))
        r.font.color.rgb = bullet_color
        if lead:
            r = p.add_run()
            r.text = lead
            r.font.name = "Aptos"
            r.font.size = Pt(size)
            r.font.bold = True
            r.font.color.rgb = color
        r = p.add_run()
        r.text = rest
        r.font.name = "Aptos"
        r.font.size = Pt(size)
        r.font.color.rgb = color
    return box


def add_image_cover(slide, path, x, y, w, h, crop_focus_y=0.5, border=True):
    path = Path(path)
    with Image.open(path) as im:
        iw, ih = im.size
    frame_ratio = w / h
    image_ratio = iw / ih
    pic = slide.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(w), height=Inches(h))
    if image_ratio > frame_ratio:
        visible = frame_ratio / image_ratio
        pic.crop_left = pic.crop_right = (1 - visible) / 2
    else:
        visible = image_ratio / frame_ratio
        excess = 1 - visible
        pic.crop_top = max(0, min(excess, excess * crop_focus_y))
        pic.crop_bottom = excess - pic.crop_top
    if border:
        pic.line.color.rgb = LINE
        pic.line.width = Pt(1)
    return pic


def add_footer(slide, number, section="FISHSHOP"):
    rect(slide, 0, 7.28, 13.333, 0.22, NAVY)
    text_box(slide, section, 0.42, 7.30, 2.3, 0.13, size=8, color=CYAN, bold=True,
             valign=MSO_ANCHOR.MIDDLE)
    text_box(slide, f"{number:02d}", 12.35, 7.29, 0.45, 0.14, size=9, color=WHITE,
             bold=True, align=PP_ALIGN.RIGHT, valign=MSO_ANCHOR.MIDDLE)


def new_slide(title, number, kicker=None, dark=False):
    slide = prs.slides.add_slide(BLANK)
    rect(slide, 0, 0, 13.333, 7.5, NAVY if dark else WHITE)
    if not dark:
        rect(slide, 0, 0, 0.12, 7.28, TEAL)
    if kicker:
        text_box(slide, kicker.upper(), 0.55, 0.34, 5.0, 0.25, size=10,
                 color=CYAN if dark else TEAL, bold=True)
    text_box(slide, title, 0.55, 0.66, 12.0, 0.62, size=28,
             color=WHITE if dark else NAVY, bold=True, valign=MSO_ANCHOR.MIDDLE)
    if not dark:
        rect(slide, 0.55, 1.34, 1.15, 0.055, TEAL)
    add_footer(slide, number)
    return slide


def pill(slide, label, x, y, w, fill=PALE, color=TEAL_DARK):
    rect(slide, x, y, w, 0.34, fill, radius=True)
    text_box(slide, label, x, y + 0.01, w, 0.29, size=10, color=color, bold=True,
             align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)


def metric_card(slide, value, label, x, y, w, color=TEAL):
    rect(slide, x, y, w, 1.15, WHITE, radius=True, line=LINE)
    rect(slide, x, y, 0.08, 1.15, color, radius=True)
    text_box(slide, value, x + 0.28, y + 0.16, w - 0.42, 0.46, size=26, color=NAVY, bold=True)
    text_box(slide, label, x + 0.28, y + 0.68, w - 0.42, 0.25, size=11, color=MUTED)


def card(slide, title, body, x, y, w, h, accent=TEAL, number=None):
    rect(slide, x, y, w, h, WHITE, radius=True, line=LINE)
    rect(slide, x, y, w, 0.07, accent, radius=True)
    if number:
        rect(slide, x + 0.25, y + 0.27, 0.46, 0.46, accent, radius=True)
        text_box(slide, number, x + 0.25, y + 0.28, 0.46, 0.38, size=14, color=WHITE,
                 bold=True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
        tx = x + 0.86
    else:
        tx = x + 0.27
    text_box(slide, title, tx, y + 0.25, w - (tx - x) - 0.25, 0.38, size=16, color=NAVY, bold=True)
    text_box(slide, body, x + 0.27, y + 0.83, w - 0.54, h - 1.0, size=12.5, color=MUTED,
             linesp=1.05)


def arrow(slide, x1, y1, x2, y2, color=TEAL, width=2.5):
    ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    ln.line.color.rgb = color
    ln.line.width = Pt(width)
    ln.line.end_arrowhead = True
    return ln


# 01 — Cover
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.333, 7.5, NAVY)
rect(slide, 0, 0, 0.15, 7.5, CYAN)
add_image_cover(slide, ASSET_DIR / "home.png", 7.72, 0, 5.613, 7.5, crop_focus_y=0.12, border=False)
overlay = rect(slide, 7.72, 0, 5.613, 7.5, NAVY)
overlay.fill.transparency = 22
slide.shapes.add_picture(str(ASSET_DIR / "uda-logo.png"), Inches(0.65), Inches(0.55), width=Inches(2.1))
pill(slide, "BÁO CÁO ĐỒ ÁN PYTHON 2", 0.68, 1.62, 2.35, fill=TEAL, color=WHITE)
text_box(slide, "FISHSHOP", 0.67, 2.15, 6.35, 0.78, size=42, color=WHITE, bold=True)
text_box(slide, "Website thương mại điện tử\nkinh doanh cá cảnh", 0.70, 3.04, 5.85, 1.15,
         size=25, color=CYAN, bold=True)
rect(slide, 0.70, 4.52, 5.95, 0.02, RGBColor(72, 105, 122))
rich_text(slide, [("Sinh viên: ", True, CYAN), ("Lê Thanh Thiên", False, WHITE)],
          0.70, 4.82, 5.3, 0.35, size=16)
rich_text(slide, [("Lớp: ", True, CYAN), ("ST23D", False, WHITE),
                  ("   |   MSSV: ", True, CYAN), ("105693", False, WHITE)],
          0.70, 5.25, 5.3, 0.35, size=16)
text_box(slide, "Đà Nẵng · 2026", 0.70, 6.56, 3.0, 0.28, size=11, color=RGBColor(172, 195, 205))
text_box(slide, "01", 12.35, 7.15, 0.45, 0.16, size=9, color=WHITE, bold=True, align=PP_ALIGN.RIGHT)

# 02 — Story
slide = new_slide("Bài toán và mục tiêu của FishShop", 2, "01 · Tổng quan")
card(slide, "Bài toán", "Người mua cần một nơi xem thông tin cá cảnh rõ ràng, đặt hàng nhanh và theo dõi được toàn bộ tiến trình giao hàng.", 0.62, 1.72, 3.83, 2.05, RED, "1")
card(slide, "Giải pháp", "FishShop số hóa quy trình từ tìm kiếm sản phẩm, giỏ hàng, đặt hàng đến cập nhật trạng thái và đánh giá sau mua.", 4.74, 1.72, 3.83, 2.05, TEAL, "2")
card(slide, "Mục tiêu", "Xây dựng hệ thống Django hoàn chỉnh, dữ liệu tập trung trên SQL Server và có trang quản trị cùng REST API.", 8.86, 1.72, 3.83, 2.05, ORANGE, "3")
text_box(slide, "Giá trị cốt lõi", 0.72, 4.18, 2.0, 0.35, size=18, color=NAVY, bold=True)
bullet_list(slide, [
    ("Đối với khách hàng: ", "trải nghiệm mua sắm trực quan, minh bạch trạng thái đơn hàng."),
    ("Đối với quản trị viên: ", "quản lý tập trung sản phẩm, danh mục và vòng đời đơn hàng."),
    ("Đối với hệ thống: ", "dễ mở rộng nhờ mô hình Django MVT và API tách biệt."),
], 0.72, 4.66, 11.75, 1.7, size=17, gap=12)

# 03 — Scope
slide = new_slide("Phạm vi chức năng và đối tượng sử dụng", 3, "01 · Tổng quan")
rect(slide, 0.67, 1.7, 5.92, 4.85, LIGHT, radius=True, line=LINE)
rect(slide, 6.88, 1.7, 5.78, 4.85, LIGHT, radius=True, line=LINE)
pill(slide, "KHÁCH HÀNG", 0.99, 2.02, 1.55, fill=TEAL, color=WHITE)
text_box(slide, "Mua sắm và hậu mãi", 0.99, 2.54, 4.8, 0.42, size=22, color=NAVY, bold=True)
bullet_list(slide, ["Đăng ký, đăng nhập, cập nhật hồ sơ", "Tìm kiếm và xem chi tiết sản phẩm", "Quản lý giỏ hàng, đặt hàng COD/chuyển khoản", "Tra cứu, lọc, hủy và mua lại đơn hàng", "Theo dõi vận đơn, xác nhận đã nhận, đánh giá"], 1.0, 3.18, 5.1, 2.85, size=15.5, gap=8)
pill(slide, "QUẢN TRỊ VIÊN", 7.20, 2.02, 1.82, fill=ORANGE, color=WHITE)
text_box(slide, "Điều hành cửa hàng", 7.20, 2.54, 4.8, 0.42, size=22, color=NAVY, bold=True)
bullet_list(slide, ["Dashboard tổng hợp số liệu kinh doanh", "CRUD sản phẩm và danh mục cá", "Kiểm soát chuyển trạng thái đơn hợp lệ", "Tạo mã vận đơn, ngày giao dự kiến, ghi chú", "Quản trị qua giao diện web và REST API"], 7.21, 3.18, 5.0, 2.85, size=15.5, gap=8, bullet_color=ORANGE)

# 04 — Stack
slide = new_slide("Công nghệ sử dụng", 4, "02 · Nền tảng")
stack = [
    ("Python + Django", "Xử lý nghiệp vụ theo mô hình MVT", TEAL),
    ("Django REST Framework", "Xây dựng API cho khối quản trị", CYAN),
    ("Microsoft SQL Server", "Lưu trữ dữ liệu quan hệ tập trung", ORANGE),
    ("HTML · CSS · JavaScript", "Giao diện đáp ứng và tương tác người dùng", GREEN),
    ("ODBC Driver 18", "Kết nối Django với SQL Server", RED),
    ("WhiteNoise", "Phục vụ static file khi triển khai", NAVY_2),
]
for i, (name, desc, accent) in enumerate(stack):
    col, row = i % 3, i // 3
    x, y = 0.68 + col * 4.18, 1.72 + row * 2.22
    rect(slide, x, y, 3.82, 1.82, WHITE, radius=True, line=LINE)
    rect(slide, x + 0.24, y + 0.28, 0.16, 1.18, accent, radius=True)
    text_box(slide, name, x + 0.62, y + 0.29, 2.9, 0.42, size=17, color=NAVY, bold=True)
    text_box(slide, desc, x + 0.62, y + 0.84, 2.88, 0.64, size=12.5, color=MUTED)
text_box(slide, "Lựa chọn phù hợp với yêu cầu: phát triển nhanh, dữ liệu nhất quán và dễ bảo trì.", 0.76, 6.34, 11.8, 0.36, size=15, color=TEAL_DARK, bold=True, align=PP_ALIGN.CENTER)

# 05 — Architecture
slide = new_slide("Kiến trúc tổng thể của hệ thống", 5, "02 · Thiết kế hệ thống")
layers = [
    ("NGƯỜI DÙNG", "Trình duyệt · Desktop / Mobile", 0.74, 1.76, TEAL),
    ("GIAO DIỆN", "Django Templates · HTML · CSS · JS", 3.18, 1.76, CYAN),
    ("ỨNG DỤNG", "Views · Models · Business Rules · DRF API", 5.62, 1.76, ORANGE),
    ("DỮ LIỆU", "SQL Server · Media files · Static files", 8.06, 1.76, GREEN),
]
for title, body, x, y, accent in layers:
    rect(slide, x, y, 2.12, 1.55, WHITE, radius=True, line=accent, line_width=2)
    rect(slide, x, y, 2.12, 0.44, accent, radius=True)
    text_box(slide, title, x, y + 0.04, 2.12, 0.28, size=11, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    text_box(slide, body, x + 0.18, y + 0.68, 1.76, 0.6, size=12, color=INK, align=PP_ALIGN.CENTER)
for x in (2.91, 5.35, 7.79):
    arrow(slide, x, 2.54, x + 0.24, 2.54)
rect(slide, 10.76, 1.76, 1.82, 1.55, NAVY, radius=True)
text_box(slide, "QUẢN TRỊ", 10.76, 1.93, 1.82, 0.3, size=11, color=CYAN, bold=True, align=PP_ALIGN.CENTER)
text_box(slide, "Web Admin\n+ REST API", 10.92, 2.43, 1.5, 0.52, size=12, color=WHITE, align=PP_ALIGN.CENTER)
arrow(slide, 10.73, 2.54, 10.50, 2.54, ORANGE)
text_box(slide, "Nguyên tắc xử lý", 0.76, 4.06, 2.1, 0.35, size=18, color=NAVY, bold=True)
bullet_list(slide, [
    ("Request/Response: ", "URL định tuyến đến View, View xử lý nghiệp vụ và trả Template hoặc JSON."),
    ("Dữ liệu: ", "ORM ánh xạ các model sang bảng trong SQL Server; migration quản lý thay đổi cấu trúc."),
    ("Tài nguyên: ", "ảnh sản phẩm lưu trong media; CSS/JS và ảnh giao diện nằm trong static."),
], 0.76, 4.52, 11.5, 1.72, size=15.5, gap=10)

# 06 — Data model
slide = new_slide("Mô hình dữ liệu chính", 6, "02 · Thiết kế hệ thống")
entities = [
    ("User", "Tài khoản", 0.55, 1.63, TEAL),
    ("UserProfile", "Thông tin giao hàng", 0.55, 3.02, CYAN),
    ("Cart", "Giỏ hàng", 3.05, 1.63, TEAL),
    ("CartItem", "Dòng giỏ hàng", 3.05, 3.02, CYAN),
    ("Category", "Danh mục", 5.55, 1.63, ORANGE),
    ("Product", "Cá cảnh", 5.55, 3.02, ORANGE),
    ("Order", "Đơn hàng", 8.05, 1.63, GREEN),
    ("OrderItem", "Chi tiết đơn", 8.05, 3.02, GREEN),
    ("OrderStatusHistory", "Lịch sử trạng thái", 10.55, 1.63, RED),
    ("Review", "Đánh giá", 10.55, 3.02, RED),
]
for name, label, x, y, accent in entities:
    rect(slide, x, y, 2.18, 0.96, WHITE, radius=True, line=accent, line_width=1.5)
    text_box(slide, name, x + 0.12, y + 0.16, 1.94, 0.25, size=12.5, color=NAVY, bold=True, align=PP_ALIGN.CENTER)
    text_box(slide, label, x + 0.12, y + 0.54, 1.94, 0.2, size=10.5, color=MUTED, align=PP_ALIGN.CENTER)
for x1, y1, x2, y2 in [(1.64,2.59,1.64,3.01),(2.73,2.11,3.04,2.11),(4.14,2.59,4.14,3.01),(5.23,3.49,5.54,3.49),(6.64,2.59,6.64,3.01),(7.73,3.49,8.04,3.49),(9.14,2.59,9.14,3.01),(10.23,2.11,10.54,2.11),(10.23,3.49,10.54,3.49)]:
    arrow(slide, x1, y1, x2, y2, MUTED, 1.5)
text_box(slide, "Quan hệ nổi bật", 0.65, 4.48, 2.0, 0.35, size=17, color=NAVY, bold=True)
bullet_list(slide, ["Một người dùng có một giỏ hàng và nhiều đơn hàng.", "Một danh mục có nhiều sản phẩm; sản phẩm được bảo vệ khi đã phát sinh đơn.", "Mỗi lần đổi trạng thái đơn đều được ghi lịch sử để truy vết.", "Mỗi khách chỉ đánh giá một lần cho mỗi sản phẩm."], 0.66, 4.89, 12.0, 1.55, size=14.5, gap=6)

# 07 — Dataset
slide = new_slide("Dữ liệu sản phẩm cá cảnh", 7, "03 · Kết quả triển khai")
metric_card(slide, "50", "sản phẩm khác nhau", 0.70, 1.70, 2.72, TEAL)
metric_card(slide, "30", "cá nước ngọt", 3.65, 1.70, 2.72, CYAN)
metric_card(slide, "10", "cá biển", 6.60, 1.70, 2.72, ORANGE)
metric_card(slide, "10", "cá Koi", 9.55, 1.70, 2.72, GREEN)
add_image_cover(slide, ASSET_DIR / "home.png", 0.70, 3.23, 7.28, 3.43, crop_focus_y=0.17)
text_box(slide, "Dữ liệu được chuẩn hóa", 8.35, 3.30, 3.8, 0.38, size=20, color=NAVY, bold=True)
bullet_list(slide, ["Tên, mô tả và giá bán riêng biệt", "Hình ảnh phù hợp từng loài cá", "Phân loại theo ba nhóm rõ ràng", "Có trạng thái đang bán/ngừng bán", "Script SQL có thể chạy trong SSMS"], 8.35, 3.86, 4.0, 2.2, size=15, gap=9)
pill(slide, "Nguồn dữ liệu: FishShopDB", 8.36, 6.17, 2.55, fill=PALE, color=TEAL_DARK)

# 08 — Customer flow
slide = new_slide("Hành trình mua hàng của khách", 8, "03 · Chức năng khách hàng")
steps = [
    ("1", "Khám phá", "Trang chủ\nTìm kiếm"),
    ("2", "Chọn cá", "Chi tiết\nGiá & mô tả"),
    ("3", "Giỏ hàng", "Số lượng\nTạm tính"),
    ("4", "Đặt hàng", "Địa chỉ\nThanh toán"),
    ("5", "Theo dõi", "Mã vận đơn\nLịch sử"),
    ("6", "Hậu mãi", "Nhận hàng\nĐánh giá"),
]
for i, (num, title, body) in enumerate(steps):
    x = 0.55 + i * 2.1
    rect(slide, x, 2.02, 1.72, 2.34, WHITE, radius=True, line=LINE)
    rect(slide, x + 0.51, 1.65, 0.70, 0.70, TEAL if i < 4 else ORANGE, radius=True)
    text_box(slide, num, x + 0.51, 1.75, 0.70, 0.38, size=20, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    text_box(slide, title, x + 0.12, 2.62, 1.48, 0.35, size=15, color=NAVY, bold=True, align=PP_ALIGN.CENTER)
    text_box(slide, body, x + 0.15, 3.26, 1.42, 0.55, size=12, color=MUTED, align=PP_ALIGN.CENTER)
    if i < len(steps) - 1:
        arrow(slide, x + 1.77, 3.15, x + 2.03, 3.15, TEAL, 2)
rect(slide, 0.78, 5.08, 11.77, 1.12, LIGHT, radius=True, line=LINE)
text_box(slide, "Điểm khác biệt", 1.04, 5.32, 1.75, 0.3, size=16, color=TEAL_DARK, bold=True)
text_box(slide, "Khách hàng không chỉ đặt mua mà còn chủ động hủy đơn đang chờ, mua lại, xác nhận đã nhận và xem toàn bộ dòng thời gian vận chuyển.", 2.87, 5.24, 9.25, 0.56, size=15, color=INK, valign=MSO_ANCHOR.MIDDLE)

# 09 — UI
slide = new_slide("Giao diện mua sắm trực quan", 9, "03 · Chức năng khách hàng")
add_image_cover(slide, ASSET_DIR / "home.png", 0.67, 1.58, 6.05, 4.85, crop_focus_y=0.15)
add_image_cover(slide, ASSET_DIR / "product.png", 7.02, 1.58, 5.63, 4.85, crop_focus_y=0.15)
pill(slide, "TRANG CHỦ", 0.91, 5.91, 1.35, fill=NAVY, color=WHITE)
pill(slide, "CHI TIẾT SẢN PHẨM", 7.28, 5.91, 2.05, fill=NAVY, color=WHITE)
text_box(slide, "Danh mục rõ ràng · Thẻ sản phẩm đồng nhất · CTA nổi bật · Tối ưu cho thao tác mua", 0.75, 6.67, 11.9, 0.28, size=13, color=TEAL_DARK, bold=True, align=PP_ALIGN.CENTER)

# 10 — Checkout
slide = new_slide("Giỏ hàng và quy trình đặt hàng", 10, "03 · Chức năng khách hàng")
left_items = [("01", "Chọn sản phẩm", "Thêm cá vào giỏ hoặc mua ngay."), ("02", "Kiểm tra giỏ", "Cập nhật số lượng, xóa sản phẩm."), ("03", "Nhập giao nhận", "Tên, email, điện thoại và địa chỉ."), ("04", "Xác nhận", "Tạo Order/OrderItem trong một giao dịch.")]
for i, (num, title, body) in enumerate(left_items):
    y = 1.63 + i * 1.20
    rect(slide, 0.69, y, 5.62, 0.94, WHITE, radius=True, line=LINE)
    rect(slide, 0.91, y + 0.17, 0.55, 0.55, TEAL, radius=True)
    text_box(slide, num, 0.91, y + 0.24, 0.55, 0.29, size=12, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    text_box(slide, title, 1.67, y + 0.15, 1.95, 0.28, size=15, color=NAVY, bold=True)
    text_box(slide, body, 1.67, y + 0.50, 4.22, 0.23, size=11.5, color=MUTED)
rect(slide, 6.76, 1.64, 5.87, 4.56, LIGHT, radius=True, line=LINE)
text_box(slide, "Quy tắc nghiệp vụ", 7.08, 1.97, 4.8, 0.38, size=21, color=NAVY, bold=True)
bullet_list(slide, [
    ("Xác thực: ", "phải đăng nhập mới có thể thao tác giỏ và đặt hàng."),
    ("Toàn vẹn: ", "tổng tiền được tính từ giá × số lượng trên máy chủ."),
    ("Thanh toán: ", "hỗ trợ COD và chuyển khoản ngân hàng."),
    ("Sau đặt hàng: ", "giỏ được xóa và trạng thái khởi tạo là Chờ xác nhận."),
], 7.08, 2.61, 4.95, 2.33, size=14.5, gap=10, bullet_color=ORANGE)
pill(slide, "transaction.atomic()", 7.10, 5.37, 1.82, fill=NAVY, color=CYAN)
pill(slide, "CSRF protection", 9.15, 5.37, 1.72, fill=NAVY, color=CYAN)

# 11 — Orders center
slide = new_slide("Trung tâm đơn hàng dành cho khách", 11, "03 · Chức năng khách hàng")
add_image_cover(slide, ASSET_DIR / "customer-orders.png", 0.68, 1.58, 7.62, 4.96, crop_focus_y=0.25)
text_box(slide, "Khách hàng chủ động", 8.68, 1.75, 3.55, 0.4, size=21, color=NAVY, bold=True)
bullet_list(slide, ["Lọc đơn theo trạng thái", "Tìm bằng mã đơn, vận đơn hoặc tên cá", "Hủy đơn khi còn Chờ xác nhận", "Mua lại toàn bộ sản phẩm", "Mở chi tiết để xem dòng thời gian"], 8.68, 2.38, 3.78, 2.55, size=15.2, gap=10)
rect(slide, 8.68, 5.22, 3.58, 0.96, PALE, radius=True, line=TEAL)
text_box(slide, "Mục tiêu: giảm phụ thuộc vào hỗ trợ thủ công của cửa hàng.", 8.93, 5.40, 3.08, 0.48, size=13, color=TEAL_DARK, bold=True, align=PP_ALIGN.CENTER)

# 12 — Tracking
slide = new_slide("Theo dõi vòng đời đơn hàng", 12, "03 · Chức năng khách hàng")
states = [("Chờ xác nhận", TEAL), ("Đã xác nhận", TEAL), ("Đang chuẩn bị", CYAN), ("Đang giao", ORANGE), ("Đã giao", GREEN), ("Đã đánh giá", NAVY_2)]
for i, (label, color) in enumerate(states):
    x = 0.54 + i * 2.09
    rect(slide, x, 1.65, 1.72, 0.69, color, radius=True)
    text_box(slide, label, x + 0.06, 1.82, 1.60, 0.25, size=10.5, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    if i < 5:
        arrow(slide, x + 1.75, 1.99, x + 2.04, 1.99, MUTED, 1.5)
add_image_cover(slide, ASSET_DIR / "order-tracking.png", 0.70, 2.69, 7.50, 3.78, crop_focus_y=0.23)
text_box(slide, "Kiểm soát trạng thái", 8.58, 2.77, 3.65, 0.38, size=20, color=NAVY, bold=True)
bullet_list(slide, ["Chỉ cho phép chuyển trạng thái hợp lệ", "Bắt buộc mã vận đơn trước khi giao", "Ghi người thực hiện, thời gian và ghi chú", "Có ngày giao dự kiến", "Khách xác nhận đã nhận hàng"], 8.58, 3.32, 3.8, 2.35, size=14.7, gap=8, bullet_color=ORANGE)
pill(slide, "Nhánh hủy: pending/confirmed/preparing → cancelled", 8.58, 5.95, 3.80, fill=RGBColor(255, 236, 231), color=RED)

# 13 — Admin dashboard
slide = new_slide("Dashboard quản trị cửa hàng", 13, "04 · Chức năng quản trị")
add_image_cover(slide, ASSET_DIR / "admin-dashboard.png", 0.66, 1.56, 8.04, 4.98, crop_focus_y=0.15)
text_box(slide, "Thông tin tập trung", 9.04, 1.74, 3.2, 0.37, size=20, color=NAVY, bold=True)
bullet_list(slide, ["Số lượng đơn hàng", "Doanh thu hoàn tất", "Sản phẩm và khách hàng", "Phân bố theo trạng thái", "Đơn hàng cần xử lý"], 9.04, 2.29, 3.25, 2.18, size=15, gap=10)
rect(slide, 9.04, 4.90, 3.22, 1.12, NAVY, radius=True)
text_box(slide, "Dashboard giúp quản trị viên ưu tiên công việc mỗi ngày.", 9.30, 5.10, 2.70, 0.58, size=13, color=WHITE, bold=True, align=PP_ALIGN.CENTER)

# 14 — Admin product
slide = new_slide("Quản lý sản phẩm và danh mục", 14, "04 · Chức năng quản trị")
add_image_cover(slide, ASSET_DIR / "admin-products.png", 0.66, 1.56, 8.13, 4.99, crop_focus_y=0.05)
text_box(slide, "Nghiệp vụ hỗ trợ", 9.10, 1.76, 3.10, 0.4, size=20, color=NAVY, bold=True)
bullet_list(slide, ["Thêm, sửa, xóa sản phẩm", "Tải và thay đổi ảnh cá", "Gán sản phẩm vào danh mục", "Đặt trạng thái đang bán", "Tìm kiếm và phân trang"], 9.10, 2.35, 3.2, 2.22, size=15, gap=9)
pill(slide, "50 sản phẩm sẵn sàng", 9.10, 4.95, 2.25, fill=TEAL, color=WHITE)
pill(slide, "3 danh mục", 9.10, 5.47, 1.47, fill=ORANGE, color=WHITE)

# 15 — API
slide = new_slide("REST API cho khối quản trị", 15, "04 · Backend API")
endpoints = [
    ("GET", "/api/admin/dashboard/", "Số liệu tổng quan"),
    ("CRUD", "/api/admin/products/", "Sản phẩm"),
    ("CRUD", "/api/admin/categories/", "Danh mục"),
    ("GET", "/api/admin/orders/", "Đơn hàng"),
    ("POST", "/orders/{id}/update_status/", "Cập nhật trạng thái"),
    ("GET", "/api/admin/customers/", "Khách hàng"),
    ("GET/DELETE", "/api/admin/reviews/", "Đánh giá"),
]
for i, (method, endpoint, desc) in enumerate(endpoints):
    y = 1.53 + i * 0.69
    rect(slide, 0.67, y, 7.48, 0.52, LIGHT if i % 2 == 0 else WHITE, radius=True, line=LINE)
    pill(slide, method, 0.83, y + 0.09, 1.05, fill=TEAL if method in ("GET", "CRUD") else ORANGE, color=WHITE)
    text_box(slide, endpoint, 2.10, y + 0.11, 3.62, 0.22, size=11.2, color=NAVY, bold=True)
    text_box(slide, desc, 5.83, y + 0.11, 2.02, 0.22, size=11.2, color=MUTED)
rect(slide, 8.52, 1.53, 4.10, 4.87, NAVY, radius=True)
text_box(slide, "Bảo vệ API", 8.88, 1.90, 3.28, 0.40, size=21, color=CYAN, bold=True)
bullet_list(slide, ["Session hoặc Basic Authentication", "Quyền IsAdminUser", "Phân trang mặc định 20 bản ghi", "Tìm kiếm và lọc theo query params", "Serializer kiểm soát dữ liệu đầu ra"], 8.89, 2.60, 3.18, 2.62, size=14.2, color=WHITE, bullet_color=CYAN, gap=10)
pill(slide, "JSON", 8.90, 5.58, 0.85, fill=TEAL, color=WHITE)
pill(slide, "DRF", 9.93, 5.58, 0.85, fill=ORANGE, color=WHITE)
pill(slide, "HTTP", 10.96, 5.58, 0.95, fill=GREEN, color=WHITE)

# 16 — Security
slide = new_slide("An toàn và toàn vẹn dữ liệu", 16, "05 · Chất lượng hệ thống")
security = [
    ("Xác thực & phân quyền", "Django Auth; chức năng quản trị yêu cầu is_staff; API yêu cầu IsAdminUser.", TEAL),
    ("Bảo vệ biểu mẫu", "POST cho thao tác thay đổi dữ liệu và CSRF middleware trên toàn hệ thống.", ORANGE),
    ("Quản lý mật khẩu", "Mật khẩu được băm theo cơ chế Django; áp dụng bộ kiểm tra mật khẩu mặc định.", GREEN),
    ("Toàn vẹn CSDL", "Foreign key, UniqueConstraint, PROTECT và transaction.atomic cho thao tác quan trọng.", RED),
    ("Cấu hình linh hoạt", "Thông tin kết nối và SECRET_KEY lấy từ biến môi trường trong tệp .env.", CYAN),
    ("Bảo vệ trình duyệt", "HttpOnly cookie, X-Frame-Options DENY và nosniff header.", NAVY_2),
]
for i, (title, body, accent) in enumerate(security):
    col, row = i % 2, i // 2
    x, y = 0.67 + col * 6.18, 1.56 + row * 1.69
    rect(slide, x, y, 5.79, 1.38, WHITE, radius=True, line=LINE)
    rect(slide, x, y, 0.11, 1.38, accent, radius=True)
    text_box(slide, title, x + 0.32, y + 0.20, 5.0, 0.32, size=16, color=NAVY, bold=True)
    text_box(slide, body, x + 0.32, y + 0.65, 5.05, 0.52, size=12.2, color=MUTED)

# 17 — Tests
slide = new_slide("Kiểm thử và kết quả", 17, "05 · Chất lượng hệ thống")
metric_card(slide, "8/8", "kiểm thử tự động đạt", 0.70, 1.66, 2.72, GREEN)
metric_card(slide, "0", "lỗi Django system check", 3.65, 1.66, 2.72, TEAL)
metric_card(slide, "50", "sản phẩm trong SQL Server", 6.60, 1.66, 2.72, ORANGE)
metric_card(slide, "100%", "ảnh sản phẩm hợp lệ", 9.55, 1.66, 2.72, CYAN)
rect(slide, 0.70, 3.22, 5.80, 2.90, NAVY, radius=True)
text_box(slide, "Các luồng đã kiểm thử", 1.04, 3.53, 4.9, 0.37, size=20, color=CYAN, bold=True)
bullet_list(slide, ["Trang chủ và chi tiết sản phẩm", "Đăng nhập và thao tác giỏ", "Đặt hàng và xóa giỏ", "Theo dõi, nhận hàng, hủy và mua lại", "Phân quyền dashboard và admin API"], 1.04, 4.13, 4.82, 1.62, size=13.7, color=WHITE, bullet_color=CYAN, gap=6)
rect(slide, 6.84, 3.22, 5.43, 2.90, LIGHT, radius=True, line=LINE)
text_box(slide, "Kết quả chạy thực tế", 7.17, 3.53, 4.55, 0.37, size=20, color=NAVY, bold=True)
text_box(slide, "........\nRan 8 tests in 2.161s\n\nOK\nSystem check identified no issues", 7.18, 4.09, 4.42, 1.48, size=16, color=TEAL_DARK, font="Consolas")
pill(slide, "Test database được tạo và hủy tự động", 7.17, 5.66, 3.33, fill=PALE, color=TEAL_DARK)

# 18 — Demo
slide = new_slide("Kịch bản demo đề xuất", 18, "06 · Trình diễn")
demo_steps = [
    ("01", "Khách hàng", "Mở trang chủ → tìm một loài cá → xem chi tiết."),
    ("02", "Mua hàng", "Đăng nhập → thêm giỏ → đặt hàng và chọn thanh toán."),
    ("03", "Quản trị", "Mở dashboard → xác nhận đơn → chuẩn bị → nhập mã vận đơn."),
    ("04", "Theo dõi", "Trở lại tài khoản khách → xem timeline và mã vận đơn."),
    ("05", "Hoàn tất", "Xác nhận nhận hàng → gửi đánh giá → trình bày API."),
]
for i, (num, title, body) in enumerate(demo_steps):
    y = 1.49 + i * 1.02
    rect(slide, 0.73, y, 11.85, 0.78, WHITE, radius=True, line=LINE)
    rect(slide, 0.96, y + 0.13, 0.50, 0.50, TEAL if i < 3 else ORANGE, radius=True)
    text_box(slide, num, 0.96, y + 0.19, 0.50, 0.28, size=11.5, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
    text_box(slide, title, 1.72, y + 0.18, 1.54, 0.30, size=15, color=NAVY, bold=True)
    text_box(slide, body, 3.27, y + 0.18, 8.75, 0.34, size=13.5, color=MUTED)
rect(slide, 0.74, 6.69, 11.84, 0.34, PALE, radius=True)
text_box(slide, "Thời lượng phù hợp: 7–10 phút · Chuẩn bị sẵn hai cửa sổ: khách hàng và quản trị viên", 0.92, 6.74, 11.47, 0.18, size=11, color=TEAL_DARK, bold=True, align=PP_ALIGN.CENTER)

# 19 — Results
slide = new_slide("Kết quả đạt được và hướng phát triển", 19, "07 · Tổng kết")
rect(slide, 0.68, 1.58, 5.83, 4.93, LIGHT, radius=True, line=LINE)
rect(slide, 6.82, 1.58, 5.83, 4.93, LIGHT, radius=True, line=LINE)
pill(slide, "ĐÃ HOÀN THÀNH", 1.00, 1.91, 1.78, fill=GREEN, color=WHITE)
bullet_list(slide, ["Website FishShop hoàn chỉnh trên Django", "SQL Server với 50 sản phẩm cá", "Quy trình mua và theo dõi đơn khép kín", "Dashboard và CRUD cho quản trị", "REST API có xác thực và phân quyền", "Kiểm thử tự động 8/8 thành công"], 1.01, 2.55, 5.0, 3.1, size=15.2, gap=9, bullet_color=GREEN)
pill(slide, "HƯỚNG PHÁT TRIỂN", 7.14, 1.91, 2.02, fill=ORANGE, color=WHITE)
bullet_list(slide, ["Tích hợp cổng thanh toán trực tuyến", "Thông báo email/Zalo theo trạng thái", "Quản lý tồn kho và khuyến mãi", "Phân tích doanh thu bằng biểu đồ", "Triển khai production với HTTPS", "Viết thêm integration và load test"], 7.15, 2.55, 5.0, 3.1, size=15.2, gap=9, bullet_color=ORANGE)

# 20 — Closing
slide = prs.slides.add_slide(BLANK)
rect(slide, 0, 0, 13.333, 7.5, NAVY)
rect(slide, 0, 0, 13.333, 0.12, CYAN)
slide.shapes.add_picture(str(ASSET_DIR / "uda-logo.png"), Inches(5.38), Inches(0.66), width=Inches(2.58))
text_box(slide, "XIN CẢM ƠN", 1.1, 2.15, 11.13, 0.74, size=40, color=WHITE, bold=True, align=PP_ALIGN.CENTER)
text_box(slide, "Thầy/Cô và các bạn đã lắng nghe", 1.3, 3.07, 10.73, 0.46, size=20, color=CYAN, align=PP_ALIGN.CENTER)
rect(slide, 5.66, 3.88, 2.02, 0.05, TEAL)
text_box(slide, "Q & A", 4.35, 4.31, 4.63, 0.66, size=30, color=ORANGE, bold=True, align=PP_ALIGN.CENTER)
text_box(slide, "FISHSHOP · LÊ THANH THIÊN · ST23D · 105693", 2.4, 6.62, 8.53, 0.28, size=11, color=RGBColor(156, 185, 198), bold=True, align=PP_ALIGN.CENTER)
text_box(slide, "20", 12.35, 7.15, 0.45, 0.16, size=9, color=WHITE, bold=True, align=PP_ALIGN.RIGHT)


# Core metadata and save
prs.core_properties.title = "FishShop - Website thương mại điện tử kinh doanh cá cảnh"
prs.core_properties.subject = "Báo cáo đồ án Python 2"
prs.core_properties.author = "Lê Thanh Thiên - ST23D - 105693"
prs.core_properties.keywords = "FishShop, Django, SQL Server, Python, REST API"
prs.core_properties.comments = "Bộ slide thuyết trình đồ án FishShop"
prs.save(OUT_FILE)
print(OUT_FILE)
print(f"Slides: {len(prs.slides)}")
