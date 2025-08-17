# Voyager 1 Deep Space Analysis Suite

This repository contains a comprehensive Python toolkit for analyzing **Voyager 1** spacecraft data, tracking its historic journey from Earth to interstellar space. The project provides advanced visualization, trajectory analysis, and scientific data processing capabilities for studying humanity's most distant active spacecraft.

## Project Overview

Voyager 1, launched in 1977, has traveled over 160 AU from the Sun and is now exploring the interstellar medium beyond our solar system's influence. This analysis suite combines real NASA data with sophisticated visualization tools to study:

- **Heliocentric trajectory** from launch through planetary flybys to current position
- **Plasma wave measurements** from the Plasma Wave Subsystem (PWS) instrument  
- **Magnetic field data** from the magnetometer instrument
- **Electron density** extraction from plasma frequency analysis
- **Interstellar medium** characterization and space weather studies

The toolkit integrates data from NASA's JPL HORIZONS ephemeris service, Space Physics Data Facility (SPDF), and Planetary Data System (PDS) archives.

## Key Features

### **Trajectory Visualization**
- **3D heliocentric plots** showing complete outbound path (1977-present)
- **Mission milestone markers** for Jupiter flyby, Saturn flyby, heliopause crossing
- **Real vs synthetic trajectory** options with JPL HORIZONS integration
- **Enhanced annotations** with arrows, text boxes, and reference lines

### **Plasma Wave Analysis** 
- **Dynamic spectrograms** of plasma wave intensity vs frequency and time
- **Wave classification** for Langmuir waves, Alfvén waves, and turbulence
- **Real-time data fetching** from NASA SPDF archives
- **Synthetic data generation** for offline analysis and education

### **Magnetic Field Processing**
- **Time series analysis** of magnetic field strength measurements
- **CDF and CSV data support** for various NASA data formats
- **Sample datasets** included for immediate testing

### **Electron Density Extraction**
- **Plasma frequency ridge detection** using advanced signal processing
- **NASA-style density plots** matching published scientific literature
- **Automated peak tracking** with confidence scoring and outlier removal
- **CSV export capabilities** for further analysis

## Repository Structure

```
voyager1_project/
├── README.md                              # This documentation
├── LICENSE                                # MIT license
├── requirements.txt                       # Python dependencies
├── voyager1_project.code-workspace       # VS Code workspace configuration
│
├── Core Analysis Scripts:
├── voyager1_magneticfield_nTS_analysis.py # Original magnetometer analysis
├── voyager1_outbound_trajectory.py        # 3D trajectory visualization  
├── voyager1_plasma_wave_analysis.py       # PWS spectrogram analysis
├── voyager1_density_extraction.py         # Electron density from plasma waves
│
├── Utilities & Testing:
├── verify_voyager_position.py             # Position accuracy verification
├── test_voyager1_magneticfield_nTS_analysis.py # Unit tests
│
├── Sample Data:
├── voyager1_magnetometer_unittest.csv     # Sample magnetometer data
│
└── Environment:
    ├── .venv/                             # Python virtual environment
    ├── .git/                              # Git version control
    ├── .gitignore                         # Git ignore rules
    └── __pycache__/                       # Python bytecode cache
```

## Scientific Applications

### **Research Areas Supported**
- **Heliospheric Physics**: Boundary interactions, solar wind termination
- **Interstellar Medium Studies**: Density, magnetic field, wave propagation  
- **Space Weather**: Plasma conditions affecting spacecraft operations
- **Astrobiological Context**: Radiation environment for potential life detection
- **Mission Planning**: Reference data for future interstellar missions

### **Data Analysis Capabilities**
- **Multi-instrument integration**: Combines trajectory, plasma, and magnetic field data
- **Time series analysis**: Statistical trends, periodicities, event detection
- **Spectral analysis**: Frequency domain processing for wave identification
- **Comparative studies**: Heliosheath vs interstellar medium conditions

## Quick Start Guide

### 1. **Environment Setup**

```bash
# Clone the repository
git clone https://github.com/PrabhuSadasivam/voyager1-analysis.git
cd voyager1_project

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Basic Usage Examples**

#### **Trajectory Visualization**
```bash
# Show complete outbound trajectory with mission events
python voyager1_outbound_trajectory.py

