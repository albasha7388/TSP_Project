from typing import List, Tuple
from .city import City

class Solution:
    def __init__(self, cities: List[City], path: List[int]):
        """
        cities: قائمة كائنات المدن كاملة.
        path: قائمة بمعرفات المدن (IDs) مرتبة حسب زيارة البائع.
              مثال: [0, 2, 1, 3] يعني ابدأ بالمدينة 0 ثم 2 ثم 1 ثم 3 ثم العودة لـ 0.
        """
        self.cities_map = {city.id: city for city in cities}
        self.path = path
        self.total_distance = self.calculate_distance()

    def calculate_distance(self) -> float:
        """حساب المسافة الكلية للمسار الحالي"""
        total_dist = 0.0
        n = len(self.path)
        
        for i in range(n):
            current_id = self.path[i]
            next_id = self.path[(i + 1) % n] # العودة للنقطة الأولى في النهاية
            
            city_a = self.cities_map[current_id]
            city_b = self.cities_map[next_id]
            
            total_dist += city_a.distance_to(city_b)
            
        return total_dist

    def get_route_coordinates(self) -> Tuple[List[float], List[float]]:
        """إرجاع إحداثيات X و Y للرسم البياني"""
        x_coords = []
        y_coords = []
        
        # إضافة المدن حسب الترتيب في المسار
        for city_id in self.path:
            city = self.cities_map[city_id]
            x_coords.append(city.x)
            y_coords.append(city.y)
        
        # إغلاق الدائرة (إضافة نقطة البداية في النهاية للرسم)
        if self.path:
            start_city = self.cities_map[self.path[0]]
            x_coords.append(start_city.x)
            y_coords.append(start_city.y)
            
        return x_coords, y_coords

    def __repr__(self):
        return f"Solution(Distance={self.total_distance:.2f}, Path={self.path})"