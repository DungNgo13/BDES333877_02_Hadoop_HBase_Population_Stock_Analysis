#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
reducer.py - MapReduce tim top 10 tinh thanh co mat do dan so cao nhat.
Dau vao: TOP \t density|province|region
Dau ra: rank \t province \t region \t density
"""

import sys

def main():
    # Danh sach de luu tru tat ca cac tinh
    provinces = []
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        try:
            key, value = line.split("\t")
            if key == "TOP":
                density_str, province, region = value.split("|")
                density = float(density_str)
                provinces.append({
                    "province": province,
                    "region": region,
                    "density": density
                })
        except ValueError:
            # Bo qua dong loi
            pass
            
    # Sap xep giam dan theo mat do
    sorted_provinces = sorted(provinces, key=lambda x: x["density"], reverse=True)
    
    # Lay top 10
    top_10 = sorted_provinces[:10]
    
    # In ket qua
    for i, item in enumerate(top_10):
        rank = i + 1
        print(f"{rank}\t{item['province']}\t{item['region']}\t{item['density']}")

if __name__ == "__main__":
    main()
