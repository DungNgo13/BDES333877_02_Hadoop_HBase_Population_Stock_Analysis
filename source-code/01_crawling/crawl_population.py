"""
crawl_population.py — Thu thập dữ liệu dân số các tỉnh/thành Việt Nam từ Wikipedia.
Nếu crawl thất bại, dùng fallback từ dataset/sample/population_sample.csv.

Output: dataset/raw/population_raw.csv
Columns: province,population,area,density,region
"""

import csv
import os
import sys
from pathlib import Path

# Đảm bảo console Windows hiển thị được tiếng Việt
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("[CẢNH BÁO] Thiếu thư viện requests hoặc beautifulsoup4.")
    print("Chạy: pip install requests beautifulsoup4")
    requests = None
    BeautifulSoup = None

# Đường dẫn tương đối từ project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_OUTPUT = PROJECT_ROOT / "dataset" / "raw" / "population_raw.csv"
SAMPLE_FILE = PROJECT_ROOT / "dataset" / "sample" / "population_sample.csv"

# URL nguồn Wikipedia
WIKI_URL = "https://en.wikipedia.org/wiki/Provinces_of_Vietnam"

# Bảng ánh xạ tỉnh → vùng (dùng cho cả crawl và fallback)
REGION_MAP = {
    "Ha Noi": "Red River Delta",
    "Ho Chi Minh": "Southeast",
    "Hai Phong": "Red River Delta",
    "Da Nang": "South Central Coast",
    "Can Tho": "Mekong River Delta",
    "Ha Giang": "Northeast",
    "Cao Bang": "Northeast",
    "Bac Kan": "Northeast",
    "Tuyen Quang": "Northeast",
    "Lao Cai": "Northwest",
    "Dien Bien": "Northwest",
    "Lai Chau": "Northwest",
    "Son La": "Northwest",
    "Yen Bai": "Northeast",
    "Hoa Binh": "Northwest",
    "Thai Nguyen": "Northeast",
    "Lang Son": "Northeast",
    "Quang Ninh": "Red River Delta",
    "Bac Giang": "Northeast",
    "Phu Tho": "Northeast",
    "Vinh Phuc": "Red River Delta",
    "Bac Ninh": "Red River Delta",
    "Hai Duong": "Red River Delta",
    "Hung Yen": "Red River Delta",
    "Ha Nam": "Red River Delta",
    "Nam Dinh": "Red River Delta",
    "Thai Binh": "Red River Delta",
    "Ninh Binh": "Red River Delta",
    "Thanh Hoa": "North Central Coast",
    "Nghe An": "North Central Coast",
    "Ha Tinh": "North Central Coast",
    "Quang Binh": "North Central Coast",
    "Quang Tri": "North Central Coast",
    "Thua Thien Hue": "North Central Coast",
    "Quang Nam": "South Central Coast",
    "Quang Ngai": "South Central Coast",
    "Binh Dinh": "South Central Coast",
    "Phu Yen": "South Central Coast",
    "Khanh Hoa": "South Central Coast",
    "Ninh Thuan": "South Central Coast",
    "Binh Thuan": "South Central Coast",
    "Kon Tum": "Central Highlands",
    "Gia Lai": "Central Highlands",
    "Dak Lak": "Central Highlands",
    "Dak Nong": "Central Highlands",
    "Lam Dong": "Central Highlands",
    "Binh Phuoc": "Southeast",
    "Tay Ninh": "Southeast",
    "Binh Duong": "Southeast",
    "Dong Nai": "Southeast",
    "Ba Ria Vung Tau": "Southeast",
    "Long An": "Mekong River Delta",
    "Tien Giang": "Mekong River Delta",
    "Ben Tre": "Mekong River Delta",
    "Tra Vinh": "Mekong River Delta",
    "Vinh Long": "Mekong River Delta",
    "Dong Thap": "Mekong River Delta",
    "An Giang": "Mekong River Delta",
    "Kien Giang": "Mekong River Delta",
    "Hau Giang": "Mekong River Delta",
    "Soc Trang": "Mekong River Delta",
    "Bac Lieu": "Mekong River Delta",
    "Ca Mau": "Mekong River Delta",
}


