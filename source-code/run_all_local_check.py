"""
run_all_local_check.py - Kiem tra tong the moi truong local cua du an.
"""
import sys
from pathlib import Path
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def check_file(path_str):
    p = PROJECT_ROOT / path_str
    if p.exists():
        print(f"[OK] Thay file/thu muc: {path_str}")
        return True
    else:
        print(f"[FAIL] Thieu file/thu muc: {path_str}")
        return False

def check_python_module(module_name):
    try:
        __import__(module_name)
        print(f"[OK] Thu vien '{module_name}' da cai dat.")
        return True
    except ImportError:
        print(f"[FAIL] Thieu thu vien '{module_name}'. Chay: pip install {module_name}")
        return False

def main():
    print("=" * 55)
    print("  KIEM TRA MOI TRUONG LOCAL")
    print("=" * 55)
    
    print("\n1. Kiem tra thu vien Python:")
    modules = ["pandas", "requests", "bs4", "happybase", "matplotlib", "flask"]
    for m in modules:
        check_python_module(m)
        
    print("\n2. Kiem tra thu muc du an:")
    dirs = [
        "source-code", "dataset/raw", "dataset/clean", 
        "reports", "refs", "libs", "dataset/sample"
    ]
    for d in dirs:
        check_file(d)
        
    print("\n3. Kiem tra dataset:")
    files = [
        "dataset/clean/population_clean.csv",
        "dataset/clean/stock_clean.csv"
    ]
    for f in files:
        check_file(f)
        
    print("\n[OK] Kiem tra hoan tat. Neu tat ca [OK] thi moi truong san sang!")

if __name__ == "__main__":
    main()
