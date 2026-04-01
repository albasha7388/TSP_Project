# TSP Optimizer - AI Algorithms Comparison Suite

A comprehensive Python project designed to solve the **Traveling Salesperson Problem (TSP)** using three state-of-the-art Meta-Heuristic algorithms: **Ant Colony Optimization (ACO)**, **Genetic Algorithm (GA)**, and **Particle Swarm Optimization (PSO)**.

This project provides a complete ecosystem including:
*   🔬 **Algorithmic Core**: Highly optimized implementations of ACO, GA, and PSO.
*   📊 **Benchmarking Engine**: Automated statistical comparison with multiple runs.
*   🎨 **Interactive GUI**: Real-time visualization of routes and convergence.
*   📈 **Reporting**: Automatic generation of CSV reports and high-quality plots.
*   🌍 **Data Flexibility**: Supports random generation and standard `.tsp` / `.csv` files (TSPLIB compatible).

---

## 📋 Features

*   **Three Advanced Algorithms**:
    *   **ACO**: Uses pheromone trails and 2-Opt local search for high precision.
    *   **GA**: Uses Order Crossover (OX1) and Swap Mutation.
    *   **PSO**: Uses Random Keys encoding for discrete optimization.
*   **Smart Data Loading**: Automatically detects and loads `.csv` or `.tsp` files. Handles coordinate scaling and ID re-indexing automatically.
*   **Statistical Rigor**: Runs experiments multiple times to calculate Mean, Standard Deviation, Min, Max, and Execution Time.
*   **Visualization**:
    *   Live route plotting in the GUI.
    *   Convergence curves (Cost vs. Iterations).
    *   Boxplots for distribution analysis.
*   **Modular Architecture**: Clean code structure separating Core logic, Algorithms, Visualization, and Experiments.

---

## 🛠️ Installation

### Prerequisites
*   Python 3.8 or higher.
*   pip (Python Package Installer).

### Steps
1.  **Clone or Download the Project**:
    ```bash
    cd TSP_Project
    ```

2.  **Create a Virtual Environment** (Recommended):
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If you are on Linux and get a Tkinter error, run `sudo apt-get install python3-tk`)*.

---

## ⚙️ How to Run

The project is launched via the main entry point `main.py`. It offers an interactive menu to choose between different modes.

### 1. Launch the Main Menu
Run the following command in your terminal:
```bash
python main.py
```

```
============================================================
       TSP OPTIMIZER - AI ALGORITHMS SUITE
       Genetic | Ant Colony | Particle Swarm
============================================================

Main Menu:
1. Run Single Algorithm (Console Mode)
2. Launch Interactive GUI
3. Run Full Benchmark & Report
4. Exit

Enter your choice (1-4):
```

### Operating Modes & Options

**Option 1: Console Mode (Single Run)**
Best for: Quick testing of a specific file or algorithm.

Select `1` in the menu.

Choose data source:
*   **Random**: Enter number of cities and seed.
*   **File**: Enter the path to your `.tsp` or `.csv` file (e.g., `data/instances/yemen.csv`).

Select the algorithm (ACO, GA, or PSO).

The system will run the optimization and print:
*   Total Distance.
*   Execution Time.
*   First 10 cities in the path.
*   Convergence summary.

**Option 2: Interactive GUI**
Best for: Visualizing the solution, watching the algorithm work, and educational demos.

Select `2` in the menu.

A window will open with two panels:
*   **Left Panel**: Controls to generate cities, load files, select algorithms, and start/stop execution.
*   **Right Panel**:
    *   **Top Graph**: The map showing cities and the evolving route.
    *   **Bottom Graph**: Real-time convergence curve (Best Cost vs. Iteration).

Features:
*   Click "Load .tsp or .csv File" to import your custom data. The view auto-zooms to fit the data.
*   Click "Start Optimization" to watch the algorithm find the path live.
*   Logs appear in the text box at the bottom.

**Option 3: Full Benchmark Suite**
Best for: Scientific comparison, research, and generating final reports.

Select `3` in the menu.

The system reads the configuration from `experiments/run_benchmark.py`.

