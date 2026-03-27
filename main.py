import sys
import os
import time
from typing import List

# Import project components
from utils.data_generator import DataGenerator
from utils.data_loader import load_data_auto
from core.distance_matrix import DistanceMatrix
from algorithms.aco_solver import ACOSolver
from algorithms.ga_solver import GASolver
from algorithms.pso_solver import PSOSolver

def print_header():
    print("=" * 60)
    print("       TSP OPTIMIZER - AI ALGORITHMS SUITE")
    print("       Genetic | Ant Colony | Particle Swarm")
    print("=" * 60)

def get_cities_source():
    """Helper function to choose data source (File or Random)"""
    print("\n--- Data Source ---")
    print("1. Generate Random Cities")
    print("2. Load File (.tsp or .csv)")
    choice = input("Choose (1 or 2): ").strip()
    
    cities = []
    if choice == '1':
        try:
            n = int(input("Enter number of cities: "))
            seed_input = input("Enter random seed (e.g., 42) [default: 42]: ")
            seed = int(seed_input) if seed_input else 42
            
            cities = DataGenerator.generate_random_cities(n, seed=seed)
            print(f"✅ Successfully generated {n} cities.")
        except ValueError:
            print("❌ Error: Please enter valid integers.")
            return []
    elif choice == '2':
        path = input("Enter file path (e.g., berlin52.tsp): ").strip()
        
        # Check direct path first, then check inside data/instances/
        if not os.path.exists(path):
            default_path = os.path.join("data", "instances", path)
            if os.path.exists(default_path):
                path = default_path
            else:
                print(f"❌ File not found: {path}")
                return []
        
        cities = load_data_auto(path)
        if not cities:
            return []
    else:
        print("❌ Invalid option.")
        return []
    
    return cities

def run_console_single():
    """Run a single algorithm and display text results in console"""
    print("\n--- Run Single Algorithm ---")
    
    cities = get_cities_source()
    if not cities:
        return

    print("\n--- Select Algorithm ---")
    print("1. Ant Colony Optimization (ACO)")
    print("2. Genetic Algorithm (GA)")
    print("3. Particle Swarm Optimization (PSO)")
    algo_choice = input("Choose (1-3): ").strip()
    
    config = {}
    solver_class = None
    algo_name = ""
    
    n = len(cities)
    
    if algo_choice == '1':
        algo_name = "ACO"
        solver_class = ACOSolver
        config = {'n_ants': n, 'n_iterations': 150, 'alpha': 1.0, 'beta': 2.0, 'rho': 0.5, 'q': 100}
    elif algo_choice == '2':
        algo_name = "GA"
        solver_class = GASolver
        config = {'pop_size': 100, 'n_generations': 200, 'pc': 0.8, 'pm': 0.02}
    elif algo_choice == '3':
        algo_name = "PSO"
        solver_class = PSOSolver
        config = {'swarm_size': 50, 'n_iterations': 200, 'w': 0.7, 'c1': 1.5, 'c2': 1.5}
    else:
        print("❌ Invalid option.")
        return

    print(f"\n🚀 Running {algo_name} on {n} cities...")
    print("Please wait...\n")
    
    start_time = time.perf_counter()
    solver = solver_class(cities, config)
    best_solution = solver.solve()
    end_time = time.perf_counter()
    
    print("\n" + "=" * 40)
    print(f"✅ Execution Complete: {algo_name}")
    print("=" * 40)
    print(f"📏 Total Distance: {best_solution.total_distance:.4f}")
    print(f"⏱️ Execution Time: {end_time - start_time:.4f} seconds")
    print(f"🛣️ Path (first 10 cities): {best_solution.path[:10]}...")
    
    # Display convergence summary
    history = solver.get_history()
    if len(history) > 0:
        print(f"📉 Convergence: From {history[0]:.2f} to {history[-1]:.2f}")
    
    input("\nPress Enter to return to the main menu...")

def run_gui_mode():
    """Launch the Graphical User Interface"""
    print("\n🎨 Launching Graphical User Interface (GUI)...")
    try:
        from gui.interface import run_gui
        run_gui()
    except ImportError as e:
        print(f"❌ Error: GUI libraries not found. Ensure PyQt6 and pyqtgraph are installed.\nDetails: {e}")
        input("Press Enter to continue...")
    except Exception as e:
        print(f"❌ An error occurred while launching the GUI: {e}")
        input("Press Enter to continue...")

def run_benchmark_mode():
    """Run the full benchmark suite"""
    print("\n📊 Launching Comprehensive Benchmark Suite...")
    print("This will run all three algorithms on scenarios defined in the config file.")
    confirm = input("Are you sure? (y/n): ").strip().lower()
    if confirm == 'y':
        import subprocess
        # Run the benchmark script as a separate process
        subprocess.run([sys.executable, "experiments/run_benchmark.py"])
        print("\n✅ Benchmark suite finished.")
        input("Press Enter to return...")
    else:
        print("Cancelled.")

def main():
    while True:
        # Clear screen based on OS
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print_header()
        print("\nMain Menu:")
        print("1. Run Single Algorithm (Console Mode)")
        print("2. Launch Interactive GUI")
        print("3. Run Full Benchmark & Report")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            run_console_single()
        elif choice == '2':
            run_gui_mode()
            # Code resumes here after GUI is closed
        elif choice == '3':
            run_benchmark_mode()
        elif choice == '4':
            print("👋 Thank you for using TSP Optimizer. Goodbye!")
            break
        else:
            print("❌ Invalid option, please try again.")
            time.sleep(1)

if __name__ == "__main__":
    main()