def normalize_name(raw_name):
    """Chuẩn hóa tên tỉnh: bỏ dấu, bỏ ký tự đặc biệt."""
    import unicodedata

    # Bỏ footnote references [1], [a], etc.
    clean = raw_name.strip()
    while "[" in clean:
        start = clean.index("[")
        end = clean.index("]", start) + 1 if "]" in clean[start:] else len(clean)
        clean = clean[:start] + clean[end:]
    clean = clean.strip()

    # Chuyển dấu tiếng Việt → ASCII gần nhất
    nfkd = unicodedata.normalize("NFKD", clean)
    ascii_name = "".join(c for c in nfkd if not unicodedata.combining(c))

    # Xử lý các trường hợp đặc biệt
    replacements = {
        "Đ": "D", "đ": "d",
        "Ð": "D",
    }
    for old, new in replacements.items():
        ascii_name = ascii_name.replace(old, new)

    # Chuẩn hóa khoảng trắng
    ascii_name = " ".join(ascii_name.split())

    return ascii_name


def parse_number(text):
    """Chuyển chuỗi số có dấu phẩy/chấm thành số."""
    clean = text.strip().replace(",", "").replace("\xa0", "")
    # Bỏ footnote
    while "[" in clean:
        start = clean.index("[")
        end = clean.index("]", start) + 1 if "]" in clean[start:] else len(clean)
        clean = clean[:start] + clean[end:]
    clean = clean.strip()
    try:
        return int(float(clean))
    except ValueError:
        return None


def parse_float(text):
    """Chuyển chuỗi số thực."""
    clean = text.strip().replace(",", "").replace("\xa0", "")
    while "[" in clean:
        start = clean.index("[")
        end = clean.index("]", start) + 1 if "]" in clean[start:] else len(clean)
        clean = clean[:start] + clean[end:]
    clean = clean.strip()
    try:
        return round(float(clean), 1)
    except ValueError:
        return None