It automatically:
*   Loads all defined scenarios (Random sets + Custom Files like `yemen.csv`).
*   Runs all three algorithms on each scenario for N runs (default is 5 or 10).
*   Calculates statistics (Mean, Std, Min, Max, Time).
*   Outputs generated in `data/results/session_YYYY-MM-DD_HH-MM-SS/`:
    *   `detailed_results.csv`: Raw data for every single run.
    *   `summary_report.csv`: Statistical aggregation with "Winner" flags.
    *   `summary_report.txt`: Human-readable text report.
    *   `comparison_boxplot.png`: Visual comparison of cost distribution.
    *   `execution_time_bar.png`: Visual comparison of speed.

### Project Structure
```
TSP_Project/
│
├── data/
│   ├── instances/          # Place your .tsp and .csv files here
│   └── results/            # Generated reports and charts go here
│
├── algorithms/             # Core AI Logic
│   ├── base_solver.py      # Abstract Base Class
│   ├── aco_solver.py       # Ant Colony Optimization
│   ├── ga_solver.py        # Genetic Algorithm
│   └── pso_solver.py       # Particle Swarm Optimization
│
├── core/                   # Problem Definition
│   ├── city.py             # City Object
│   ├── distance_matrix.py  # Optimized Distance Calculation (NumPy)
│   └── solution.py         # Solution Object (Path + Cost)
│
├── utils/                  # Helpers
│   ├── data_loader.py      # Smart Loader (.tsp & .csv)
│   ├── data_generator.py   # Random Data Generator
│   ├── metrics.py          # Statistical Metrics
│   └── logger.py           # Logging Utility
│
├── visualization/          # Graphics
│   ├── route_drawer.py     # Static Route Plotting
│   ├── convergence_analyzer.py # Convergence Charts
│   └── gui_interface.py    # PyQt6 Interactive Interface
│
├── experiments/            # Benchmarking
│   └── run_benchmark.py    # Automated Experiment Runner
│
├── main.py                 # Entry Point (Menu System)
├── requirements.txt        # Dependencies
└── README.md               # This file
```

### Adding Custom Data
To test with your own maps:

1.  Prepare a `.csv` file with columns:
    ```
    id,x,y
    0,10.5,20.3
    1,15.2,25.6
    ...
    ```
    Or use standard TSPLIB `.tsp` format.

2.  Place the file in `data/instances/`.

3.  For Console/GUI: Simply select "Load File" and type the filename.

4.  For Benchmark: Edit `experiments/run_benchmark.py` and add your file to the `scenarios` list:
    ```python
    'scenarios': [
        {'type': 'file', 'path': 'data/instances/my_custom_map.csv'},
        # ... other scenarios
    ],
    ```

## 🏆 Expected Results
Based on typical TSP characteristics:
*   **Accuracy**: ACO usually provides the shortest paths due to the positive feedback loop of pheromones and integrated 2-Opt local search.
*   **Speed**: PSO and GA are often faster per iteration but may require more iterations to converge to a high-quality solution compared to ACO.
*   **Stability**: ACO typically shows lower standard deviation across multiple runs, indicating higher reliability.

## 🤝 Contributing
Feel free to fork this repository, add new algorithms (e.g., Simulated Annealing, Tabu Search), or improve the visualization. Please ensure your code follows the existing modular structure.

## 📄 License
This project is open-source and available for educational and research purposes.

## 💡 Quick Tips
*   **Large Datasets**: If running files with >1000 cities (like `ym7663.tsp`), reduce the `n_iterations` in the config to save time during testing.
*   **GUI Freezing**: If the GUI seems unresponsive during heavy calculation, wait a moment; the calculation runs in a background thread, and the plot updates after completion or in batches.
*   **Errors**: If you see `ModuleNotFoundError`, ensure you activated the virtual environment (`venv`) before running `pip install`.

---

## 🧑‍💻 Author and Project Information

*   **Author**: ENG/Sameh Alsalahy
*   **Project Repository**: [TSP Optimizer - AI Algorithms Comparison Suite](https://github.com/albasha7388/TSP_Project.git)
*   **Author's GitHub Profile**: [albasha7388](https://github.com/albasha7388)
*   **Contact**: almandopeng1230@gmail.com

---