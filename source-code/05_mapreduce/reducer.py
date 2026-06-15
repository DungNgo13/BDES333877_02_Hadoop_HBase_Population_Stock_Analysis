#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
reducer.py - MapReduce tim top 10 tinh thanh co dan so dong nhat.
Dau vao: TOP \t population|province|region
Dau ra: rank \t province \t region \t population
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
                pop_str, province, region = value.split("|")
                population = int(pop_str)
                provinces.append({
                    "province": province,
                    "region": region,
                    "population": population
                })
        except ValueError:
            # Bo qua dong loi
            pass
            
    # Sap xep giam dan theo dan so
    sorted_provinces = sorted(provinces, key=lambda x: x["population"], reverse=True)
    
    # Lay top 10
    top_10 = sorted_provinces[:10]
    
    # In ket qua
    for i, item in enumerate(top_10):
        rank = i + 1
        print(f"{rank}\t{item['province']}\t{item['region']}\t{item['population']}")

if __name__ == "__main__":
    main()
