import math

class City:
    def __init__(self, id: int, x: float, y: float):
        self.id = id
        self.x = x
        self.y = y

    def distance_to(self, other_city: 'City') -> float:
        """حساب المسافة الإقليدية بين مدينتين"""
        dx = self.x - other_city.x
        dy = self.y - other_city.y
        return math.sqrt(dx*dx + dy*dy)

    def __repr__(self):
        return f"City({self.id}, {self.x:.2f}, {self.y:.2f})"