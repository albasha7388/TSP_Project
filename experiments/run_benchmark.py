# ==========================================
# STEP 1: FIX PYTHON PATH (MUST BE FIRST)
# ==========================================
import os
import sys

# ✅ إضافة هذا الكود لحل مشكلة المسار BEFORE any other imports
# يضيف المجلد الرئيسي للمشروع (TSP_Project) إلى مسار بحث بايثون
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)


import os
import time
import csv
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
from tqdm import tqdm

# استيراد مكونات المشروع
from utils.data_loader import load_data_auto
from utils.data_generator import DataGenerator
from algorithms.aco_solver import ACOSolver
from algorithms.ga_solver import GASolver
from algorithms.pso_solver import PSOSolver
from visualization.convergence_analyzer import ConvergenceAnalyzer
import matplotlib.pyplot as plt

# ==========================================
# إعدادات التجربة
# ==========================================
EXPERIMENT_CONFIG = {
    'output_dir': 'data/results',
    'runs_per_scenario': 5, 
    'scenarios': [
        # {'type': 'random', 'n_cities': 20, 'seed_start': 0},
        {'type': 'file', 'path': 'data/instances/yemen.csv'}, 
        {'type': 'file', 'path': 'data/instances/sample_cities.csv'},
    ],
    'algorithms': {
        'ACO': {'class': ACOSolver, 'config': {'n_ants': 50, 'n_iterations': 150, 'alpha': 1.0, 'beta': 2.0, 'rho': 0.5, 'q': 100}},
        'GA': {'class': GASolver, 'config': {'pop_size': 100, 'n_generations': 200, 'pc': 0.8, 'pm': 0.02}},
        'PSO': {'class': PSOSolver, 'config': {'swarm_size': 50, 'n_iterations': 200, 'w': 0.7, 'c1': 1.5, 'c2': 1.5}}
    }
}

