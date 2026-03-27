import numpy as np
from typing import List
from .city import City

class DistanceMatrix:
    def __init__(self, cities: List[City]):
        """
        يقوم بحساب مصفوفة المسافات بين جميع أزواج المدن عند الإنشاء.
        Complexity: O(N^2) - يتم مرة واحدة فقط.
        """
        self.n = len(cities)
        self.cities = cities
        # إنشاء مصفوفة فارغة بحجم N x N
        self.matrix = np.zeros((self.n, self.n))
        
        self._compute_matrix()

    def _compute_matrix(self):
        """حساب المسافات الإقليدية وتخزينها في المصفوفة"""
        for i in range(self.n):
            for j in range(i + 1, self.n):
                dist = self.cities[i].distance_to(self.cities[j])
                self.matrix[i][j] = dist
                self.matrix[j][i] = dist # المصفوفة متماثلة (Symmetric)

    def get_distance(self, idx1: int, idx2: int) -> float:
        """إرجاع المسافة بين مدينتين باستخدام مؤشراتهما (Indices) بسرعة O(1)"""
        return self.matrix[idx1][idx2]

    def get_full_matrix(self) -> np.ndarray:
        """إرجاع المصفوفة الكاملة لاستخدامها في الخوارزميات"""
        return self.matrix

    def calculate_path_cost(self, path_indices: List[int]) -> float:
        """
        حساب تكلفة مسار كامل بسرعة باستخدام المصفوفة.
        path_indices: قائمة بمؤشرات المدن (Integers) وليس IDs.
        """
        total_cost = 0.0
        n = len(path_indices)
        
        # استخدام NumPy للفهرسة المتقدمة للسرعة القصوى
        # نجمع المسافة من المدينة i إلى i+1
        for i in range(n - 1):
            total_cost += self.matrix[path_indices[i], path_indices[i+1]]
        
        # إضافة مسافة العودة من آخر مدينة للأولى
        total_cost += self.matrix[path_indices[-1], path_indices[0]]
        
        return total_cost