#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
mapper.py - MapReduce tim top 10 tinh thanh co dan so dong nhat.
Dau vao: province,population,area,density,region
Dau ra: TOP \t population|province|region
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
            population_str = parts[1].strip()
            region = parts[4].strip()
            
            try:
                # Chuyen doi dan so sang so nguyen
                population = int(population_str)
                # Phat ra: Key="TOP", Value="population|province|region"
                print(f"TOP\t{population}|{province}|{region}")
            except ValueError:
                # Bo qua dong neu dan so khong phai la so
                pass

if __name__ == "__main__":
    main()