class BenchmarkRunner:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results_data = []
        
        # إنشاء مجلد النتائج مع طابع زمني فريد لتجنب الكتابة فوق الملفات القديمة
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.session_folder = os.path.join(config['output_dir'], f"session_{timestamp}")
        os.makedirs(self.session_folder, exist_ok=True)
        
        print(f"📂 Results will be saved in: {self.session_folder}")

    def run_single_run(self, scenario_name: str, algo_name: str, algo_class: type, algo_config: dict, cities: List, run_id: int) -> Dict:
        solver = algo_class(cities, algo_config)
        start_time = time.perf_counter()
        best_solution = solver.solve()
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        final_cost = best_solution.total_distance
        
        return {
            'Scenario': scenario_name,
            'Algorithm': algo_name,
            'Run_ID': run_id,
            'Num_Cities': len(cities),
            'Final_Cost': final_cost,
            'Execution_Time_Sec': execution_time,
            'Status': 'Completed'
        }

    def run_all_experiments(self):
        print("🚀 Starting Comprehensive Benchmark Suite...")
        
        total_runs = len(self.config['scenarios']) * len(self.config['algorithms']) * self.config['runs_per_scenario']
        
        with tqdm(total=total_runs, desc="Overall Progress", unit="run") as pbar:
            for scenario in self.config['scenarios']:
                scenario_type = scenario.get('type', 'random')
                scenario_label = ""
                base_cities = []

                if scenario_type == 'random':
                    n_cities = scenario['n_cities']
                    seed_start = scenario['seed_start']
                    base_cities = DataGenerator.generate_random_cities(n_cities, seed=seed_start)
                    scenario_label = f"Random-{n_cities}"
                elif scenario_type == 'file':
                    file_path = scenario['path']
                    if not os.path.exists(file_path):
                        pbar.update(len(self.config['algorithms']) * self.config['runs_per_scenario'])
                        continue
                    base_cities = load_data_auto(file_path)
                    if not base_cities:
                        pbar.update(len(self.config['algorithms']) * self.config['runs_per_scenario'])
                        continue
                    scenario_label = f"File-{os.path.basename(file_path)}"
                
                if not base_cities: continue

                for algo_name, algo_info in self.config['algorithms'].items():
                    for run_idx in range(self.config['runs_per_scenario']):
                        try:
                            result = self.run_single_run(
                                scenario_name=scenario_label,
                                algo_name=algo_name,
                                algo_class=algo_info['class'],
                                algo_config=algo_info['config'],
                                cities=base_cities, 
                                run_id=run_idx + 1
                            )
                            self.results_data.append(result)
                            pbar.update(1)
                        except Exception as e:
                            print(f"❌ Error in {algo_name}: {e}")
                            pbar.update(1)

        if self.results_data:
            self.save_organized_results()
            self.generate_human_readable_summary()
            self.plot_benchmark_charts()
        else:
            print("⚠️ No results generated.")

    def save_organized_results(self):
        """حفظ النتائج في ملف CSV منظم جداً بأعمدة واضحة"""
        # تحويل القائمة إلى DataFrame لترتيب الأعمدة وتنسيقها
        df = pd.DataFrame(self.results_data)
        
        # إعادة ترتيب الأعمدة لتكون منطقية للقراءة
        ordered_columns = ['Scenario', 'Algorithm', 'Run_ID', 'Num_Cities', 'Final_Cost', 'Execution_Time_Sec', 'Status']
        df = df[ordered_columns]
        
        # تقريب الأرقام العشرية لسهولة القراءة (4 خانات عشرية)
        df['Final_Cost'] = df['Final_Cost'].round(4)
        df['Execution_Time_Sec'] = df['Execution_Time_Sec'].round(4)
        
        filename = os.path.join(self.session_folder, 'detailed_results.csv')
        df.to_csv(filename, index=False)
        print(f"✅ Organized data saved to: {filename}")
        
        return df

    def generate_human_readable_summary(self):
        """إنشاء ملف نصي وجدول CSV ملخص يسهل قراءته بالعين"""
        df = pd.DataFrame(self.results_data)
        
        # حساب الإحصائيات: المتوسط، الانحراف المعياري، الأفضل، الأسوأ
        summary = df.groupby(['Scenario', 'Algorithm']).agg(
            Avg_Cost=('Final_Cost', 'mean'),
            Std_Dev=('Final_Cost', 'std'),
            Best_Cost=('Final_Cost', 'min'),
            Avg_Time=('Execution_Time_Sec', 'mean'),
            Runs=('Run_ID', 'count')
        ).round(4)
        
        # إضافة عمود لتحديد "الأفضل تكلفة" و "الأسرع وقت" لكل سيناريو
        # هذه الخطوة تجعل التقرير واضحاً جداً
        summary['Best_In_Cost'] = summary.groupby(level=0)['Avg_Cost'].transform(lambda x: x == x.min()).map({True: '🏆 Winner', False: ''})
        summary['Fastest_In_Time'] = summary.groupby(level=0)['Avg_Time'].transform(lambda x: x == x.min()).map({True: '⚡ Fastest', False: ''})
        
        # حفظ الملخص كـ CSV
        summary_file = os.path.join(self.session_folder, 'summary_report.csv')
        summary.to_csv(summary_file)
        
        # حفظ ملخص نصي منسق (Table Format) للقراءة المباشرة
        txt_file = os.path.join(self.session_folder, 'summary_report.txt')
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("="*100 + "\n")
            f.write("TSP BENCHMARK SUMMARY REPORT\n")
            f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*100 + "\n\n")
            
            # تحويل الـ DataFrame لنص منسق
            f.write(summary.to_string())
            
            f.write("\n\n" + "="*100 + "\n")
            f.write("LEGEND:\n")
            f.write("🏆 Winner = Lowest Average Cost for this scenario\n")
            f.write("⚡ Fastest = Lowest Average Execution Time for this scenario\n")
            f.write("="*100 + "\n")
            
        print(f"📊 Human-readable summary saved to: {txt_file}")
        print("\n--- Quick Summary Preview ---")
        print(summary.to_string())
        print("-----------------------------\n")

    def plot_benchmark_charts(self):
        """توليد رسوم بيانية وحفظها في نفس المجلد"""
        df = pd.DataFrame(self.results_data)
        analyzer = ConvergenceAnalyzer()
        
        # 1. Boxplot للتكلفة
        plt.figure(figsize=(12, 8))
        # تجميع البيانات لعرض واضح
        plot_data = {}
        for (scenario, algo), group in df.groupby(['Scenario', 'Algorithm']):
            key = f"{algo}\n({scenario})"
            plot_data[key] = group['Final_Cost'].tolist()
            
        # استخدام seaborn لرسم أجمل
        import seaborn as sns
        sns.boxplot(data=pd.DataFrame({k: pd.Series(v) for k, v in plot_data.items()}), palette="Set2")
        plt.title("Final Cost Distribution Comparison (Lower is Better)", fontsize=14, fontweight='bold')
        plt.ylabel("Cost (Distance)")
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(self.session_folder, 'cost_comparison_boxplot.png'), dpi=300)
        plt.close()
        
        # 2. Bar Chart للوقت
        plt.figure(figsize=(12, 6))
        time_stats = df.groupby(['Scenario', 'Algorithm'])['Execution_Time_Sec'].mean().unstack()
        time_stats.plot(kind='bar', figsize=(12, 6), rot=0, colormap='viridis')
        plt.title("Average Execution Time by Scenario and Algorithm", fontsize=14, fontweight='bold')
        plt.ylabel("Time (seconds)")
        plt.xlabel("Scenario")
        plt.legend(title='Algorithm')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(self.session_folder, 'time_comparison_bar.png'), dpi=300)
        plt.close()
        
        print(f"🖼️ Charts saved to: {self.session_folder}")

if __name__ == "__main__":
    runner = BenchmarkRunner(EXPERIMENT_CONFIG)
    runner.run_all_experiments()