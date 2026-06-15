"""
crawl_population.py — Thu thập dữ liệu dân số các tỉnh/thành Việt Nam từ Wikipedia.
Nếu crawl thất bại, dùng dữ liệu mẫu có sẵn trong script.

Output: dataset/raw/population_raw.csv
Columns: province,population,area,density,region
"""

import csv
import sys
import unicodedata
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
    print("[CANH BAO] Thieu thu vien requests hoac beautifulsoup4.")
    print("Chay: pip install requests beautifulsoup4")
    requests = None
    BeautifulSoup = None

# Đường dẫn — tự tính từ vị trí file, không dùng đường dẫn cá nhân
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RAW_OUTPUT = PROJECT_ROOT / "dataset" / "raw" / "population_raw.csv"

# URL nguồn dữ liệu
WIKI_URL = "https://en.wikipedia.org/wiki/Provinces_of_Vietnam"

# Dữ liệu mẫu — dùng khi crawl thất bại (20 tỉnh/thành)
FALLBACK_DATA = [
    {"province": "Ha Noi", "population": 8435700, "area": 3358.6, "density": 2511, "region": "Red River Delta"},
    {"province": "Ho Chi Minh", "population": 9205000, "area": 2061.2, "density": 4466, "region": "Southeast"},
    {"province": "Da Nang", "population": 1195500, "area": 1284.9, "density": 930, "region": "South Central Coast"},
    {"province": "Hai Phong", "population": 2072000, "area": 1561.8, "density": 1327, "region": "Red River Delta"},
    {"province": "Can Tho", "population": 1248000, "area": 1401.6, "density": 891, "region": "Mekong River Delta"},
    {"province": "Binh Duong", "population": 2577000, "area": 2694.4, "density": 957, "region": "Southeast"},
    {"province": "Dong Nai", "population": 3168000, "area": 5907.2, "density": 536, "region": "Southeast"},
    {"province": "Quang Ninh", "population": 1327000, "area": 6178.8, "density": 215, "region": "Red River Delta"},
    {"province": "Thanh Hoa", "population": 3645000, "area": 11116.3, "density": 328, "region": "North Central Coast"},
    {"province": "Nghe An", "population": 3410000, "area": 16493.7, "density": 207, "region": "North Central Coast"},
    {"province": "Khanh Hoa", "population": 1260000, "area": 5137.8, "density": 245, "region": "South Central Coast"},
    {"province": "Lam Dong", "population": 1310000, "area": 9773.5, "density": 134, "region": "Central Highlands"},
    {"province": "Bac Ninh", "population": 1426000, "area": 822.7, "density": 1733, "region": "Red River Delta"},
    {"province": "Thua Thien Hue", "population": 1135000, "area": 5033.2, "density": 226, "region": "North Central Coast"},
    {"province": "Long An", "population": 1720000, "area": 4494.9, "density": 383, "region": "Mekong River Delta"},
    {"province": "An Giang", "population": 1908000, "area": 3536.8, "density": 539, "region": "Mekong River Delta"},
    {"province": "Dak Lak", "population": 1920000, "area": 13125.4, "density": 146, "region": "Central Highlands"},
    {"province": "Gia Lai", "population": 1530000, "area": 15536.9, "density": 98, "region": "Central Highlands"},
    {"province": "Ba Ria Vung Tau", "population": 1180000, "area": 1989.5, "density": 593, "region": "Southeast"},
    {"province": "Thai Nguyen", "population": 1310000, "area": 3536.4, "density": 370, "region": "Northern Midlands"},
]

