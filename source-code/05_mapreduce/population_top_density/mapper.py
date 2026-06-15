#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
mapper.py - MapReduce tim top 10 tinh thanh co mat do dan so cao nhat.
Dau vao: province,population,area,density,region
Dau ra: TOP \t density|province|region
"""

import sys

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        # Bo qua dong header
        if line.startswith("province,"):
            continue
            
        parts = line.split(",")
        # Kiem tra dong hop le (can it nhat 5 cot)
        if len(parts) >= 5:
            province = parts[0].strip()
            density_str = parts[3].strip()
            region = parts[4].strip()
            
            try:
                # Chuyen doi mat do sang so thuc
                density = float(density_str)
                # Phat ra: Key="TOP", Value="density|province|region"
                print(f"TOP\t{density}|{province}|{region}")
            except ValueError:
                # Bo qua dong neu mat do khong phai la so
                pass

if __name__ == "__main__":
    main()
