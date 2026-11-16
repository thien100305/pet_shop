from pathlib import Path
from zipfile import ZipFile

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output" / "report"
OUTPUT = OUTPUT_DIR / "Bao_cao_FishShop_LeThanhThien_ST23D_105693.docx"
SAMPLE = Path(r"C:\Users\NHATANH\Downloads\ST22C_TranNgocTien101119_TrinhVuHoaiThuong_devops.docx")
BLUE = "1D4ED8"
NAVY = "13213C"
LIGHT_BLUE = "DBEAFE"
GRAY = "F1F5F9"


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def add_field(paragraph, instruction):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "Nhấn F9 để cập nhật trường"
    separate.append(text)
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, end])


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run("Trang ")
    add_field(paragraph, "PAGE")


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def add_table(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    header = table.rows[0]
    set_repeat_table_header(header)
    for index, value in enumerate(headers):
        cell = header.cells[index]
        cell.text = str(value)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_shading(cell, NAVY)
        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.size = Pt(10)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for row_values in rows:
        cells = table.add_row().cells
        for index, value in enumerate(row_values):
            cells[index].text = str(value)
            cells[index].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for paragraph in cells[index].paragraphs:
                paragraph.paragraph_format.space_after = Pt(2)
                for run in paragraph.runs:
                    run.font.size = Pt(10)
        if len(table.rows) % 2 == 1:
            for cell in cells:
                set_cell_shading(cell, GRAY)
    if widths:
        for row in table.rows:
            for index, width in enumerate(widths):
                row.cells[index].width = Cm(width)
    doc.add_paragraph()
    return table


def add_bullets(doc, items):
    for item in items:
        paragraph = doc.add_paragraph(style="List Bullet")
        paragraph.add_run(item)


def add_numbered(doc, items):
    for item in items:
        paragraph = doc.add_paragraph(style="List Number")
        paragraph.add_run(item)


def add_code(doc, code):
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.left_indent = Cm(0.6)
    paragraph.paragraph_format.right_indent = Cm(0.6)
    paragraph.paragraph_format.space_before = Pt(3)
    paragraph.paragraph_format.space_after = Pt(8)
    p_pr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "EFF6FF")
    p_pr.append(shd)
    run = paragraph.add_run(code)
    run.font.name = "Consolas"
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(30, 64, 175)


def add_caption(doc, text):
    paragraph = doc.add_paragraph(style="Caption")
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(text)
    run.italic = True
    return paragraph


def add_image(doc, filename, caption, width=6.1):
    path = OUTPUT_DIR / filename
    if path.exists():
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.add_run().add_picture(str(path), width=Inches(width))
        add_caption(doc, caption)


def add_chapter(doc, title):
    doc.add_page_break()
    paragraph = doc.add_heading(title, level=1)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER


def style_document(doc):
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(13)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.first_line_indent = Cm(1)
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    normal.paragraph_format.space_after = Pt(5)

    for level, size, color in [(1, 16, NAVY), (2, 14, BLUE), (3, 13, "0F172A")]:
        style = doc.styles[f"Heading {level}"]
        style.font.name = "Times New Roman"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        style.paragraph_format.space_before = Pt(10)
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.keep_with_next = True

    doc.styles["Title"].font.name = "Times New Roman"
    doc.styles["Title"].font.bold = True
    doc.styles["Title"].font.color.rgb = RGBColor.from_string(NAVY)
    doc.styles["Caption"].font.name = "Times New Roman"
    doc.styles["Caption"].font.size = Pt(11)
    doc.styles["Caption"].font.italic = True

    for section in doc.sections:
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin = Cm(3.0)
        section.right_margin = Cm(2.0)
        section.header_distance = Cm(1.0)
        section.footer_distance = Cm(1.0)
        add_page_number(section.footer.paragraphs[0])


def extract_logo():
    logo = OUTPUT_DIR / "uda-logo.png"
    if not logo.exists() and SAMPLE.exists():
        with ZipFile(SAMPLE) as archive:
            logo.write_bytes(archive.read("word/media/image1.png"))
    return logo


