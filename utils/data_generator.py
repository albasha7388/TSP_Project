import random
import csv
import os
from typing import List
from core.city import City

class DataGenerator:
    @staticmethod
    def generate_random_cities(num_cities: int, seed: int = 42, width: int = 100, height: int = 100) -> List[City]:
        """
        يولد عدداً محدداً من المدن بإحداثيات عشوائية ضمن نطاق معين.
        
        Args:
            num_cities: عدد المدن المطلوب.
            seed: بذرة العشوائية (لتكرار نفس النتائج لاحقاً للمقارنة العادلة).
            width, height: أبعاد الخريطة الافتراضية.
            
        Returns:
            قائمة بكائنات City.
        """
        random.seed(seed)
        cities = []
        
        for i in range(num_cities):
            x = random.uniform(0, width)
            y = random.uniform(0, height)
            cities.append(City(id=i, x=x, y=y))
            
        return cities

    @staticmethod
    def save_cities_to_csv(cities: List[City], file_path: str):
        """حفظ المدن المولدة في ملف CSV للاستخدام لاحقاً"""
        # التأكد من وجود المجلد
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'x', 'y'])
            for city in cities:
                writer.writerow([city.id, city.x, city.y])
        
        print(f"✅ Generated and saved {len(cities)} cities to {file_path}")

    @staticmethod
    def load_or_generate(file_path: str, num_cities: int = None, seed: int = 42) -> List[City]:
        """
        دالة ذكية: تحاول تحميل المدن من الملف، إذا لم يوجد تقوم بتوليدها وحفظها.
        مفيد جداً لضمان أن التجارب المختلفة تستخدم نفس المدن بالضبط.
        """
        if os.path.exists(file_path):
            from utils.data_loader import load_cities_from_csv
            return load_cities_from_csv(file_path)
        else:
            if num_cities is None:
                raise ValueError("عدد المدن مطلوب للتوليد لأن الملف غير موجود.")
            
            cities = DataGenerator.generate_random_cities(num_cities, seed=seed)
            DataGenerator.save_cities_to_csv(cities, file_path)
            return cities