# Bảng ánh xạ tỉnh → vùng (dùng khi crawl từ Wikipedia)
REGION_MAP = {
    "Ha Noi": "Red River Delta", "Ho Chi Minh": "Southeast",
    "Hai Phong": "Red River Delta", "Da Nang": "South Central Coast",
    "Can Tho": "Mekong River Delta", "Cao Bang": "Northeast",
    "Lang Son": "Northeast", "Bac Kan": "Northeast",
    "Tuyen Quang": "Northeast", "Lao Cai": "Northwest",
    "Dien Bien": "Northwest", "Lai Chau": "Northwest",
    "Son La": "Northwest", "Yen Bai": "Northeast",
    "Hoa Binh": "Northwest", "Thai Nguyen": "Northeast",
    "Quang Ninh": "Red River Delta", "Bac Giang": "Northeast",
    "Phu Tho": "Northeast", "Vinh Phuc": "Red River Delta",
    "Bac Ninh": "Red River Delta", "Hai Duong": "Red River Delta",
    "Hung Yen": "Red River Delta", "Ha Nam": "Red River Delta",
    "Nam Dinh": "Red River Delta", "Thai Binh": "Red River Delta",
    "Ninh Binh": "Red River Delta", "Thanh Hoa": "North Central Coast",
    "Nghe An": "North Central Coast", "Ha Tinh": "North Central Coast",
    "Quang Binh": "North Central Coast", "Quang Tri": "North Central Coast",
    "Thua Thien Hue": "North Central Coast", "Quang Nam": "South Central Coast",
    "Quang Ngai": "South Central Coast", "Binh Dinh": "South Central Coast",
    "Phu Yen": "South Central Coast", "Khanh Hoa": "South Central Coast",
    "Ninh Thuan": "South Central Coast", "Binh Thuan": "South Central Coast",
    "Kon Tum": "Central Highlands", "Gia Lai": "Central Highlands",
    "Dak Lak": "Central Highlands", "Dak Nong": "Central Highlands",
    "Lam Dong": "Central Highlands", "Binh Phuoc": "Southeast",
    "Tay Ninh": "Southeast", "Binh Duong": "Southeast",
    "Dong Nai": "Southeast", "Ba Ria Vung Tau": "Southeast",
    "Long An": "Mekong River Delta", "Tien Giang": "Mekong River Delta",
    "Ben Tre": "Mekong River Delta", "Tra Vinh": "Mekong River Delta",
    "Vinh Long": "Mekong River Delta", "Dong Thap": "Mekong River Delta",
    "An Giang": "Mekong River Delta", "Kien Giang": "Mekong River Delta",
    "Hau Giang": "Mekong River Delta", "Soc Trang": "Mekong River Delta",
    "Bac Lieu": "Mekong River Delta", "Ca Mau": "Mekong River Delta",
}


def normalize_name(raw_name):
    """Chuẩn hóa tên tỉnh: bỏ dấu tiếng Việt, bỏ footnote."""
    # Bỏ footnote [1], [a], v.v.
    clean = raw_name.strip()
    while "[" in clean:
        start = clean.index("[")
        end = clean.index("]", start) + 1 if "]" in clean[start:] else len(clean)
        clean = clean[:start] + clean[end:]
    clean = clean.strip()

    # Bỏ dấu tiếng Việt
    nfkd = unicodedata.normalize("NFKD", clean)
    ascii_name = "".join(c for c in nfkd if not unicodedata.combining(c))

    # Xử lý chữ Đ
    ascii_name = ascii_name.replace("Đ", "D").replace("đ", "d").replace("Ð", "D")

    return " ".join(ascii_name.split())


def parse_number(text):
    """Chuyển chuỗi '1,234,567' thành số nguyên."""
    clean = text.strip().replace(",", "").replace("\xa0", "")
    while "[" in clean:
        start = clean.index("[")
        end = clean.index("]", start) + 1 if "]" in clean[start:] else len(clean)
        clean = clean[:start] + clean[end:]
    try:
        return int(float(clean.strip()))
    except ValueError:
        return None


def parse_float(text):
    """Chuyển chuỗi '1,234.5' thành số thực."""
    clean = text.strip().replace(",", "").replace("\xa0", "")
    while "[" in clean:
        start = clean.index("[")
        end = clean.index("]", start) + 1 if "]" in clean[start:] else len(clean)
        clean = clean[:start] + clean[end:]
    try:
        return round(float(clean.strip()), 1)
    except ValueError:
        return None