def create_report():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = Document()
    style_document(doc)

    # Cover
    section = doc.sections[0]
    section.different_first_page_header_footer = True
    logo = extract_logo()
    if logo.exists():
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.add_run().add_picture(str(logo), width=Inches(2.6))
    for text, size, bold in [
        ("TRƯỜNG ĐẠI HỌC ĐÔNG Á", 16, True),
        ("KHOA CÔNG NGHỆ THÔNG TIN", 15, True),
    ]:
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run(text)
        run.bold = bold
        run.font.name = "Times New Roman"
        run.font.size = Pt(size)
    doc.add_paragraph("\n")
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run("BÁO CÁO KẾT THÚC MÔN")
    run.bold = True
    run.font.size = Pt(22)
    run.font.color.rgb = RGBColor.from_string(NAVY)
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run("PYTHON 2")
    run.bold = True
    run.font.size = Pt(24)
    run.font.color.rgb = RGBColor.from_string(BLUE)
    doc.add_paragraph()
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run("ĐỀ TÀI")
    run.bold = True
    run.font.size = Pt(15)
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run("XÂY DỰNG WEBSITE THƯƠNG MẠI ĐIỆN TỬ\nFISHSHOP BẰNG DJANGO VÀ SQL SERVER")
    run.bold = True
    run.font.size = Pt(20)
    run.font.color.rgb = RGBColor.from_string(NAVY)

    doc.add_paragraph("\n")
    info = add_table(doc, ["Thông tin", "Nội dung"], [
        ("Giảng viên hướng dẫn", "........................................................"),
        ("Sinh viên thực hiện", "Lê Thanh Thiên"),
        ("Mã sinh viên", "105693"),
        ("Lớp", "ST23D"),
    ], [5.5, 10.5])
    for cell in info.rows[0].cells:
        set_cell_shading(cell, BLUE)
    paragraph = doc.add_paragraph("Đà Nẵng, tháng 11 năm 2026")
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.runs[0].italic = True

    # TOC
    doc.add_page_break()
    heading = doc.add_heading("MỤC LỤC", level=1)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    toc = doc.add_paragraph()
    add_field(toc, 'TOC \\o "1-3" \\h \\z \\u')
    doc.add_page_break()
    heading = doc.add_heading("DANH MỤC HÌNH ẢNH", level=1)
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    figures = [
        "Hình 1. Kiến trúc tổng thể hệ thống FishShop",
        "Hình 2. Luồng xử lý đơn hàng",
        "Hình 3. Giao diện trang chủ FishShop",
        "Hình 4. Giao diện chi tiết sản phẩm",
        "Hình 5. Giao diện đăng nhập",
        "Hình 6. Trung tâm đơn mua của khách hàng",
        "Hình 7. Theo dõi chi tiết vận chuyển",
        "Hình 8. Dashboard quản trị FishShop",
        "Hình 9. Giao diện quản lý 50 sản phẩm",
    ]
    for item in figures:
        doc.add_paragraph(item)

    # Introduction
    add_chapter(doc, "LỜI MỞ ĐẦU")
    doc.add_paragraph(
        "Sự phát triển của thương mại điện tử tạo điều kiện để các cửa hàng chuyên biệt tiếp cận khách hàng nhanh hơn, "
        "quản lý sản phẩm tập trung và nâng cao chất lượng phục vụ. Với lĩnh vực cá cảnh, một hệ thống trực tuyến không chỉ "
        "cần giới thiệu hình ảnh và giá bán mà còn phải hỗ trợ giỏ hàng, đặt hàng, theo dõi vận chuyển, đánh giá sản phẩm và "
        "quản trị dữ liệu một cách an toàn."
    )
    doc.add_paragraph(
        "Đề tài FishShop được xây dựng bằng Django 5.2.8 theo mô hình MVT, sử dụng Microsoft SQL Server làm hệ quản trị cơ sở "
        "dữ liệu và Django REST Framework để cung cấp API quản trị. Hệ thống hiện có 50 sản phẩm thuộc ba nhóm cá cảnh, hỗ trợ "
        "đầy đủ nghiệp vụ từ tìm kiếm, xem chi tiết, giỏ hàng, đặt hàng đến theo dõi trạng thái và đánh giá sau khi nhận hàng."
    )
    doc.add_paragraph(
        "Báo cáo trình bày cơ sở lý thuyết, yêu cầu nghiệp vụ, thiết kế cơ sở dữ liệu, quá trình triển khai, kết quả kiểm thử và "
        "định hướng phát triển. Nội dung và hình ảnh được tổng hợp trực tiếp từ phiên bản FishShop đã hoàn thành và kết nối thành "
        "công với SQL Server Express."
    )

    # Chapter 1
    add_chapter(doc, "CHƯƠNG 1. CƠ SỞ LÝ THUYẾT")
    doc.add_heading("1.1. Tổng quan thương mại điện tử", level=2)
    doc.add_paragraph(
        "Thương mại điện tử là mô hình thực hiện hoạt động giới thiệu, giao dịch và chăm sóc khách hàng trên nền tảng số. "
        "Đối với cửa hàng cá cảnh, website giúp khách hàng tiếp cận thông tin giống cá, giá bán, đặc điểm chăm sóc và trạng thái "
        "đơn hàng mà không phụ thuộc vào thời gian mở cửa của cửa hàng vật lý."
    )
    doc.add_heading("1.2. Python và Django Framework", level=2)
    doc.add_paragraph(
        "Django là framework web mã nguồn mở của Python, cung cấp sẵn ORM, hệ thống URL, template, xác thực, session, biểu mẫu, "
        "migration và trang quản trị. Cấu trúc Model–View–Template giúp phân tách dữ liệu, xử lý nghiệp vụ và giao diện, từ đó "
        "tăng khả năng bảo trì và kiểm thử."
    )
    add_table(doc, ["Thành phần", "Vai trò trong FishShop"], [
        ("Model", "Mô tả Category, Product, Cart, Order, Review và các quan hệ dữ liệu."),
        ("View", "Xử lý tìm kiếm, giỏ hàng, thanh toán, theo dõi đơn và quản trị."),
        ("Template", "Hiển thị giao diện HTML responsive bằng Django Template Language."),
        ("URL Router", "Ánh xạ đường dẫn người dùng, quản trị và REST API."),
        ("ORM/Migration", "Đồng bộ model Python với Microsoft SQL Server."),
    ], [4, 12])
    doc.add_heading("1.3. Microsoft SQL Server", level=2)
    doc.add_paragraph(
        "Microsoft SQL Server là hệ quản trị cơ sở dữ liệu quan hệ, hỗ trợ giao dịch, khóa, ràng buộc toàn vẹn, chỉ mục và quản "
        "lý bằng SQL Server Management Studio. FishShop kết nối SQL Server thông qua mssql-django và ODBC Driver 18. Database "
        "FishShopDB được tạo bởi script FishShop.sql và quản lý thay đổi cấu trúc bằng migration của Django."
    )
    doc.add_heading("1.4. REST API và Django REST Framework", level=2)
    doc.add_paragraph(
        "REST API biểu diễn tài nguyên bằng URL và trao đổi dữ liệu JSON qua các phương thức HTTP. Django REST Framework được "
        "sử dụng để xây dựng API quản trị cho dashboard, sản phẩm, danh mục, đơn hàng, khách hàng và đánh giá. Các endpoint được "
        "bảo vệ bằng Session Authentication hoặc Basic Authentication và chỉ cho phép tài khoản staff/superuser truy cập."
    )
    doc.add_heading("1.5. Bảo mật và phân quyền", level=2)
    add_bullets(doc, [
        "Mật khẩu được băm bằng cơ chế xác thực chuẩn của Django, không lưu dạng rõ trong cơ sở dữ liệu.",
        "CSRF token bảo vệ các biểu mẫu thay đổi dữ liệu.",
        "Kiểm tra quyền sở hữu đảm bảo khách hàng chỉ xem và thao tác trên đơn hàng của chính mình.",
        "IsAdminUser bảo vệ toàn bộ API quản trị.",
        "SecurityMiddleware, HttpOnly cookie, X-Frame-Options và Content-Type sniffing protection được bật.",
    ])
    doc.add_heading("1.6. Docker và khả năng triển khai", level=2)
    doc.add_paragraph(
        "Dockerfile của dự án sử dụng Python 3.12 slim, cài ODBC Driver 18, các dependency trong requirements.txt và chạy ứng "
        "dụng qua Gunicorn. Cách đóng gói này giúp môi trường phát triển và triển khai đồng nhất, thuận tiện khi đưa hệ thống lên "
        "máy chủ Linux hoặc nền tảng cloud."
    )

    # Chapter 2
    add_chapter(doc, "CHƯƠNG 2. PHÂN TÍCH VÀ THIẾT KẾ HỆ THỐNG")
    doc.add_heading("2.1. Mục tiêu đề tài", level=2)
    add_bullets(doc, [
        "Xây dựng website chuyên bán cá cảnh với giao diện hiện đại, responsive.",
        "Quản lý tối thiểu 50 sản phẩm thuộc cá nước ngọt, cá biển và cá Koi.",
        "Hỗ trợ đầy đủ giỏ hàng, checkout, đơn hàng, vận chuyển và đánh giá.",
        "Cung cấp dashboard và REST API dành cho quản trị viên.",
        "Lưu trữ dữ liệu tập trung trên Microsoft SQL Server và có script khởi tạo bằng SSMS.",
        "Đảm bảo phân quyền rõ ràng giữa khách hàng, nhân viên và superuser.",
    ])
    doc.add_heading("2.2. Tác nhân hệ thống", level=2)
    add_table(doc, ["Tác nhân", "Quyền và nghiệp vụ chính"], [
        ("Khách vãng lai", "Xem danh mục, tìm kiếm, xem chi tiết sản phẩm, đăng ký và đăng nhập."),
        ("Khách hàng", "Quản lý giỏ, đặt hàng, theo dõi vận chuyển, hủy đơn chờ xác nhận, mua lại và đánh giá."),
        ("Nhân viên", "Xem dashboard, quản lý sản phẩm/danh mục, xử lý trạng thái và mã vận đơn."),
        ("Superuser", "Có toàn bộ quyền nhân viên, truy cập Django Admin và API quản trị."),
    ], [4, 12])
    doc.add_heading("2.3. Yêu cầu chức năng", level=2)
    add_table(doc, ["STT", "Nhóm chức năng", "Mô tả"], [
        (1, "Tài khoản", "Đăng ký, đăng nhập, đăng xuất, cập nhật hồ sơ và phân quyền."),
        (2, "Sản phẩm", "Hiển thị 50 loài cá, lọc danh mục, tìm kiếm và xem chi tiết."),
        (3, "Giỏ hàng", "Thêm, cập nhật số lượng, xóa và tính tổng tự động."),
        (4, "Checkout", "Nhập thông tin giao hàng, chọn COD/chuyển khoản và tạo đơn."),
        (5, "Đơn mua", "Lọc trạng thái, tìm mã đơn/mã vận đơn/tên cá, hủy và mua lại."),
        (6, "Theo dõi", "Hiển thị tiến trình năm bước, lịch sử cập nhật và ngày giao dự kiến."),
        (7, "Đánh giá", "Chỉ khách đã nhận hàng được đánh giá từ 1 đến 5 sao."),
        (8, "Quản trị", "Thống kê, CRUD danh mục/sản phẩm và xử lý đơn đúng luồng."),
        (9, "Backend API", "Dashboard, sản phẩm, danh mục, đơn hàng, khách hàng, đánh giá."),
    ], [1.5, 4.2, 10.3])
    doc.add_heading("2.4. Yêu cầu phi chức năng", level=2)
    add_table(doc, ["Tiêu chí", "Yêu cầu"], [
        ("Bảo mật", "Xác thực, phân quyền, CSRF, HttpOnly cookie và kiểm tra quyền sở hữu."),
        ("Hiệu năng", "Phân trang sản phẩm/đơn hàng, select_related và prefetch_related giảm truy vấn."),
        ("Tin cậy", "Transaction atomic cho checkout, hủy đơn, mua lại và đổi trạng thái."),
        ("Khả dụng", "Giao diện tiếng Việt, responsive, trạng thái dễ nhận biết."),
        ("Bảo trì", "MVT, ORM, migration và API tách module rõ ràng."),
        ("Khả năng triển khai", "Có Dockerfile, requirements và biến môi trường .env."),
    ], [4, 12])
    doc.add_heading("2.5. Kiến trúc tổng thể", level=2)
    architecture = add_table(doc, ["Tầng", "Thành phần", "Dữ liệu trao đổi"], [
        ("Client", "Trình duyệt khách hàng / quản trị", "HTTP, HTML, CSS, biểu mẫu, JSON"),
        ("Web", "Django URL + View + Template", "Request/Response, Session, CSRF"),
        ("API", "Django REST Framework", "JSON, Session/Basic Authentication"),
        ("Nghiệp vụ", "Models, Forms, Transaction", "Đối tượng domain và validation"),
        ("Dữ liệu", "mssql-django + ODBC Driver 18", "SQL và transaction"),
        ("CSDL", "Microsoft SQL Server – FishShopDB", "Bảng, khóa ngoại, chỉ mục"),
    ], [3, 7, 6])
    add_caption(doc, "Hình 1. Kiến trúc tổng thể hệ thống FishShop")
    doc.add_heading("2.6. Luồng xử lý đơn hàng", level=2)
    add_table(doc, ["Trạng thái hiện tại", "Trạng thái tiếp theo hợp lệ", "Chủ thể"], [
        ("Chờ xác nhận", "Đã xác nhận / Đã hủy", "Nhân viên / Khách hàng"),
        ("Đã xác nhận", "Đang chuẩn bị / Đã hủy", "Nhân viên"),
        ("Đang chuẩn bị", "Đang giao / Đã hủy", "Nhân viên"),
        ("Đang giao", "Đã giao", "Khách hàng hoặc hệ thống"),
        ("Đã giao", "Đã đánh giá", "Khách hàng"),
        ("Đã đánh giá / Đã hủy", "Kết thúc", "Hệ thống"),
    ], [4, 7, 5])
    add_caption(doc, "Hình 2. Luồng xử lý đơn hàng")

    # Chapter 3
    add_chapter(doc, "CHƯƠNG 3. THIẾT KẾ CƠ SỞ DỮ LIỆU VÀ API")
    doc.add_heading("3.1. Mô hình dữ liệu", level=2)
    add_table(doc, ["Bảng", "Vai trò", "Quan hệ chính"], [
        ("auth_user", "Tài khoản và quyền truy cập", "1–1 UserProfile, 1–n Order/Review"),
        ("accounts_category", "Danh mục cá", "1–n Product"),
        ("accounts_product", "Thông tin cá, giá, ảnh, trạng thái", "n–1 Category, 1–n OrderItem/Review"),
        ("accounts_cart", "Giỏ hàng của người dùng", "1–1 User, 1–n CartItem"),
        ("accounts_cartitem", "Sản phẩm và số lượng trong giỏ", "n–1 Cart/Product"),
        ("accounts_order", "Thông tin đơn hàng và vận chuyển", "n–1 User, 1–n OrderItem/History"),
        ("accounts_orderitem", "Chi tiết hàng hóa và giá tại thời điểm mua", "n–1 Order/Product"),
        ("accounts_orderstatushistory", "Nhật ký trạng thái đơn", "n–1 Order/User"),
        ("accounts_review", "Số sao và nhận xét", "n–1 User/Product/Order"),
        ("accounts_userprofile", "Thông tin liên hệ khách hàng", "1–1 User"),
    ], [4.5, 7, 4.5])
    doc.add_heading("3.2. Ràng buộc toàn vẹn", level=2)
    add_bullets(doc, [
        "Tên danh mục là duy nhất; giá sản phẩm và tổng đơn không âm.",
        "Mỗi người dùng chỉ có một giỏ hàng và một hồ sơ.",
        "Một sản phẩm chỉ xuất hiện một lần trong mỗi giỏ, số lượng từ 1 đến 99.",
        "Điểm đánh giá nằm trong khoảng 1–5; một người chỉ đánh giá một sản phẩm một lần.",
        "Sản phẩm đã xuất hiện trong đơn hàng được bảo vệ khỏi thao tác xóa trực tiếp.",
        "Lịch sử trạng thái lưu người cập nhật, thời gian và ghi chú để truy vết.",
    ])
    doc.add_heading("3.3. Dữ liệu sản phẩm", level=2)
    doc.add_paragraph(
        "Cơ sở dữ liệu có 50 sản phẩm khác nhau: 30 cá cảnh nước ngọt, 10 cá cảnh biển và 10 cá Koi. Mỗi sản phẩm có tên, "
        "mô tả, giá, hình ảnh, danh mục và trạng thái đang bán. Dữ liệu được tạo idempotent bởi FishShop.sql và migration "
        "0011–0012, vì vậy có thể chạy lại mà không phát sinh tên sản phẩm trùng."
    )
    doc.add_heading("3.4. Thiết kế REST API quản trị", level=2)
    add_table(doc, ["Endpoint", "Phương thức", "Chức năng"], [
        ("/api/admin/dashboard/", "GET", "Số liệu tổng hợp, doanh thu, top sản phẩm, đơn mới."),
        ("/api/admin/products/", "GET/POST", "Danh sách, tìm kiếm, lọc và tạo sản phẩm."),
        ("/api/admin/products/{id}/", "GET/PUT/PATCH/DELETE", "Chi tiết và CRUD sản phẩm."),
        ("/api/admin/products/{id}/toggle_active/", "POST", "Ẩn hoặc mở bán sản phẩm."),
        ("/api/admin/categories/", "CRUD", "Quản lý danh mục."),
        ("/api/admin/orders/", "GET", "Tìm kiếm và lọc đơn hàng."),
        ("/api/admin/orders/{id}/update_status/", "POST", "Đổi trạng thái đúng quy trình."),
        ("/api/admin/customers/", "GET", "Danh sách khách, tổng đơn và chi tiêu."),
        ("/api/admin/customers/{id}/toggle_active/", "POST", "Khóa hoặc mở tài khoản khách."),
        ("/api/admin/reviews/", "GET/DELETE", "Lọc và kiểm duyệt đánh giá."),
    ], [7.2, 3.4, 5.4])
    doc.add_heading("3.5. Cấu hình kết nối SQL Server", level=2)
    add_code(doc, 'DATABASES = {"default": {\n    "ENGINE": "mssql",\n    "NAME": "FishShopDB",\n    "HOST": "LETHANHTHIEN\\\\SQLEXPRESS01",\n    "OPTIONS": {"driver": "ODBC Driver 18 for SQL Server"}\n}}')

    # Chapter 4
    add_chapter(doc, "CHƯƠNG 4. TRIỂN KHAI HỆ THỐNG")
    doc.add_heading("4.1. Môi trường và công nghệ", level=2)
    add_table(doc, ["Thành phần", "Phiên bản / lựa chọn", "Vai trò"], [
        ("Python", "3.12+", "Ngôn ngữ backend"),
        ("Django", "5.2.8", "Web framework MVT"),
        ("Django REST Framework", "3.16.1", "Backend API quản trị"),
        ("Microsoft SQL Server", "SQL Server 2022 Express", "Cơ sở dữ liệu FishShopDB"),
        ("mssql-django", "1.6+", "Backend kết nối Django–SQL Server"),
        ("pyodbc", "5.2+", "Kết nối ODBC"),
        ("Pillow", "12.0", "Xử lý trường ảnh sản phẩm"),
        ("HTML/CSS", "Responsive", "Giao diện khách hàng và quản trị"),
        ("Docker/Gunicorn", "Python 3.12 slim", "Đóng gói và chạy production"),
    ], [4.5, 4.5, 7])
    doc.add_heading("4.2. Cấu trúc mã nguồn", level=2)
    add_code(doc, "FishShop/\n├── accounts/               # Model, view, form, API, migration, test\n├── fishshop/               # Settings, URL, template và static\n├── media/products/         # Ảnh các loài cá\n├── FishShop.sql            # Script khởi tạo SQL Server\n├── Dockerfile              # Image triển khai\n├── requirements.txt        # Thư viện Python\n└── manage.py               # Công cụ quản trị Django")
    doc.add_heading("4.3. Khởi tạo cơ sở dữ liệu", level=2)
    add_numbered(doc, [
        "Mở FishShop.sql trong SQL Server Management Studio.",
        "Kết nối SQL Server Express bằng tài khoản có quyền tạo database.",
        "Chạy toàn bộ script để tạo FishShopDB, bảng và 50 sản phẩm mẫu.",
        "Cấu hình DB_HOST, DB_USER, DB_PASSWORD trong file .env.",
        "Chạy python manage.py migrate để áp dụng migration còn thiếu.",
    ])
    add_code(doc, "python -m venv .venv\n.\\.venv\\Scripts\\Activate.ps1\npip install -r requirements.txt\npython manage.py migrate\npython manage.py runserver")
    doc.add_heading("4.4. Luồng đặt hàng", level=2)
    add_numbered(doc, [
        "Khách đăng nhập, chọn cá và thêm vào giỏ hoặc mua ngay.",
        "Hệ thống xác thực biểu mẫu giao hàng và khóa dữ liệu cần thiết trong transaction.",
        "Order và OrderItem được tạo, giá được chụp tại thời điểm mua.",
        "Giỏ hàng được xóa sau khi checkout thành công.",
        "OrderStatusHistory ghi nhận trạng thái chờ xác nhận.",
        "Nhân viên cập nhật chuẩn bị, mã vận đơn và ngày giao dự kiến.",
        "Khách theo dõi, xác nhận nhận hàng và đánh giá sản phẩm.",
    ])
    doc.add_heading("4.5. Quản lý đơn hàng khách hàng", level=2)
    doc.add_paragraph(
        "Trang Đơn mua cung cấp các tab trạng thái, tìm kiếm theo mã đơn, mã vận đơn hoặc tên cá. Khách được hủy đơn khi còn "
        "chờ xác nhận; thao tác được khóa bằng select_for_update và transaction.atomic. Chức năng Mua lại thêm các sản phẩm còn "
        "hoạt động vào giỏ, bảo đảm số lượng không vượt quá 99."
    )
    doc.add_heading("4.6. Quản trị và API", level=2)
    doc.add_paragraph(
        "Dashboard hiển thị số sản phẩm, danh mục, đơn chờ xác nhận và doanh thu đã giao. Nhân viên có thể quản lý sản phẩm, "
        "danh mục và chuyển trạng thái đơn theo luồng cho phép. API quản trị được duy trì ở backend nhưng không hiển thị trong "
        "menu giao diện, phù hợp với yêu cầu tách biệt giữa người vận hành và tích hợp hệ thống."
    )

    # Chapter 5
    add_chapter(doc, "CHƯƠNG 5. KẾT QUẢ THỰC NGHIỆM VÀ ĐÁNH GIÁ")
    doc.add_heading("5.1. Giao diện trang chủ", level=2)
    doc.add_paragraph(
        "Trang chủ hiển thị banner thương hiệu, danh mục và lưới sản phẩm có phân trang. Dữ liệu đọc trực tiếp từ FishShopDB; "
        "tại thời điểm nghiệm thu hệ thống hiển thị đủ 50 sản phẩm."
    )
    add_image(doc, "home.png", "Hình 3. Giao diện trang chủ FishShop", width=5.25)
    doc.add_heading("5.2. Chi tiết sản phẩm", level=2)
    add_image(doc, "product.png", "Hình 4. Giao diện chi tiết sản phẩm", width=5.6)
    doc.add_heading("5.3. Xác thực người dùng", level=2)
    add_image(doc, "login.png", "Hình 5. Giao diện đăng nhập", width=6.1)
    doc.add_heading("5.4. Trung tâm đơn mua", level=2)
    add_image(doc, "customer-orders.png", "Hình 6. Trung tâm đơn mua của khách hàng", width=6.2)
    doc.add_heading("5.5. Theo dõi chi tiết vận chuyển", level=2)
    add_image(doc, "order-tracking.png", "Hình 7. Theo dõi chi tiết vận chuyển", width=6.2)
    doc.add_heading("5.6. Dashboard quản trị", level=2)
    add_image(doc, "admin-dashboard.png", "Hình 8. Dashboard quản trị FishShop", width=6.2)
    doc.add_heading("5.7. Quản lý sản phẩm", level=2)
    add_image(doc, "admin-products.png", "Hình 9. Giao diện quản lý 50 sản phẩm", width=6.2)
    doc.add_heading("5.8. Kiểm thử chức năng", level=2)
    add_table(doc, ["STT", "Ca kiểm thử", "Kết quả"], [
        (1, "Trang chủ và chi tiết sản phẩm trả HTTP 200", "Đạt"),
        (2, "Giỏ hàng yêu cầu đăng nhập và chỉ nhận POST khi thay đổi", "Đạt"),
        (3, "Checkout tạo đơn, chi tiết đơn và xóa giỏ đúng", "Đạt"),
        (4, "Khách theo dõi và xác nhận đã nhận hàng", "Đạt"),
        (5, "Nhân viên phải tuân thủ chuyển trạng thái hợp lệ", "Đạt"),
        (6, "Dashboard chỉ dành cho staff", "Đạt"),
        (7, "API quản trị chặn khách thường và trả danh sách sản phẩm", "Đạt"),
        (8, "Khách có thể theo dõi, hủy đơn chờ xác nhận và mua lại", "Đạt"),
    ], [1.5, 11.5, 3])
    doc.add_paragraph(
        "Kết quả chạy bộ kiểm thử: 8/8 test thành công; Django system check không phát hiện lỗi; migration graph hợp lệ và "
        "không có thay đổi model chưa được tạo migration. Script FishShop.sql đã được chạy lặp trên database thật và số lượng "
        "sản phẩm vẫn giữ 50 tên duy nhất, chứng minh tính idempotent."
    )
    doc.add_heading("5.9. Đánh giá", level=2)
    doc.add_heading("Ưu điểm", level=3)
    add_bullets(doc, [
        "Chức năng khách hàng và quản trị tương đối đầy đủ, luồng đơn hàng rõ ràng.",
        "Dữ liệu thực trên SQL Server, không sử dụng SQLite.",
        "Phân quyền và kiểm tra quyền sở hữu được áp dụng nhất quán.",
        "API quản trị có phân trang, tìm kiếm, lọc và action nghiệp vụ.",
        "Mã nguồn có kiểm thử tự động và đóng gói Docker.",
        "Giao diện thống nhất, responsive và có hình ảnh cá riêng cho từng nhóm.",
    ])
    doc.add_heading("Hạn chế", level=3)
    add_bullets(doc, [
        "Chưa tích hợp cổng thanh toán trực tuyến thực tế.",
        "Chưa có quản lý tồn kho theo số lượng và cảnh báo sắp hết hàng.",
        "Một số sản phẩm mở rộng đang dùng chung ảnh đại diện theo nhóm.",
        "Chưa có email/SMS thông báo thay đổi trạng thái đơn.",
        "Mật khẩu demo quản trị đơn giản, chỉ phù hợp môi trường học tập.",
    ])

    # Conclusion
    add_chapter(doc, "CHƯƠNG 6. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN")
    doc.add_heading("6.1. Kết luận", level=2)
    doc.add_paragraph(
        "Đề tài đã xây dựng thành công website thương mại điện tử FishShop bằng Django và Microsoft SQL Server. Hệ thống đáp "
        "ứng các chức năng chính của một cửa hàng cá cảnh trực tuyến: quản lý 50 sản phẩm, tìm kiếm, giỏ hàng, checkout, theo "
        "dõi đơn mua, hủy đơn, mua lại, xác nhận nhận hàng và đánh giá. Khu vực quản trị hỗ trợ thống kê, quản lý danh mục, sản "
        "phẩm và xử lý đơn hàng theo quy trình."
    )
    doc.add_paragraph(
        "Việc sử dụng Django ORM và migration giúp mô hình dữ liệu nhất quán; transaction đảm bảo an toàn cho các thao tác quan "
        "trọng; REST API tạo nền tảng để kết nối ứng dụng di động hoặc dashboard độc lập trong tương lai. Kết quả kiểm thử cho "
        "thấy các luồng nghiệp vụ cốt lõi hoạt động đúng và ổn định trên SQL Server Express."
    )
    doc.add_heading("6.2. Hướng phát triển", level=2)
    add_bullets(doc, [
        "Bổ sung tồn kho, nhập hàng, nhà cung cấp và cảnh báo số lượng thấp.",
        "Tích hợp VNPay, MoMo hoặc PayPal và đối soát giao dịch.",
        "Thêm voucher, flash sale, phí vận chuyển và chương trình khách hàng thân thiết.",
        "Tạo ảnh riêng cho toàn bộ 50 loài cá và hỗ trợ album nhiều ảnh.",
        "Gửi email/SMS hoặc thông báo đẩy khi đơn thay đổi trạng thái.",
        "Áp dụng JWT/OAuth2 cho ứng dụng mobile và tài liệu OpenAPI/Swagger.",
        "Triển khai HTTPS, domain, giám sát log, backup tự động và CI/CD.",
        "Tối ưu tìm kiếm bằng full-text search và xây dựng gợi ý sản phẩm.",
    ])

    # References and appendix
    add_chapter(doc, "TÀI LIỆU THAM KHẢO")
    references = [
        "[1] Django Software Foundation. Django 5.2 Documentation. https://docs.djangoproject.com/en/5.2/",
        "[2] Django REST Framework. API Guide. https://www.django-rest-framework.org/",
        "[3] Microsoft. SQL Server Documentation. https://learn.microsoft.com/sql/sql-server/",
        "[4] Microsoft. ODBC Driver for SQL Server. https://learn.microsoft.com/sql/connect/odbc/",
        "[5] mssql-django. Microsoft SQL Server backend for Django. https://github.com/microsoft/mssql-django",
        "[6] Python Software Foundation. Python Documentation. https://docs.python.org/3/",
        "[7] Docker, Inc. Docker Documentation. https://docs.docker.com/",
        "[8] OWASP Foundation. Web Application Security Cheat Sheets. https://cheatsheetseries.owasp.org/",
        "[9] Bootstrap Team. Responsive Web Design Concepts. https://getbootstrap.com/docs/",
        "[10] Git SCM. Git Documentation. https://git-scm.com/doc",
    ]
    for reference in references:
        doc.add_paragraph(reference)

    doc.add_page_break()
    doc.add_heading("PHỤ LỤC A. HƯỚNG DẪN CHẠY DỰ ÁN", level=1)
    add_code(doc, "# 1. Cài môi trường\npython -m venv .venv\n.\\.venv\\Scripts\\Activate.ps1\npip install -r requirements.txt\n\n# 2. Mở FishShop.sql trong SSMS và chạy toàn bộ\n\n# 3. Chạy Django\npython manage.py migrate\npython manage.py runserver")
    doc.add_heading("Tài khoản quản trị demo", level=2)
    add_table(doc, ["Thông tin", "Giá trị"], [
        ("Đường dẫn", "/quan-tri/"),
        ("Tên đăng nhập", "admin"),
        ("Mật khẩu", "123456 (chỉ dùng cho môi trường học tập)"),
    ], [5, 11])
    doc.add_heading("Các đường dẫn chính", level=2)
    add_table(doc, ["Đường dẫn", "Chức năng"], [
        ("/", "Trang chủ và danh sách sản phẩm"),
        ("/cart/", "Giỏ hàng"),
        ("/don-hang/", "Trung tâm đơn mua"),
        ("/profile/", "Hồ sơ khách hàng"),
        ("/quan-tri/", "Dashboard quản trị"),
        ("/api/admin/", "REST API quản trị"),
    ], [6, 10])

    # Ask Word to update TOC/fields when opened.
    settings = doc.settings._element
    update_fields = OxmlElement("w:updateFields")
    update_fields.set(qn("w:val"), "true")
    settings.append(update_fields)

    doc.core_properties.title = "Báo cáo dự án FishShop"
    doc.core_properties.subject = "Website thương mại điện tử Django và SQL Server"
    doc.core_properties.author = "Lê Thanh Thiên - ST23D - 105693"
    doc.core_properties.keywords = "FishShop, Django, SQL Server, REST API, Python 2"
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    create_report()
