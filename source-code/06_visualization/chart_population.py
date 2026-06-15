"""
chart_population.py - Ve bieu do cho du lieu dan so.
Input: dataset/clean/population_clean.csv
Output: 
- population_top10.png
- population_density_top10.png
- population_area_scatter.png
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Dam bao hien thi tieng Viet tren Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
INPUT_FILE = PROJECT_ROOT / "dataset" / "clean" / "population_clean.csv"

# 2 thu muc xuat bieu do
OUT_GUI = PROJECT_ROOT / "source-code" / "07_gui" / "static" / "charts"
OUT_REPORT = PROJECT_ROOT / "reports" / "screenshots" / "charts"

def setup_folders():
    """Tao cac thu muc dau ra neu chua co."""
    OUT_GUI.mkdir(parents=True, exist_ok=True)
    OUT_REPORT.mkdir(parents=True, exist_ok=True)

def save_plot(fig, filename):
    """Luu bieu do vao ca 2 thu muc."""
    p1 = OUT_GUI / filename
    p2 = OUT_REPORT / filename
    fig.savefig(p1, bbox_inches="tight", dpi=150)
    fig.savefig(p2, bbox_inches="tight", dpi=150)
    print(f"  -> Da luu: {filename}")

def plot_population_top10(df):
    """Bieu do cot: Top 10 tinh thanh dong dan nhat."""
    top10 = df.sort_values("population", ascending=False).head(10)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(top10["province"], top10["population"] / 1000000, color="skyblue")
    
    ax.set_title("Top 10 Tỉnh Thành Đông Dân Nhất", fontsize=14)
    ax.set_xlabel("Tỉnh / Thành Phố", fontsize=12)
    ax.set_ylabel("Dân Số (Triệu Người)", fontsize=12)
    plt.xticks(rotation=45, ha="right")
    
    # Them label tren cot
    for i, v in enumerate(top10["population"] / 1000000):
        ax.text(i, v + 0.1, f"{v:.1f}", ha="center")
        
    plt.tight_layout()
    save_plot(fig, "population_top10.png")
    plt.close(fig)

def plot_density_top10(df):
    """Bieu do cot ngang: Top 10 tinh thanh co mat do dan so cao nhat."""
    top10 = df.sort_values("density", ascending=False).head(10).iloc[::-1] # Dao nguoc de ve thanh ngang tu tren xuong
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top10["province"], top10["density"], color="salmon")
    
    ax.set_title("Top 10 Tỉnh Thành Có Mật Độ Dân Số Cao Nhất", fontsize=14)
    ax.set_xlabel("Mật Độ (người/km²)", fontsize=12)
    ax.set_ylabel("Tỉnh / Thành Phố", fontsize=12)
    
    plt.tight_layout()
    save_plot(fig, "population_density_top10.png")
    plt.close(fig)

def plot_area_scatter(df):
    """Bieu do phan tan: Moi quan he Dien tich - Dan so."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df["area"], df["population"] / 1000000, alpha=0.6, color="green")
    
    ax.set_title("Mối Quan Hệ Giữa Diện Tích và Dân Số", fontsize=14)
    ax.set_xlabel("Diện Tích (km²)", fontsize=12)
    ax.set_ylabel("Dân Số (Triệu Người)", fontsize=12)
    
    plt.tight_layout()
    save_plot(fig, "population_area_scatter.png")
    plt.close(fig)

def main():
    print("=" * 55)
    print("  VE BIEU DO DAN SO")
    print("=" * 55)
    
    if not INPUT_FILE.exists():
        print(f"[LOI] Khong tim thay {INPUT_FILE}. Vui long kiem tra file raw hoac tao thu muc.")
        sys.exit(1)
        
    setup_folders()
    
    try:
        df = pd.read_csv(INPUT_FILE)
    except Exception as e:
        print(f"[LOI] Khong the doc file CSV: {e}")
        sys.exit(1)
        
    print("[+] Dang tao bieu do...")
    plot_population_top10(df)
    plot_density_top10(df)
    plot_area_scatter(df)
    
    print("\n[OK] Hoan tat tao bieu do dan so!")

if __name__ == "__main__":
    main()
