import sys
import time
import threading
from typing import Optional, List, Dict, Any

# PyQt6 imports
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QComboBox, 
                             QSpinBox, QTextEdit, QGroupBox, QFormLayout, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QFont

# pyqtgraph imports
import pyqtgraph as pg
import numpy as np

# Project imports
from utils.data_generator import DataGenerator
from utils.data_loader import load_data_auto
from core.city import City
from algorithms.aco_solver import ACOSolver
from algorithms.ga_solver import GASolver
from algorithms.pso_solver import PSOSolver

class WorkerSignals(QObject):
    """Signals for communication between worker thread and main GUI"""
    update_plot = pyqtSignal(list, list)
    update_convergence = pyqtSignal(float)
    finished = pyqtSignal(str)
    log_message = pyqtSignal(str)

class AlgorithmWorker(QThread):
    """Background thread to run algorithms without freezing GUI"""
    def __init__(self, algo_name: str, cities: List[City], config: dict):
        super().__init__()
        self.algo_name = algo_name
        self.cities = cities
        self.config = config
        self.signals = WorkerSignals()
        self._stop_flag = False

    def run(self):
        try:
            solver = None
            # 1. تهيئة الخوارزمية المختارة
            if self.algo_name == "ACO":
                solver = ACOSolver(self.cities, self.config)
            elif self.algo_name == "GA":
                solver = GASolver(self.cities, self.config)
            elif self.algo_name == "PSO":
                solver = PSOSolver(self.cities, self.config)
            else:
                raise ValueError(f"Unknown algorithm: {self.algo_name}")

            self.signals.log_message.emit(f"🚀 Starting {self.algo_name} optimization...")

            # 2. تشغيل الخوارزمية وحساب الوقت
            start_time = time.time()
            best_solution = solver.solve()
            end_time = time.time()
            
            elapsed_time = end_time - start_time

            # 3. إرسال إحداثيات المسار النهائي للرسم
            if best_solution and best_solution.path:
                x_coords, y_coords = best_solution.get_route_coordinates()
                self.signals.update_plot.emit(x_coords, y_coords)
                
                # 4. إرسال رسالة النجاح بالتفصيل (هنا تظهر المسافة والوقت)
                success_msg = (
                    f"✅ Finished!\n"
                    f"📏 Total Distance: {best_solution.total_distance:.2f}\n"
                    f"⏱️ Execution Time: {elapsed_time:.2f} seconds\n"
                    f"🔢 Cities Count: {len(self.cities)}"
                )
                self.signals.log_message.emit(success_msg)
            else:
                self.signals.log_message.emit("❌ Error: No valid solution found.")

            # 5. تحديث منحنى التقارب (اختياري - قد يسبب بطء إذا كان كبيراً جداً)
            # نقوم بإرسال التاريخ دفعة واحدة أو جزء منه لتجنب البطء
            history = solver.get_history()
            if history:
                # نرسل البيانات على دفعات صغيرة لمحاكاة الحركة دون تجميد الواجهة
                step = max(1, len(history) // 50) # تقليل عدد النقاط المرسلة للواجهة
                for i in range(0, len(history), step):
                    if self._stop_flag: break
                    self.signals.update_convergence.emit(history[i])
                    time.sleep(0.01) # تأخير بسيط جداً للرسم المتحرك

        except Exception as e:
            # 6. معالجة الأخطاء بشكل آمن جداً
            # نحول الخطأ لنص بغض النظر عن نوعه (سواء كان رقم، numpy type، أو نص)
            error_type = type(e).__name__
            error_msg_str = str(e)
            
            final_error_msg = f"❌ Error occurred in {self.algo_name}:\nType: {error_type}\nDetails: {error_msg_str}"
            
            self.signals.log_message.emit(final_error_msg)
            # نرسل إشارة فارغة لإنهاء الحالة
            self.signals.finished.emit(final_error_msg)
            return # خروج آمن

        # 7. إشارة الانتهاء الناجح
        self.signals.finished.emit("Optimization Completed Successfully")


    def stop(self):
        self._stop_flag = True

class TSPInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker: Optional[AlgorithmWorker] = None
        self.current_cities: List[City] = []
        
        # Initialize UI components first to avoid attribute errors
        self.btn_run = None
        self.btn_stop = None
        self.route_curve = None
        self.conv_curve = None
        
        self.init_ui()
        self.setWindowTitle("TSP Optimizer - AI Comparison Tool")
        self.setGeometry(100, 100, 1200, 800)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- Right Panel: Controls ---
        control_panel = QGroupBox("Control Panel")
        control_layout = QFormLayout()
        
        # City Settings
        self.n_cities_input = QSpinBox()
        self.n_cities_input.setRange(5, 200)
        self.n_cities_input.setValue(30)
        control_layout.addRow("Number of Cities:", self.n_cities_input)
        
        self.seed_input = QSpinBox()
        self.seed_input.setRange(0, 9999)
        self.seed_input.setValue(42)
        control_layout.addRow("Random Seed:", self.seed_input)
        
        btn_generate = QPushButton("Generate New Cities")
        btn_generate.clicked.connect(self.generate_cities)
        control_layout.addRow(btn_generate)
        
        # File Loading
        btn_load_file = QPushButton("Load .tsp or .csv File")
        btn_load_file.setStyleSheet("background-color: #3498db; color: white;")
        btn_load_file.clicked.connect(self.load_file_dialog)
        control_layout.addRow(btn_load_file)
        
        self.lbl_current_source = QLabel("Source: Random Generation")
        self.lbl_current_source.setStyleSheet("color: gray; font-style: italic;")
        control_layout.addRow(self.lbl_current_source)
        
        control_layout.addRow(QLabel("-" * 20))
        
        # Algorithm Settings
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["ACO", "GA", "PSO"])
        control_layout.addRow("Algorithm:", self.algo_combo)
        
        # Define buttons as self attributes BEFORE using them
        self.btn_run = QPushButton("Start Optimization")
        self.btn_run.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 5px;")
        self.btn_run.clicked.connect(self.start_optimization)
        
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet("background-color: #e74c3c; color: white;")
        self.btn_stop.clicked.connect(self.stop_optimization)
        
        control_layout.addRow(self.btn_run)
        control_layout.addRow(self.btn_stop)
        
        control_layout.addRow(QLabel("-" * 20))
        
        # Log Box
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setMaximumHeight(200)
        control_layout.addRow("Log:", self.log_box)
        
        control_panel.setLayout(control_layout)
        main_layout.addWidget(control_panel, 1)

        # --- Left Panel: Plots ---
        plots_panel = QWidget()
        plots_layout = QVBoxLayout(plots_panel)
        
        # Map Plot
        self.map_plot = pg.PlotWidget(title="TSP Route Map")
        self.map_plot.setAspectLocked(True)
        self.map_plot.setBackground('w')
        self.map_plot.showGrid(x=True, y=True, alpha=0.3)
        self.route_curve = self.map_plot.plot(pen='b', symbol='o', symbolBrush='r', symbolSize=5)
        
        # Convergence Plot
        self.conv_plot = pg.PlotWidget(title="Convergence Curve (Best Cost vs Iteration)")
        self.conv_plot.setBackground('w')
        self.conv_plot.showGrid(x=True, y=True, alpha=0.3)
        self.conv_plot.setLabel('left', 'Cost (Distance)')
        self.conv_plot.setLabel('bottom', 'Iteration')
        self.conv_curve = self.conv_plot.plot(pen='g', width=2)
        
        plots_layout.addWidget(self.map_plot, 2)
        plots_layout.addWidget(self.conv_plot, 1)
        
        main_layout.addWidget(plots_panel, 3)

    def generate_cities(self):
        n = self.n_cities_input.value()
        seed = self.seed_input.value()
        self.current_cities = DataGenerator.generate_random_cities(n, seed=seed)
        
        x = [c.x for c in self.current_cities]
        y = [c.y for c in self.current_cities]
        
        # تحديد حجم النقطة بناءً على عدد المدن (لتجنب التكتل)
        point_size = 6 if n < 100 else (2 if n < 1000 else 1)
        
        # رسم المدن
        self.route_curve.setData(x + [x[0]], y + [y[0]], 
                                 pen=None, 
                                 symbol='o', 
                                 symbolBrush='skyblue', 
                                 symbolSize=point_size)
        
        # ✅ الحل السحري: ضبط الكاميرا تلقائياً لتناسب البيانات فوراً
        self.map_plot.enableAutoRange() 
        
        self.conv_curve.clear()
        self.lbl_current_source.setText(f"Source: Random ({n} cities)")
        self.lbl_current_source.setStyleSheet("color: gray; font-style: italic;")
        self.log_message(f"Generated {n} cities with seed {seed}. View auto-adjusted.")

    def load_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Load TSP File", 
            "data/instances/", 
            "TSP Files (*.tsp *.csv);;All Files (*)"
        )
        
        if file_path:
            self.log_message(f"📂 Loading file: {file_path}...")
            cities = load_data_auto(file_path)
            
            if cities:
                self.current_cities = cities
                n = len(cities)
                
                x = [c.x for c in self.current_cities]
                y = [c.y for c in self.current_cities]
                
                # تحديد حجم النقطة بناءً على العدد
                point_size = 6 if n < 100 else (2 if n < 1000 else 1)
                
                # رسم المدن
                self.route_curve.setData(x + [x[0]], y + [y[0]], 
                                         pen=None, 
                                         symbol='o', 
                                         symbolBrush='skyblue', 
                                         symbolSize=point_size)
                
                # ✅ الحل السحري: ضبط الكاميرا تلقائياً لتناسب البيانات فوراً
                self.map_plot.enableAutoRange()
                
                self.conv_curve.clear()
                self.lbl_current_source.setText(f"Source: File ({n} cities)")
                self.lbl_current_source.setStyleSheet("color: green; font-weight: bold;")
                self.log_message(f"✅ Successfully loaded {n} cities. View auto-adjusted to fit data.")
            else:
                QMessageBox.critical(self, "Error", "Failed to load cities from file. Check console logs.")

    def start_optimization(self):
        if not self.current_cities:
            self.generate_cities()
        
        if not self.current_cities:
            QMessageBox.warning(self, "No Data", "Please generate or load cities first.")
            return

        algo_name = self.algo_combo.currentText()
        n = len(self.current_cities)
        
        config = {}
        if algo_name == "ACO":
            config = {'n_ants': n, 'n_iterations': 200, 'alpha': 1, 'beta': 2, 'rho': 0.5, 'q': 100}
        elif algo_name == "GA":
            config = {'pop_size': 100, 'n_generations': 200, 'pc': 0.8, 'pm': 0.02}
        elif algo_name == "PSO":
            config = {'swarm_size': 50, 'n_iterations': 200, 'w': 0.7, 'c1': 1.5, 'c2': 1.5}
            
        self.worker = AlgorithmWorker(algo_name, self.current_cities, config)
        self.worker.signals.update_plot.connect(self.update_route_plot)
        self.worker.signals.update_convergence.connect(self.update_convergence_plot)
        self.worker.signals.log_message.connect(self.log_message)

        self.worker.finished.connect(self.on_finished)
        
        # FIX: Ensure buttons exist before enabling/disabling
        if self.btn_run: self.btn_run.setEnabled(False)
        if self.btn_stop: self.btn_stop.setEnabled(True)
        
        self.conv_curve.clear()
        self.worker.start()

    def stop_optimization(self):
        if self.worker:
            self.worker.stop()
            self.log_message("⏹ Stopped by user.")
            self.on_finished("Stopped")

    def update_route_plot(self, x_coords, y_coords):
        self.route_curve.setData(x_coords, y_coords, pen=pg.mkPen('b', width=2), symbol='o', symbolBrush='r', symbolSize=5)

    def update_convergence_plot(self, cost):
        data = self.conv_curve.getData()
        if data[0] is None:
            x_data = [0]
            y_data = [cost]
        else:
            x_data = list(data[0])
            y_data = list(data[1])
            x_data.append(len(x_data))
            y_data.append(cost)
        self.conv_curve.setData(x_data, y_data)

    def log_message(self, msg):
        self.log_box.append(msg)
        self.log_box.verticalScrollBar().setValue(self.log_box.verticalScrollBar().maximum())

    def on_finished(self, msg=None):
        """تعامل مع انتهاء الخوارزمية"""
        if self.btn_run: 
            self.btn_run.setEnabled(True)
        if self.btn_stop: 
            self.btn_stop.setEnabled(False)
        
        if msg:
            self.log_message(msg)
            
        self.worker = None

def run_gui():
    app = QApplication(sys.argv)
    window = TSPInterface()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_gui()