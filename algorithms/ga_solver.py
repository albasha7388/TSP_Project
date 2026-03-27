import numpy as np
import random
from typing import List, Tuple
from algorithms.base_solver import BaseSolver
from core.city import City
from core.solution import Solution
from core.distance_matrix import DistanceMatrix

class GASolver(BaseSolver):
    def __init__(self, cities: List[City], config: dict):
        super().__init__(cities, config)
        
        # معاملات GA
        self.pop_size = config.get('pop_size', 100)
        self.n_generations = config.get('n_generations', 500)
        self.pc = config.get('pc', 0.8)      # احتمال التقاطع
        self.pm = config.get('pm', 0.02)     # احتمال الطفرة
        self.tournament_k = config.get('tournament_k', 3) # حجم البطولة
        
        self.n_cities = len(cities)
        self.dist_matrix = DistanceMatrix(cities)
        
        # تهيئة السكان الأوليين (Population)
        # كل فرد هو قائمة ترتيب (Permutation) لمؤشرات المدن
        self.population = [list(range(self.n_cities)) for _ in range(self.pop_size)]
        for individual in self.population:
            random.shuffle(individual)
            
        self.fitness_scores = []

    def solve(self) -> Solution:
        best_solution_overall = None
        best_cost_overall = float('inf')
        
        for gen in range(self.n_generations):
            # 1. حساب اللياقة (التكلفة) لكل فرد
            costs = [self.dist_matrix.calculate_path_cost(ind) for ind in self.population]
            
            # تحديث الأفضل العام
            min_cost_idx = np.argmin(costs)
            if costs[min_cost_idx] < best_cost_overall:
                best_cost_overall = costs[min_cost_idx]
                best_solution_overall = Solution(self.cities, self.population[min_cost_idx])
            
            self.history.append(best_cost_overall)
            
            if (gen + 1) % 50 == 0:
                print(f"Gen {gen+1}/{self.n_generations} - Best Cost: {best_cost_overall:.2f}")

            # 2. الاختيار (Selection) - Tournament Selection
            new_population = []
            
            # حفظ أفضل فرد (Elitism) لضمان عدم فقدان الحل الأفضل
            elite = self.population[min_cost_idx]
            new_population.append(elite[:])
            
            while len(new_population) < self.pop_size:
                parent1 = self._tournament_selection(costs)
                parent2 = self._tournament_selection(costs)
                
                child1, child2 = self._crossover(parent1, parent2)
                
                if random.random() < self.pm:
                    child1 = self._mutate(child1)
                if random.random() < self.pm:
                    child2 = self._mutate(child2)
                    
                new_population.append(child1)
                if len(new_population) < self.pop_size:
                    new_population.append(child2)
            
            self.population = new_population[:self.pop_size]
            
        return best_solution_overall

    def _tournament_selection(self, costs: List[float]) -> List[int]:
        """اختيار فرد عبر بطولة صغيرة"""
        indices = random.sample(range(self.pop_size), self.tournament_k)
        # اختيار الفرد ذو أقل تكلفة (أفضل لياقة) بين المشاركين
        best_idx = min(indices, key=lambda i: costs[i])
        return self.population[best_idx][:]

    def _crossover(self, p1: List[int], p2: List[int]) -> Tuple[List[int], List[int]]:
        """Order Crossover (OX1)"""
        if random.random() > self.pc:
            return p1[:], p2[:]
            
        size = self.n_cities
        a, b = sorted(random.sample(range(size), 2))
        
        # إنشاء أطفال فارغة
        c1 = [-1] * size
        c2 = [-1] * size
        
        # نسخ القسم الأوسط من الآباء
        c1[a:b+1] = p1[a:b+1]
        c2[a:b+1] = p2[a:b+1]
        
        # ملء الباقي بالترتيب من الوالد الآخر مع تجنب التكرار
        def fill_child(child, parent):
            current_idx = (b + 1) % size
            parent_idx = (b + 1) % size
            while -1 in child:
                gene = parent[parent_idx]
                if gene not in child:
                    child[current_idx] = gene
                    current_idx = (current_idx + 1) % size
                parent_idx = (parent_idx + 1) % size
                
        fill_child(c1, p2)
        fill_child(c2, p1)
        
        return c1, c2

    def _mutate(self, individual: List[int]) -> List[int]:
        """Swap Mutation: تبديل موقع مدينتين عشوائيتين"""
        idx1, idx2 = random.sample(range(self.n_cities), 2)
        individual[idx1], individual[idx2] = individual[idx2], individual[idx1]
        return individual

    def reset(self):
        super().reset()
        self.population = [list(range(self.n_cities)) for _ in range(self.pop_size)]
        for ind in self.population:
            random.shuffle(ind)