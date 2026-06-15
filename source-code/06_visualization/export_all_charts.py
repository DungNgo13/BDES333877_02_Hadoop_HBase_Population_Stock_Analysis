"""
export_all_charts.py - Chay tat ca cac script ve bieu do.
"""

import sys
from pathlib import Path
import subprocess

# Dam bao hien thi tieng Viet
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CURRENT_DIR = Path(__file__).resolve().parent

def run_script(script_name):
    """Goi lenh python chay script"""
    script_path = CURRENT_DIR / script_name
    print(f"\n[{script_name}] Dang thuc thi...")
    
    if not script_path.exists():
        print(f"  -> [LOI] Khong tim thay {script_path}")
        return False
        
    try:
        result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
            print(f"  -> [THANH CONG]")
            return True
        else:
            print(f"  -> [LOI] Ma loi: {result.returncode}")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"  -> [LOI] {e}")
        return False

def main():
    print("=" * 55)
    print("  EXPORT ALL CHARTS — Xuat tat ca bieu do")
    print("=" * 55)
    
    success = True
    
    # 1. Chay bieu do dan so
    if not run_script("chart_population.py"):
        success = False
        
    # 2. Chay bieu do chung khoan
    if not run_script("chart_stock.py"):
        success = False
        
    print("=" * 55)
    if success:
        print("  KET LUAN: TAT CA BIEU DO DA DUOC TAO THANH CONG!")
    else:
        print("  KET LUAN: CO LOI XAY RA TRONG QUA TRINH TAO BIEU DO.")

if __name__ == "__main__":
    main()