def crawl_from_wikipedia():
    """Crawl dữ liệu dân số từ Wikipedia."""
    if requests is None or BeautifulSoup is None:
        print("[LỖI] Không có thư viện cần thiết để crawl.")
        return None

    print(f"[1/3] Đang tải trang: {WIKI_URL}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (BigDataProject/1.0; Educational)"
        }
        response = requests.get(WIKI_URL, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[LỖI] Không thể tải trang Wikipedia: {e}")
        return None

    print("[2/3] Đang phân tích bảng HTML...")
    soup = BeautifulSoup(response.text, "html.parser")

    # Tìm bảng đầu tiên có cả "population" và "area"
    tables = soup.find_all("table", class_="wikitable")
    if not tables:
        print("[LỖI] Không tìm thấy bảng wikitable trên trang.")
        return None

    target_table = None
    for table in tables:
        header_row = table.find("tr")
        if header_row:
            header_text = header_row.get_text().lower()
            if "province" in header_text and "population" in header_text:
                target_table = table
                break

    if target_table is None:
        print("[LỖI] Không tìm thấy bảng dân số phù hợp.")
        return None

    rows = target_table.find_all("tr")
    if len(rows) < 3:
        print("[LỖI] Bảng không đủ dữ liệu.")
        return None

    # Cấu trúc bảng Wikipedia hiện tại:
    # Row 0: Header chính — Province/city, Number, Center, Area, Population, Density, Admin divisions, Region
    # Row 1: Sub-header — Communes, Wards, Special (cho cột Admin divisions)
    # Row 2+: Dữ liệu — có thể 9 hoặc 10 cột (Region dùng rowspan)
    # Cột dữ liệu: 0=Name, 1=Number, 2=Center, 3=Area, 4=Population, 5=Density, 6=Communes, 7=Wards, 8=Special, [9=Region]

    NAME_IDX = 0
    AREA_IDX = 3
    POP_IDX = 4
    DENSITY_IDX = 5

    print(f"  Cột: name={NAME_IDX}, area={AREA_IDX}, pop={POP_IDX}, density={DENSITY_IDX}")

    # Parse từng hàng dữ liệu (bắt đầu từ row 2, bỏ qua header và sub-header)
    results = []
    current_region = "Unknown"
    region_rows_remaining = 0

    for row in rows[2:]:
        cells = row.find_all(["td", "th"])
        if len(cells) < 6:
            continue

        # Lấy tên tỉnh
        raw_name = cells[NAME_IDX].get_text().strip()

        # Bỏ hậu tố " province" / " city"
        clean_name = raw_name
        for suffix in [" province", " city", " Province", " City"]:
            if clean_name.endswith(suffix):
                clean_name = clean_name[:-len(suffix)]

        name = normalize_name(clean_name)

        # Bỏ qua hàng tổng hoặc hàng rỗng
        if not name or name.lower() in ("total", "vietnam", "sum", ""):
            continue

        # Parse số liệu
        population = parse_number(cells[POP_IDX].get_text())
        area = parse_float(cells[AREA_IDX].get_text())
        density = parse_number(cells[DENSITY_IDX].get_text())

        # Kiểm tra xem hàng có cột Region hay không (do rowspan)
        # Nếu có 10 cột → cột cuối là Region mới
        if len(cells) >= 10:
            region_cell = cells[-1]
            region_text = normalize_name(region_cell.get_text().strip())
            if region_text:
                current_region = region_text
            # Xem rowspan để biết bao nhiêu hàng tiếp theo dùng region này
            rowspan = region_cell.get("rowspan")
            if rowspan:
                try:
                    region_rows_remaining = int(rowspan) - 1
                except ValueError:
                    region_rows_remaining = 0
        else:
            # Không có cột region → dùng region hiện tại
            if region_rows_remaining > 0:
                region_rows_remaining -= 1

        # Ưu tiên region từ bảng, fallback sang REGION_MAP
        region = current_region
        if region == "Unknown" or not region:
            region = REGION_MAP.get(name, "Unknown")

        # Tính density nếu chưa có
        if density is None and population and area and area > 0:
            density = round(population / area)

        if population and area:
            results.append({
                "province": name,
                "population": population,
                "area": area,
                "density": density if density else 0,
                "region": region,
            })

    print(f"  Tìm thấy {len(results)} tỉnh/thành phố.")

    if len(results) < 10:
        print(f"[CẢNH BÁO] Chỉ tìm được {len(results)} tỉnh, có thể cấu trúc Wikipedia đã thay đổi.")
        return None

    return results


def load_fallback():
    """Tải dữ liệu fallback từ file sample."""
    if not SAMPLE_FILE.exists():
        print(f"[LỖI] Không tìm thấy file fallback: {SAMPLE_FILE}")
        return None

    print(f"[FALLBACK] Đang tải dữ liệu mẫu từ: {SAMPLE_FILE}")
    results = []
    with open(SAMPLE_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append({
                "province": row["province"].strip(),
                "population": int(row["population"]),
                "area": float(row["area"]),
                "density": int(row["density"]),
                "region": row["region"].strip(),
            })
    print(f"  Đã tải {len(results)} tỉnh/thành từ file mẫu.")
    return results


def save_csv(data, output_path):
    """Lưu dữ liệu ra file CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ["province", "population", "area", "density", "region"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(f"[OK] Đã lưu {len(data)} dòng -> {output_path}")


def main():
    """Hàm chính: crawl dân số hoặc dùng fallback."""
    print("=" * 50)
    print("  CRAWL POPULATION — Dữ liệu dân số Việt Nam")
    print("=" * 50)
    print()

    # Bước 1: Thử crawl từ Wikipedia
    data = crawl_from_wikipedia()

    # Bước 2: Nếu crawl thất bại, dùng fallback
    if data is None:
        print()
        print("[CẢNH BÁO] Crawl thất bại. Chuyển sang dữ liệu mẫu.")
        data = load_fallback()

    # Bước 3: Kiểm tra dữ liệu
    if data is None or len(data) == 0:
        print("[LỖI NGHIÊM TRỌNG] Không có dữ liệu nào. Dừng chương trình.")
        sys.exit(1)

    # Bước 4: Lưu file
    print()
    save_csv(data, RAW_OUTPUT)

    # Bước 5: Tóm tắt
    print()
    print("=" * 50)
    print("  TÓM TẮT")
    print("=" * 50)
    print(f"  Số tỉnh/thành: {len(data)}")
    print(f"  Output file:    {RAW_OUTPUT}")
    print(f"  Columns:        province, population, area, density, region")

    # Hiển thị 5 dòng đầu
    print()
    print("  5 dòng đầu tiên:")
    print(f"  {'province':<20} {'population':>12} {'area':>10} {'density':>8} {'region'}")
    print("  " + "-" * 70)
    for row in data[:5]:
        print(f"  {row['province']:<20} {row['population']:>12,} {row['area']:>10.1f} {row['density']:>8,} {row['region']}")
    print()


if __name__ == "__main__":
    main()
