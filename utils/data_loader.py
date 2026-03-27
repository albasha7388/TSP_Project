# utils/data_loader.py
import csv
import os
from typing import List
from core.city import City

def load_cities_from_csv(file_path: str) -> List[City]:
    cities = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            # نستخدم enumerate للحصول على index يبدأ من 0 بغض النظر عن محتوى الملف
            for index, row in enumerate(reader):
                city = City(
                    id=index,              # ✅ نجعل الـ ID هو الـ index (0, 1, 2...)
                    x=float(row['x']),
                    y=float(row['y'])
                )
                cities.append(city)
        print(f"✅ Loaded {len(cities)} cities from CSV: {file_path}")
        return cities
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return []

def load_tsplib_file(file_path: str) -> List[City]:
    cities = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        in_node_section = False
        index_counter = 0 # عداد يبدأ من 0
        
        for line in lines:
            line = line.strip()
            if line.startswith("NODE_COORD_SECTION"):
                in_node_section = True
                continue
            if line.startswith("EOF"):
                break
            
            if in_node_section and line:
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        # نتجاهل الجزء الأول (ID الأصلي) ونستخدم العداد الخاص بنا
                        x = float(parts[1])
                        y = float(parts[2])
                        cities.append(City(id=index_counter, x=x, y=y))
                        index_counter += 1
                    except ValueError:
                        continue
        
        if not cities:
            print(f"⚠️ No cities found in {file_path}.")
        else:
            print(f"✅ Loaded {len(cities)} cities from TSPLIB: {file_path}")
            
        return cities
    except Exception as e:
        print(f"❌ Error reading TSPLIB file: {e}")
        return []

def load_data_auto(file_path: str) -> List[City]:
    """
    دالة ذكية تكتشف نوع الملف تلقائياً وتستدعي الدالة المناسبة.
    """
    if not os.path.exists(file_path):
        print(f"❌ File does not exist: {file_path}")
        return []
    
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.csv':
        return load_cities_from_csv(file_path)
    elif ext == '.tsp':
        return load_tsplib_file(file_path)
    else:
        print(f"❌ Unsupported file extension: {ext}. Use .csv or .tsp")
        return []