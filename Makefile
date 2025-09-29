.PHONY: help venv install run headless video plot clean

# Default target
help:
	@echo "PyBullet Path Follower - Available targets:"
	@echo "  venv      - Create virtual environment"
	@echo "  install   - Install dependencies"
	@echo "  run       - Run simulation with GUI"
	@echo "  headless  - Run simulation without GUI"
	@echo "  video     - Record simulation video"
	@echo "  plot      - Plot trajectory from CSV"
	@echo "  clean     - Clean generated files"

# Create virtual environment
venv:
	@echo "Creating virtual environment..."
	python -m venv .venv
	@echo ""
	@echo "Virtual environment created!"
	@echo "To activate on Windows: .venv\\Scripts\\activate"
	@echo "To activate on macOS/Linux: source .venv/bin/activate"
	@echo ""
	@echo "After activation, run: make install"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "Dependencies installed!"

# Run simulation with GUI
run:
	@echo "Running simulation with GUI..."
	python main.py --gui

# Run simulation headless
headless:
	@echo "Running simulation in headless mode..."
	python main.py --headless

# Record simulation video
video:
	@echo "Recording simulation video..."
	@mkdir -p assets
	python main.py --record --video assets/demo.mp4
	@echo "Video saved to assets/demo.mp4"

# Plot trajectory
plot:
	@echo "Plotting trajectory..."
	python traj_plot.py

# Plot with velocity profile
plot-velocity:
	@echo "Plotting trajectory with velocity profile..."
	python traj_plot.py --velocity

# Save plots
plot-save:
	@echo "Plotting and saving trajectory..."
	python traj_plot.py --save

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	@if exist trajectory.csv del trajectory.csv
	@if exist assets rmdir /s /q assets
	@if exist __pycache__ rmdir /s /q __pycache__
	@if exist *.png del *.png
	@echo "Clean complete!"

# Run tests (placeholder for future tests)
test:
	@echo "No tests defined yet"

# Development setup (create venv and install)
setup: venv
	@echo "Please activate the virtual environment and then run 'make install'"
