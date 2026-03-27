# visualization/convergence_analyzer.py
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Dict, Optional

sns.set(style="whitegrid", context="talk")

class ConvergenceAnalyzer:
    def __init__(self):
        pass

    def plot_convergence_curves(self, histories: Dict[str, List[List[float]]], title: str = "Algorithm Convergence Comparison", save_path: Optional[str] = None):
        plt.figure(figsize=(12, 8))
        colors = {'ACO': '#e74c3c', 'GA': '#3498db', 'PSO': '#2ecc71'}
        linestyles = {'ACO': '-', 'GA': '--', 'PSO': '-.'}
        
        for algo_name, runs in histories.items():
            df_runs = pd.DataFrame(runs)
            mean_costs = df_runs.mean(axis=0)
            std_costs = df_runs.std(axis=0)
            iterations = list(range(len(mean_costs)))
            
            color = colors.get(algo_name, 'gray')
            plt.plot(iterations, mean_costs, label=f'{algo_name} (Mean)', color=color, linestyle=linestyles.get(algo_name, '-'), linewidth=2)
            plt.fill_between(iterations, mean_costs - std_costs, mean_costs + std_costs, color=color, alpha=0.2, label=f'{algo_name} (Std Dev)')
        
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel("Iteration / Generation", fontsize=12)
        plt.ylabel("Best Cost (Distance)", fontsize=12)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, which='both', linestyle='--', alpha=0.7)
        
        if save_path:
            plt.savefig(save_path, dpi=300)
        return plt.gcf()

    def plot_boxplot_comparison(self, final_costs: Dict[str, List[float]], title: str = "Final Cost Distribution", save_path: Optional[str] = None):
        plt.figure(figsize=(10, 6))
        
        data = []
        labels = []
        for algo, costs in final_costs.items():
            data.extend(costs)
            labels.extend([algo] * len(costs))
            
        df = pd.DataFrame({'Algorithm': labels, 'Cost': data})
        
        # ✅ التصحيح هنا: إضافة hue و legend=False
        sns.boxplot(x='Algorithm', y='Cost', data=df, palette="Set2", hue='Algorithm', legend=False)
        
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel("Algorithm", fontsize=12)
        plt.ylabel("Final Distance", fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        if save_path:
            plt.savefig(save_path, dpi=300)
        return plt.gcf()