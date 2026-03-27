from abc import ABC, abstractmethod
from typing import List, Optional
from core.city import City
from core.solution import Solution

class BaseSolver(ABC):
    def __init__(self, cities: List[City], config: dict):
        """
        cities: قائمة المدن المشكلة.
        config: قاموس يحتوي على المعاملات (مثل عدد الأجيال، حجم المجتمع، إلخ).
        """
        self.cities = cities
        self.config = config
        self.best_solution: Optional[Solution] = None
        self.history: List[float] = [] # لتخزين أفضل تكلفة في كل تكرار

    @abstractmethod
    def solve(self) -> Solution:
        """
        الدالة الرئيسية لتشغيل الخوارزمية.
        يجب أن ترجع كائن Solution واحد يمثل أفضل حل وجدته.
        """
        pass

    def get_history(self) -> List[float]:
        """إرجاع سجل التقارب (أفضل تكلفة في كل خطوة)"""
        return self.history

    def reset(self):
        """إعادة تعيين حالة الخوارزمية لتشغيلها مرة أخرى بنفس المعاملات"""
        self.best_solution = None
        self.history = []