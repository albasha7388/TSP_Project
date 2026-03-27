import numpy as np
import random
from typing import List, Tuple, Optional
from algorithms.base_solver import BaseSolver
from core.city import City
from core.solution import Solution
from core.distance_matrix import DistanceMatrix

class ACOSolver(BaseSolver):
    def __init__(self, cities: List[City], config: dict):
        super().__init__(cities, config)
        
        # إعدادات الخوارزمية من ملف التوثيق
        self.n_ants = config.get('n_ants', len(cities))
        self.n_iterations = config.get('n_iterations', 200)
        self.alpha = config.get('alpha', 1.0)      # أهمية الفيرومون
        self.beta = config.get('beta', 2.0)        # أهمية المسافة (Heuristic)
        self.rho = config.get('rho', 0.5)          # معدل تبخر الفيرومون
        self.q = config.get('q', 100)              # كمية الفيرومون المودعة
        
        # تهيئة البيانات الأساسية
        self.n_cities = len(cities)
        self.dist_matrix = DistanceMatrix(cities)
        self.distances = self.dist_matrix.get_full_matrix()
        
        # مصفوفة الفيرومونات (N x N) - تبدأ بقيمة صغيرة موجبة
        self.pheromones = np.ones((self.n_cities, self.n_cities)) * 0.1
        
        # مصفوفة الجاذبية العكسية (1 / distance) لتجنب القسمة على صفر نضيف قيمة صغيرة جداً
        # إذا كانت المسافة 0 (نفس المدينة)، نجعل الجاذبية 0
        with np.errstate(divide='ignore'):
            self.heuristics = 1.0 / self.distances
            self.heuristics[self.heuristics == np.inf] = 0.0

    def solve(self) -> Solution:
        """تشغيل حلقة مستعمرة النمل الرئيسية"""
        best_solution_overall: Optional[Solution] = None
        best_cost_overall = float('inf')
        
        # مؤشرات المدن (0 إلى N-1)
        city_indices = list(range(self.n_cities))

        for iteration in range(self.n_iterations):
            all_solutions_indices = []
            
            # 1. بناء الحلول بواسطة كل نملة
            for _ in range(self.n_ants):
                path = self._construct_solution(city_indices)
                
                # تطبيق تحسين محلي 2-Opt لتحسين المسار فوراً (اختياري لكن موصى به بشدة)
                path = self._local_search_2opt(path)
                
                cost = self.dist_matrix.calculate_path_cost(path)
                all_solutions_indices.append((path, cost))
                
                # تحديث الأفضل العام
                if cost < best_cost_overall:
                    best_cost_overall = cost
                    best_solution_overall = Solution(self.cities, path)
            
            # تسجيل التاريخ للتقارب
            current_best_cost = min(sol[1] for sol in all_solutions_indices)
            self.history.append(current_best_cost)
            
            # 2. تحديث الفيرومونات
            self._update_pheromones(all_solutions_indices)
            
            # طباعة تقدم بسيطة (يمكن إزالتها أو استبدالها بـ tqdm في الـ GUI)
            if (iteration + 1) % 50 == 0:
                print(f"Iteration {iteration+1}/{self.n_iterations} - Best Cost: {best_cost_overall:.2f}")

        if best_solution_overall is None:
            # حالة طارئة (لا ينبغي حدوثها)
            return Solution(self.cities, list(range(self.n_cities)))
            
        return best_solution_overall

    def _construct_solution(self, city_indices: List[int]) -> List[int]:
        """تبني نملة واحدة مساراً كاملاً بناءً على الاحتمالات"""
        unvisited = set(city_indices)
        current_city = random.choice(city_indices) # بدء عشوائي
        unvisited.remove(current_city)
        
        path = [current_city]
        
        while unvisited:
            next_city = self._select_next_city(current_city, unvisited)
            unvisited.remove(next_city)
            path.append(next_city)
            current_city = next_city
            
        return path

    def _select_next_city(self, current: int, unvisited: set) -> int:
        """اختيار المدينة التالية باستخدام قاعدة الاحتمال"""
        probabilities = []
        candidates = list(unvisited)
        
        for candidate in candidates:
            tau = self.pheromones[current][candidate] ** self.alpha
            eta = self.heuristics[current][candidate] ** self.beta
            probabilities.append(tau * eta)
        
        # تطبيع الاحتمالات
        total_prob = sum(probabilities)
        if total_prob == 0:
            return random.choice(candidates) # تجنب القسمة على صفر
            
        probabilities = [p / total_prob for p in probabilities]
        
        # اختيار بناءً على الاحتمال الموزون
        return random.choices(candidates, weights=probabilities, k=1)[0]

    def _update_pheromones(self, solutions: List[Tuple[List[int], float]]):
        """تبخر الفيرومونات القديمة وإضافة الجديد من أفضل الحلول"""
        # 1. التبخر (Evaporation)
        self.pheromones *= (1.0 - self.rho)
        
        # 2. الإيداع (Deposit) - نستخدم فقط أفضل حل في هذه الجولة (Elitism) أو كل النمل
        # هنا نطبق Global Update: فقط أفضل نملة في الجولة تودع فيرومونات (للتقارب الأسرع)
        best_path, best_cost = min(solutions, key=lambda x: x[1])
        
        delta_pheromone = self.q / best_cost
        
        for i in range(len(best_path)):
            u = best_path[i]
            v = best_path[(i + 1) % len(best_path)]
            self.pheromones[u][v] += delta_pheromone
            self.pheromones[v][u] += delta_pheromone # لأن الرسم غير موجه

    def _local_search_2opt(self, path: List[int]) -> List[int]:
        """
        خوارزمية 2-Opt المحلية: تقطع حافتين وتعكس الجزء بينهما إذا أدى ذلك لتقصير المسار.
        تكرر حتى لا يوجد تحسين ممكن.
        """
        improved = True
        best_path = path[:]
        n = len(best_path)
        
        while improved:
            improved = False
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    # إنشاء مسار جديد بعكس الجزء بين i و j
                    new_path = best_path[:i] + best_path[i:j+1][::-1] + best_path[j+1:]
                    
                    old_cost = self.dist_matrix.calculate_path_cost(best_path)
                    new_cost = self.dist_matrix.calculate_path_cost(new_path)
                    
                    if new_cost < old_cost:
                        best_path = new_path
                        improved = True
                        break # ابدأ من جديد بعد أي تحسين
                if improved:
                    break
                    
        return best_path

    def reset(self):
        """إعادة تعيين الخوارزمية لتجربة جديدة"""
        super().reset()
        self.pheromones = np.ones((self.n_cities, self.n_cities)) * 0.1