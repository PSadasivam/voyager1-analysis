# Getting Started

This guide walks you through setting up and running the Voyager 1 Deep Space Analysis Suite on your local machine.

## Prerequisites

- **Python 3.8+** (tested with 3.13)
- **Git** for cloning the repository
- **VS Code** (recommended) — a workspace file is included

## 1. Clone the Repository

```bash
git clone https://github.com/PSadasivam/voyager1-analysis.git
cd voyager1_project
```

## 2. Create and Activate a Virtual Environment

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python -m venv .venv
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs the following packages:

| Package      | Purpose                                  |
|--------------|------------------------------------------|
| astropy      | Astronomical calculations and coordinates |
| astroquery   | NASA JPL HORIZONS ephemeris queries       |
| pandas       | Data manipulation and analysis            |
| numpy        | Numerical computing                       |
| matplotlib   | Plotting and visualization                |
| cdflib       | NASA CDF file format support              |
| scipy        | Scientific computing and signal processing|

## 4. Open the Workspace in VS Code

Open the included workspace file for a preconfigured experience:

```
File → Open Workspace from File → voyager1_project.code-workspace
```

## 5. Run the Analysis Scripts

### Trajectory Visualization

Plot Voyager 1's complete outbound heliocentric trajectory (1977–present):

```bash
python voyager1_outbound_trajectory.py
```

Use `--fallback` for offline synthetic data, or `--show-earth` to include Earth's position:

```bash
python voyager1_outbound_trajectory.py --fallback --step-days 60
python voyager1_outbound_trajectory.py --show-earth
```

### Plasma Wave Analysis

Generate spectrograms of plasma wave intensity:

```bash
python voyager1_plasma_wave_analysis.py --synthetic --spectrogram
```

Analyze a specific frequency range or view a time series:

```bash
python voyager1_plasma_wave_analysis.py --synthetic --frequency-range 100 2000 --time-series
```

### Electron Density Extraction

Extract electron density with NASA-style plots:

```bash
python voyager1_density_extraction.py --synthetic --nasa-style
```

Export results to CSV:

```bash
python voyager1_density_extraction.py --synthetic --export-csv density_results.csv
```

### Magnetic Field Analysis

Run the magnetometer analysis with the included sample data:

```bash
python voyager1_magneticfield_nTS_analysis.py
python voyager1_magneticfield_nTS_analysis.py --csv voyager1_magnetometer_unittest.csv
```

### Web Application

Launch the Flask-based web dashboard to explore Voyager 1 data in your browser:

```bash
pip install flask
python voyager1_web_app.py
```

Then open **http://localhost:5000** in your browser.

## 6. Verify Your Setup

Confirm position calculations are working correctly:

```bash
python verify_voyager_position.py
```

## 7. Run Unit Tests

```bash
python -m unittest test_voyager1_magneticfield_nTS_analysis.py
```

## Troubleshooting

- **`ModuleNotFoundError`** — Make sure the virtual environment is activated and dependencies are installed.
- **Network errors when fetching data** — Several scripts support a `--synthetic` or `--fallback` flag to use locally generated data instead of downloading from NASA servers.
- **`ExecutionPolicy` errors on Windows** — Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` before activating the virtual environment.
