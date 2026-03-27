import numpy as np
import random
from typing import List
from algorithms.base_solver import BaseSolver
from core.city import City
from core.solution import Solution
from core.distance_matrix import DistanceMatrix

class PSOSolver(BaseSolver):
    def __init__(self, cities: List[City], config: dict):
        super().__init__(cities, config)
        
        # معاملات PSO
        self.swarm_size = config.get('swarm_size', 50)
        self.n_iterations = config.get('n_iterations', 500)
        self.w = config.get('w', 0.7)       # القصور الذاتي
        self.c1 = config.get('c1', 1.5)     # المعرفي
        self.c2 = config.get('c2', 1.5)     # الاجتماعي
        
        self.n_cities = len(cities)
        self.dist_matrix = DistanceMatrix(cities)
        
        # تهيئة السرب
        # الموقع: قيم عشوائية مستمرة لكل مدينة لكل جسيم
        self.positions = np.random.rand(self.swarm_size, self.n_cities)
        # السرعة: قيم صغيرة عشوائية
        self.velocities = np.random.uniform(-0.1, 0.1, (self.swarm_size, self.n_cities))
        
        # أفضل مواقع شخصية (Pbest) ومواقعها المقابلة في شكل مسار
        self.pbest_positions = self.positions.copy()
        self.pbest_costs = np.full(self.swarm_size, float('inf'))
        
        # أفضل موقع عام (Gbest)
        self.gbest_position = None
        self.gbest_cost = float('inf')
        
        # حساب التكاليف الأولية
        self._evaluate_swarm()

    def _decode_path(self, continuous_values: np.ndarray) -> List[int]:
        """تحويل القيم المستمرة إلى مسار (Permutation) عن طريق الترتيب"""
        return list(np.argsort(continuous_values))

    def _evaluate_swarm(self):
        """حساب تكاليف جميع الجسيمات وتحديث Pbest و Gbest"""
        for i in range(self.swarm_size):
            path = self._decode_path(self.positions[i])
            cost = self.dist_matrix.calculate_path_cost(path)
            
            if cost < self.pbest_costs[i]:
                self.pbest_costs[i] = cost
                self.pbest_positions[i] = self.positions[i].copy()
                
            if cost < self.gbest_cost:
                self.gbest_cost = cost
                self.gbest_position = self.positions[i].copy()

    def solve(self) -> Solution:
        for it in range(self.n_iterations):
            # تحديث السرعة والموقع
            r1, r2 = np.random.rand(2, self.swarm_size, self.n_cities)
            
            # معادلة سرعة PSO
            inertia = self.w * self.velocities
            cognitive = self.c1 * r1 * (self.pbest_positions - self.positions)
            social = self.c2 * r2 * (self.gbest_position - self.positions)
            
            self.velocities = inertia + cognitive + social
            
            # تحديث الموقع
            self.positions += self.velocities
            
            # حدود القيم (اختياري، لكن يحافظ على استقرار الأرقام)
            self.positions = np.clip(self.positions, 0, 1)
            
            # التقييم
            self._evaluate_swarm()
            
            self.history.append(self.gbest_cost)
            
            if (it + 1) % 50 == 0:
                print(f"Iteration {it+1}/{self.n_iterations} - Best Cost: {self.gbest_cost:.2f}")
                
        return Solution(self.cities, self._decode_path(self.gbest_position))

    def reset(self):
        super().reset()
        self.positions = np.random.rand(self.swarm_size, self.n_cities)
        self.velocities = np.random.uniform(-0.1, 0.1, (self.swarm_size, self.n_cities))
        self.pbest_positions = self.positions.copy()
        self.pbest_costs = np.full(self.swarm_size, float('inf'))
        self.gbest_position = None
        self.gbest_cost = float('inf')
        self._evaluate_swarm()