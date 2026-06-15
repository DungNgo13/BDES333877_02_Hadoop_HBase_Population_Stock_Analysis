"""
chart_stock.py - Ve bieu do cho du lieu chung khoan.
Input: dataset/clean/stock_clean.csv
Output: 
- stock_monthly_avg_close.png
- stock_yearly_volume.png
- stock_movement_ratio.png
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
INPUT_FILE = PROJECT_ROOT / "dataset" / "clean" / "stock_clean.csv"

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

def plot_monthly_avg_close(df):
    """Bieu do duong (Line chart): Trung binh gia dong cua theo thang."""
    # Chuyen date thanh datetime
    df["date"] = pd.to_datetime(df["date"])
    df["month_str"] = df["date"].dt.strftime("%Y-%m")
    
    # Nhom theo symbol va thang
    monthly = df.groupby(["symbol", "month_str"])["close_price"].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for symbol in monthly["symbol"].unique():
        sym_data = monthly[monthly["symbol"] == symbol]
        # Sort by month_str
        sym_data = sym_data.sort_values("month_str")
        ax.plot(sym_data["month_str"], sym_data["close_price"], marker="o", label=symbol)
        
    ax.set_title("Trung Bình Giá Đóng Cửa Theo Tháng", fontsize=14)
    ax.set_xlabel("Tháng", fontsize=12)
    ax.set_ylabel("Giá Đóng Cửa (VND)", fontsize=12)
    ax.legend(title="Mã CP")
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    save_plot(fig, "stock_monthly_avg_close.png")
    plt.close(fig)

def plot_yearly_volume(df):
    """Bieu do cot: Tong khoi luong giao dich theo nam."""
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    
    yearly = df.groupby(["symbol", "year"])["volume"].sum().unstack()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    if yearly is not None and not yearly.empty:
        yearly.plot(kind="bar", ax=ax, width=0.7)
        
    ax.set_title("Tổng Khối Lượng Giao Dịch Theo Năm", fontsize=14)
    ax.set_xlabel("Mã Cổ Phiếu", fontsize=12)
    ax.set_ylabel("Khối Lượng (Cổ Phiếu)", fontsize=12)
    ax.legend(title="Năm")
    plt.xticks(rotation=0)
    
    plt.tight_layout()
    save_plot(fig, "stock_yearly_volume.png")
    plt.close(fig)

def plot_movement_ratio(df):
    """Bieu do tron (Pie chart): Ty le tang/giam cua 1 co phieu."""
    symbols = df["symbol"].unique()
    if len(symbols) == 0:
        return
        
    # Chon ma co phieu dau tien de ve (hoac ve tat ca vao subplots, nhung de don gian ta chi ve ma dau tien)
    target_symbol = symbols[0]
    
    sym_data = df[df["symbol"] == target_symbol].copy()
    
    # Phan loai tang/giam/dung gia
    sym_data["movement"] = "Flat"
    sym_data.loc[sym_data["change_value"] > 0, "movement"] = "Up"
    sym_data.loc[sym_data["change_value"] < 0, "movement"] = "Down"
    
    counts = sym_data["movement"].value_counts()
    
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Mau sac tuong ung: Xanh (Up), Do (Down), Vang (Flat)
    color_map = {"Up": "#2ecc71", "Down": "#e74c3c", "Flat": "#f1c40f"}
    colors = [color_map.get(lbl, "#95a5a6") for lbl in counts.index]
    
    ax.pie(counts, labels=counts.index, autopct="%1.1f%%", startangle=90, colors=colors)
    ax.set_title(f"Tỷ Lệ Tăng/Giảm/Đứng Giá - {target_symbol}", fontsize=14)
    
    plt.tight_layout()
    save_plot(fig, "stock_movement_ratio.png")
    plt.close(fig)

def main():
    print("=" * 55)
    print("  VE BIEU DO CHUNG KHOAN")
    print("=" * 55)
    
    if not INPUT_FILE.exists():
        print(f"[LOI] Khong tim thay {INPUT_FILE}.")
        sys.exit(1)
        
    setup_folders()
    
    try:
        df = pd.read_csv(INPUT_FILE)
    except Exception as e:
        print(f"[LOI] Khong the doc file CSV: {e}")
        sys.exit(1)
        
    print("[+] Dang tao bieu do...")
    plot_monthly_avg_close(df)
    plot_yearly_volume(df)
    plot_movement_ratio(df)
    
    print("\n[OK] Hoan tat tao bieu do chung khoan!")

if __name__ == "__main__":
    main()
