# Voyager 1 Data Visualization & Analysis

This repository contains a small Python project for visualising the heliocentric position of **Voyager 1** and plotting science data recorded by the spacecraft.  The goal is to provide an extensible framework that can be expanded with additional instruments and analysis in the future.

## Project overview

The project bundles a standalone script, some sample data, and supporting documentation.  When run, the script uses [Astroquery](https://astroquery.readthedocs.io/) to request the current position of Voyager 1 and Earth from NASA’s JPL HORIZONS service.  It then produces a simple 3‑D plot showing both bodies in heliocentric coordinates and prints the galactic coordinates of Voyager 1 for reference.

In addition to ephemeris data, the script can load a comma‑separated values (CSV) file or a Common Data Format (CDF) file containing instrument measurements such as magnetometer field strength.  When a dataset is provided, the script will plot the time series on a separate figure.  A small sample CSV file (`voyager1_magnetometer_sample.csv`) is included for demonstration.

Real Data: https://spdf.gsfc.nasa.gov/pub/data/voyager/voyager1/
Yearly Data from Voyager 1: https://spdf.gsfc.nasa.gov/pub/data/voyager/voyager1/coho1hr_magplasma/


## Getting started

1. **Clone the repository** and navigate into it:

   ```sh
   git clone <repository‑url>
   cd voyager1_project
   ```

2. **Create a virtual environment**.  Using a virtual environment helps keep the dependencies isolated: 

   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**.  All required third‑party libraries are listed in `requirements.txt`.  Install them with pip:

   ```sh
   pip install -r requirements.txt
   ```

4. **Run the script**.  To visualise the current Voyager 1 position and plot the sample data, run:

   ```sh
   python voyager1_astropy_science.py
   ```

   To plot your own CSV or CDF data, supply the `--csv` or `--cdf` arguments:

   ```sh
   python voyager1_astropy_science.py --csv path/to/your_data.csv
   python voyager1_astropy_science.py --cdf path/to/your_data.cdf
   ```

## Repository structure

The layout of this repository follows several commonly recommended conventions for Python projects.  At the top level you will find a `README.md` (this file), a `LICENSE`, and a `requirements.txt` file for managing dependencies.  The source code and sample data live in the root folder of the project.  See the articles in the Python Guide for more details on why projects often include a README, requirements file and license【458911791183543†L53-L116】【749836306123978†L419-L456】.  Additional features or packages can be added later by creating subpackages or a `src/` directory as your needs grow.

## License

This project is licensed under the MIT License.  See the `LICENSE` file for details.

Developer/Contributor: Prabhu Sadasivam, https://www.linkedin.com/in/prabhusadasivam/