def crawl_from_wikipedia():
    """Crawl dữ liệu dân số từ bảng Wikipedia."""
    if requests is None or BeautifulSoup is None:
        print("[LOI] Thieu thu vien de crawl.")
        return None

    print(f"[1/3] Dang tai trang: {WIKI_URL}")
    try:
        headers = {"User-Agent": "Mozilla/5.0 (BigDataProject/1.0; Educational)"}
        response = requests.get(WIKI_URL, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[LOI] Khong the tai trang: {e}")
        return None

    print("[2/3] Dang phan tich bang HTML...")
    soup = BeautifulSoup(response.text, "html.parser")

    # Tìm bảng đầu tiên có header "Province" và "Population"
    tables = soup.find_all("table", class_="wikitable")
    target_table = None
    for table in tables:
        header_row = table.find("tr")
        if header_row:
            text = header_row.get_text().lower()
            if "province" in text and "population" in text:
                target_table = table
                break

    if target_table is None:
        print("[LOI] Khong tim thay bang dan so.")
        return None

    rows = target_table.find_all("tr")
    if len(rows) < 3:
        print("[LOI] Bang khong du du lieu.")
        return None

    # Cấu trúc bảng Wikipedia:
    # Row 0: Header — Province/city(0), Number(1), Center(2), Area(3), Population(4), Density(5), ..., Region
    # Row 1: Sub-header (bỏ qua)
    # Row 2+: Dữ liệu — có 9 hoặc 10 cột (Region dùng rowspan)
    results = []
    current_region = "Unknown"

    for row in rows[2:]:
        cells = row.find_all(["td", "th"])
        if len(cells) < 6:
            continue

        # Cột 0: Tên tỉnh
        raw_name = cells[0].get_text().strip()
        for suffix in [" province", " city", " Province", " City"]:
            if raw_name.endswith(suffix):
                raw_name = raw_name[:-len(suffix)]
        name = normalize_name(raw_name)

        if not name or name.lower() in ("total", "vietnam", "sum"):
            continue

        # Cột 3: Diện tích, cột 4: Dân số, cột 5: Mật độ
        area = parse_float(cells[3].get_text())
        population = parse_number(cells[4].get_text())
        density = parse_number(cells[5].get_text())

        # Cột cuối: Region (chỉ xuất hiện ở dòng có rowspan)
        if len(cells) >= 10:
            region_text = normalize_name(cells[-1].get_text().strip())
            if region_text:
                current_region = region_text

        # Ưu tiên REGION_MAP nếu có
        region = REGION_MAP.get(name, current_region)

        # Tính mật độ nếu thiếu
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

    print(f"[3/3] Tim thay {len(results)} tinh/thanh pho.")

    # Trả None nếu quá ít dữ liệu (có thể Wikipedia đổi cấu trúc)
    if len(results) < 10:
        print(f"[CANH BAO] Chi tim duoc {len(results)} tinh — co the cau truc da thay doi.")
        return None

    return results


def save_csv(data, output_path):
    """Lưu danh sách dict ra file CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["province", "population", "area", "density", "region"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"[OK] Da luu {len(data)} dong -> {output_path}")


def main():
    """Hàm chính: crawl dân số hoặc dùng dữ liệu mẫu."""
    print("=" * 55)
    print("  CRAWL POPULATION — Du lieu dan so Viet Nam")
    print("=" * 55)
    print()

    # Bước 1: Thử crawl từ Wikipedia
    data = crawl_from_wikipedia()

    # Bước 2: Nếu thất bại → dùng dữ liệu mẫu trong script
    if data is None:
        print()
        print("[CANH BAO] Crawl that bai. Dung du lieu mau co san.")
        data = FALLBACK_DATA
        print(f"  Da tai {len(data)} tinh/thanh tu du lieu mau.")

    # Bước 3: Lưu file CSV
    print()
    save_csv(data, RAW_OUTPUT)

    # Bước 4: Tóm tắt kết quả
    print()
    print("=" * 55)
    print("  TOM TAT")
    print("=" * 55)
    print(f"  So tinh/thanh: {len(data)}")
    print(f"  Output file:   {RAW_OUTPUT}")
    print(f"  Columns:       province, population, area, density, region")
    print()
    print("  5 dong dau tien:")
    print(f"  {'province':<20} {'population':>12} {'area':>10} {'density':>8} region")
    print("  " + "-" * 70)
    for row in data[:5]:
        print(f"  {row['province']:<20} {row['population']:>12,} {row['area']:>10.1f} {row['density']:>8,} {row['region']}")
    print()


if __name__ == "__main__":
    main()