# Use synthetic data (offline mode)
python voyager1_outbound_trajectory.py --fallback --step-days 60

# Include Earth position reference
python voyager1_outbound_trajectory.py --show-earth
```

#### **Plasma Wave Analysis**
```bash
# Generate spectrogram from synthetic data
python voyager1_plasma_wave_analysis.py --synthetic --spectrogram

# Analyze specific frequency range
python voyager1_plasma_wave_analysis.py --synthetic --frequency-range 100 2000 --time-series

# Attempt real data download
python voyager1_plasma_wave_analysis.py --real-data --days-back 30
```

#### **Electron Density Extraction**
```bash
# Extract density with NASA-style plotting
python voyager1_density_extraction.py --synthetic --nasa-style

# Export results to CSV
python voyager1_density_extraction.py --synthetic --export-csv density_results.csv

# Focus on plasma frequency range
python voyager1_density_extraction.py --synthetic --freq-range 1000 5000
```

#### **Magnetic Field Analysis**
```bash
# Basic magnetometer analysis
python voyager1_magneticfield_nTS_analysis.py

# Use real data if available
python voyager1_magneticfield_nTS_analysis.py --real-data --days-back 14

# Plot sample data
python voyager1_magneticfield_nTS_analysis.py --csv voyager1_magnetometer_unittest.csv
```

## Technical Requirements

### **Dependencies**
- **Python 3.8+** (tested with 3.13)
- **astropy** - Astronomical calculations and coordinates
- **astroquery** - NASA JPL HORIZONS ephemeris queries  
- **matplotlib** - Plotting and visualization
- **numpy** - Numerical computing
- **pandas** - Data manipulation and analysis
- **scipy** - Scientific computing and signal processing
- **cdflib** - NASA CDF file format support

### **Optional Enhancements**
- **VS Code** - Recommended IDE with workspace configuration included
- **Jupyter** - For interactive analysis (not required)
- **Git LFS** - For large data files (if adding real datasets)

## Data Sources & References

### **NASA Data Archives**
- **JPL HORIZONS**: https://ssd.jpl.nasa.gov/horizons/ (Ephemeris data)
- **NASA SPDF**: https://spdf.gsfc.nasa.gov/pub/data/voyager/voyager1/ (Science data)
- **NASA PDS**: https://pds-ppi.igpp.ucla.edu/search/?sc=Voyager+1 (Archived datasets)
- **Real Data**: https://spdf.gsfc.nasa.gov/pub/data/voyager/voyager1/
- **Yearly Data from Voyager 1**: https://spdf.gsfc.nasa.gov/pub/data/voyager/voyager1/coho1hr_magplasma/

### **Scientific Background**
- **Voyager Mission**: https://voyager.jpl.nasa.gov/
- **Plasma Wave Instrument**: Detailed specifications and methodology
- **Interstellar Medium**: Current understanding and Voyager discoveries
- **Heliospheric Physics**: Solar wind termination and boundary processes

## Development & Contribution

### **Code Organization**
- **Modular design** with separate scripts for each analysis type
- **Consistent APIs** across all analysis modules
- **Error handling** with graceful fallbacks to synthetic data
- **Documentation** following NumPy/SciPy standards

### **Testing**
```bash
# Run unit tests
python -m unittest test_voyager1_magneticfield_nTS_analysis.py

# Verify position calculations
python verify_voyager_position.py
```

### **Contributing**
1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-analysis`)
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

## License & Attribution

**License**: MIT License - see `LICENSE` file for details

**Developer**: Prabhu Sadasivam  
**Contact**: https://www.linkedin.com/in/prabhusadasivam/

**Citation**: If using this toolkit for research, please cite:
```
Sadasivam, P. (2025). Voyager 1 Deep Space Analysis Suite. 
GitHub Repository: https://github.com/PrabhuSadasivam/voyager1-analysis
```

## Acknowledgments

- **NASA JPL Voyager Team** - For decades of brilliant engineering and science
- **NASA SPDF & PDS** - For maintaining accessible data archives  
- **Python Scientific Community** - For the excellent scientific computing ecosystem
- **Astroquery/Astropy Teams** - For seamless astronomical data integration

---

*This toolkit represents 48+ years of Voyager 1's journey from Earth to interstellar space, continuing humanity's greatest voyage of discovery.*

