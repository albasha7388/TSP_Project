import matplotlib.pyplot as plt
import numpy as np
from typing import List, Optional, Tuple
from core.solution import Solution
from core.city import City

class RouteDrawer:
    def __init__(self, figsize: Tuple[int, int] = (10, 8)):
        self.figsize = figsize

    def draw_solution(self, solution: Solution, title: str = "TSP Solution", save_path: Optional[str] = None):
        """
        يرسم مسار حل واحد على خريطة ثنائية الأبعاد.
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # الحصول على الإحداثيات من كائن الحل
        x_coords, y_coords = solution.get_route_coordinates()
        
        # 1. رسم الخطوط (المسار)
        # نستخدم لون متدرج أو لون ثابت مع شفافية
        ax.plot(x_coords, y_coords, 'b-', linewidth=1.5, label='Route', alpha=0.7)
        
        # 2. رسم المدن (النقاط)
        # المدينة الأولى (بداية المسار) بلون مختلف
        ax.scatter(x_coords[0], y_coords[0], c='red', s=100, zorder=5, label='Start City', edgecolors='black')
        ax.scatter(x_coords[1:-1], y_coords[1:-1], c='skyblue', s=50, zorder=3, label='Cities', edgecolors='gray', linewidths=0.5)
        
        # إضافة أرقام للمدن (اختياري، يمكن تعطيله إذا كانت المدن كثيرة)
        if len(solution.path) <= 30:
            for i, city_id in enumerate(solution.path):
                ax.annotate(str(city_id), (x_coords[i], y_coords[i]), textcoords="offset points", xytext=(5, 5), fontsize=8, color='darkblue')

        # تنسيق الرسم
        ax.set_title(f"{title}\nTotal Distance: {solution.total_distance:.2f}", fontsize=14, fontweight='bold')
        ax.set_xlabel("X Coordinate")
        ax.set_ylabel("Y Coordinate")
        ax.legend(loc='best')
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_aspect('equal') # لضمان عدم تشوه الخريطة
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300)
            print(f"✅ Route plot saved to {save_path}")
        
        return fig, ax

    def draw_multiple_solutions(self, solutions: List[Tuple[Solution, str]], title: str = "Comparison of Algorithms", save_path: Optional[str] = None):
        """
        يرسم مسارات متعددة (من خوارزميات مختلفة) في رسوم منفصلة ضمن نفس النافذة للمقارنة side-by-side.
        solutions: قائمة من tuples (كائن الحل, اسم الخوارزمية)
        """
        n = len(solutions)
        cols = 2
        rows = (n + 1) // 2
        
        fig, axes = plt.subplots(rows, cols, figsize=(cols * 8, rows * 6))
        axes = axes.flatten() if n > 1 else [axes]
        
        for i, (sol, name) in enumerate(solutions):
            ax = axes[i]
            x_coords, y_coords = sol.get_route_coordinates()
            
            ax.plot(x_coords, y_coords, '-', linewidth=1.5, label=f'{name} Path')
            ax.scatter(x_coords[0], y_coords[0], c='red', s=80, zorder=5, edgecolors='black')
            ax.scatter(x_coords[1:-1], y_coords[1:-1], c='lightgray', s=40, zorder=3, edgecolors='gray')
            
            ax.set_title(f"{name}\nDist: {sol.total_distance:.2f}", fontsize=12, fontweight='bold')
            ax.grid(True, linestyle=':', alpha=0.5)
            ax.set_aspect('equal')
            ax.legend()
        
        # إخفاء المحاور الزائدة إذا كان عدد الحلول فردياً
        for j in range(i + 1, len(axes)):
            fig.delaxes(axes[j])
            
        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        if save_path:
            plt.savefig(save_path, dpi=300)
            print(f"✅ Comparison plot saved to {save_path}")
            
        return fig, axes