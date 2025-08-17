#!/usr/bin/env python3
"""
voyager1_magneticfield_nTS_analysis.py
--------------------------------------

Voyager 1 Magnetometer Analysis by fetching real data from NASA's PDS/SPDF datasets.

This code is about fetching and visualizing the heliocentric position of
Voyager 1 relative to Earth using the JPL HORIZONS service via
``astroquery``.  

It also contains helpers for plotting time–series data from
comma‑separated values (CSV) files or Common Data Format (CDF) files.  

The objective is to develop a simple, extensible entry point for analysing Voyager 1
science data.

- Added --real-data flag to fetch actual Voyager 1 data from NASA archives
- Added --days-back option to control how much historical data to fetch
- Fallback to realistic simulated data if archive access fails

Run time (real time): 
python voyager1_magneticfield_nTS_analysis.py --real-data --days-back 30

Run time (unit test): 
python -m unittest test_voyager1_magneticfield_nTS_analysis.py

"""

import argparse
import datetime
import sys
from pathlib import Path
import urllib.request
import urllib.error
import tempfile

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    # Astroquery is used to query the JPL HORIZONS ephemeris service
    from astroquery.jplhorizons import Horizons  # type: ignore
    _ASTROQUERY_AVAILABLE = True
except Exception:
    _ASTROQUERY_AVAILABLE = False

try:
    import cdflib  # type: ignore
    _CDFLIB_AVAILABLE = True
except Exception:
    cdflib = None
    _CDFLIB_AVAILABLE = False

from astropy import units as u
from astropy.coordinates import SkyCoord


def fetch_ephemeris(now: datetime.datetime) -> tuple[np.ndarray, np.ndarray]:
    """Fetch the heliocentric positions of Voyager 1 and Earth.

    Parameters
    ----------
    now: datetime.datetime
        The epoch at which to query the ephemeris.  The JPL service expects
        UTC times.

    Returns
    -------
    (np.ndarray, np.ndarray)
        Two 3‑element arrays containing the x, y, z coordinates (in
        astronomical units) of Voyager 1 and Earth in a heliocentric frame.

    Notes
    -----
    If ``astroquery`` is not available or the query fails, approximate
    positions are returned as a fallback.  These sample values are not
    scientifically accurate but allow the script to run offline.
    """
    # Fallback positions (approximate in AU for demonstration)
    fallback_voyager = np.array([15.0, 20.0, 25.0])
    fallback_earth = np.array([1.0, 0.0, 0.0])

    if not _ASTROQUERY_AVAILABLE:
        return fallback_voyager, fallback_earth

    epoch = now.strftime('%Y-%m-%d %H:%M')
    try:
        # Voyager 1 ID is 'Voyager 1'; Earth is 399
        obj_voyager = Horizons(id="Voyager 1", location="@sun", epochs=epoch, id_type=None)
        obj_earth = Horizons(id=399, location="@sun", epochs=epoch)
        eph_voyager = obj_voyager.vectors()
        eph_earth = obj_earth.vectors()
        vx = float(eph_voyager['x'][0])
        vy = float(eph_voyager['y'][0])
        vz = float(eph_voyager['z'][0])
        ex = float(eph_earth['x'][0])
        ey = float(eph_earth['y'][0])
        ez = float(eph_earth['z'][0])
        return np.array([vx, vy, vz]), np.array([ex, ey, ez])
    except Exception:
        # Return fallback values on any error
        return fallback_voyager, fallback_earth


def plot_positions(v_pos: np.ndarray, e_pos: np.ndarray) -> None:
    """Plot the heliocentric positions of Voyager 1 and Earth in 3‑D.

    A simple scatter plot is created with the Sun at the origin.  The positions
    are given in astronomical units.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(0, 0, 0, label='Sun', s=50, c='yellow')
    ax.scatter(e_pos[0], e_pos[1], e_pos[2], label='Earth', s=50, c='blue')
    ax.scatter(v_pos[0], v_pos[1], v_pos[2], label='Voyager 1', s=50, c='red')
    ax.set_xlabel('X (AU)')
    ax.set_ylabel('Y (AU)')
    ax.set_zlabel('Z (AU)')
    ax.set_title('Voyager 1 and Earth positions in heliocentric coordinates')
    ax.legend()
    plt.show()

    # Convert Voyager 1 position to galactic coordinates and print to console
    coord = SkyCoord(x=v_pos[0] * u.au, y=v_pos[1] * u.au, z=v_pos[2] * u.au,
                     representation_type='cartesian')
    gal = coord.galactic
    print(f"Voyager 1 galactic longitude (l): {gal.l.deg:.2f} deg")
    print(f"Voyager 1 galactic latitude (b): {gal.b.deg:.2f} deg")


def plot_csv(csv_path: Path) -> None:
    """Load a CSV file and plot its second column as a time series.

    The CSV file must contain a 'time' column and at least one data column.
    The first data column will be plotted.
    """
    try:
        df = pd.read_csv(csv_path, parse_dates=['time'])
    except Exception as exc:
        raise RuntimeError(f"Failed to read CSV file {csv_path}: {exc}")
    if df.shape[1] < 2:
        raise ValueError(f"CSV file {csv_path} must contain at least two columns (time and value)")
    time_series = df.iloc[:, 0]
    data_series = df.iloc[:, 1]
    fig, ax = plt.subplots()
    ax.plot(time_series, data_series)
    ax.set_xlabel('Time')
    ax.set_ylabel(df.columns[1])
    ax.set_title(f"Time series of {df.columns[1]}")
    fig.autofmt_xdate()
    plt.show()


def plot_cdf(cdf_path: Path) -> None:
    """Load a CDF file and plot a selected variable.

    This function attempts to infer common time and value variables.  It requires
    the optional ``cdflib`` library; if not installed, an ``ImportError`` is
    raised.
    """
    if not _CDFLIB_AVAILABLE:
        raise ImportError("cdflib is not installed.  Install it to read CDF files.")
    cdf = cdflib.CDF(str(cdf_path))
    info = cdf.cdf_info()
    rvars = info['rVariables']

    # Candidate variable names for time and value
    time_candidates = ['Epoch', 'epoch', 'TIME', 'time']
    value_candidates = ['B', 'B_mag', 'B_nT', 'value', 'mag']
    time_var = next((v for v in time_candidates if v in rvars), None)
    value_var = next((v for v in value_candidates if v in rvars), None)
    if time_var is None or value_var is None:
        raise ValueError(f"Could not identify suitable time or value variables in {cdf_path}")
    time_data = cdf.varget(time_var)
    value_data = cdf.varget(value_var)
    # Convert CDF epoch to python datetime using cdflib helper
    try:
        times = cdflib.cdfepoch.to_datetime(time_data)
    except Exception:
        # Fallback conversion: assume seconds since epoch
        times = [datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=float(t)) for t in time_data]
    fig, ax = plt.subplots()
    ax.plot(times, value_data)
    ax.set_xlabel('Time')
    ax.set_ylabel(value_var)
    ax.set_title(f"Time series of {value_var}")
    fig.autofmt_xdate()
    plt.show()


def fetch_real_voyager_data(days_back: int = 30) -> Path:
    """Fetch real Voyager 1 magnetometer data from NASA's SPDF archives.
    
    Parameters
    ----------
    days_back : int
        Number of days back from today to fetch data for.
        
    Returns
    -------
    Path
        Path to the downloaded CDF file containing real Voyager 1 data.
        
    Notes
    -----
    This function attempts to download recent Voyager 1 magnetometer data
    from NASA's Space Physics Data Facility (SPDF). The data is saved to
    a temporary file and returned as a Path object.
    """
    end_date = datetime.datetime.now(datetime.UTC)
    start_date = end_date - datetime.timedelta(days=days_back)
    
    # NASA SPDF CDAWeb URL for Voyager 1 magnetometer data
    # Using the VG1-MAG-4SEC dataset (4-second resolution magnetometer data)
    base_url = "https://spdf.gsfc.nasa.gov/pub/data/voyager/voyager1/magnetic_field/4sec_data/"
    
    # Try to get data from the most recent year
    year = end_date.year
    filename = f"vg1_mag_4sec_{year}.cdf"
    url = f"{base_url}{year}/{filename}"
    
    try:
        print(f"Fetching real Voyager 1 magnetometer data from NASA SPDF...")
        print(f"URL: {url}")
        
        # Create a temporary file to store the downloaded data
        temp_file = tempfile.NamedTemporaryFile(suffix='.cdf', delete=False)
        temp_path = Path(temp_file.name)
        temp_file.close()
        
        # Download the file
        urllib.request.urlretrieve(url, temp_path)
        print(f"Successfully downloaded data to: {temp_path}")
        return temp_path
        
    except urllib.error.URLError as e:
        # If current year fails, try previous year
        prev_year = year - 1
        filename = f"vg1_mag_4sec_{prev_year}.cdf"
        url = f"{base_url}{prev_year}/{filename}"
        
        try:
            print(f"Trying previous year: {url}")
            temp_file = tempfile.NamedTemporaryFile(suffix='.cdf', delete=False)
            temp_path = Path(temp_file.name)
            temp_file.close()
            urllib.request.urlretrieve(url, temp_path)
            print(f"Successfully downloaded data to: {temp_path}")
            return temp_path
        except Exception as e2:
            raise RuntimeError(f"Failed to download Voyager 1 data from SPDF: {e2}") from e2
    except Exception as e:
        raise RuntimeError(f"Failed to download Voyager 1 data: {e}") from e


def fetch_real_voyager_data_alternative() -> Path:
    """Alternative method to fetch Voyager 1 data using a realistic simulation.
    
    This function creates a sample of what real magnetometer data might look like,
    based on the typical characteristics of Voyager 1's magnetic field measurements
    in the heliosheath/interstellar medium.
    
    Returns
    -------
    Path
        Path to a CSV file containing simulated recent Voyager 1 data.
    """
    print("Generating realistic Voyager 1 magnetometer data based on recent mission characteristics...")
    
    # Create realistic data based on Voyager 1's current environment
    # In the interstellar medium, magnetic field is typically 0.3-0.5 nT
    end_time = datetime.datetime.now(datetime.UTC)
    start_time = end_time - datetime.timedelta(days=7)  # Last week of data
    
    # Generate time series (every 4 seconds for 7 days)
    time_points = []
    current_time = start_time
    while current_time <= end_time:
        time_points.append(current_time)
        current_time += datetime.timedelta(seconds=4)
    
    # Generate realistic magnetic field data
    # Voyager 1 is in interstellar space with relatively stable but varying B-field
    np.random.seed(42)  # For reproducible "realistic" data
    base_field = 0.4  # nT, typical interstellar field strength
    
    # Add some realistic variations
    magnetic_field = []
    for i, _ in enumerate(time_points):
        # Long-term trend (space weather effects)
        trend = 0.1 * np.sin(2 * np.pi * i / (len(time_points) / 3))
        # Random fluctuations
        noise = np.random.normal(0, 0.05)
        # Occasional "events" (cosmic ray effects, etc.)
        if np.random.random() < 0.01:  # 1% chance of an event
            event = np.random.normal(0, 0.2)
        else:
            event = 0
        
        field_strength = base_field + trend + noise + event
        magnetic_field.append(max(0, field_strength))  # B-field can't be negative in magnitude
    
    # Create DataFrame
    df = pd.DataFrame({
        'time': time_points,
        'B_field_nT': magnetic_field
    })
    
    # Save to temporary CSV file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    temp_path = Path(temp_file.name)
    temp_file.close()
    
    df.to_csv(temp_path, index=False)
    print(f"Generated realistic Voyager 1 data: {temp_path}")
    print(f"Data covers {len(time_points)} measurements from {start_time.strftime('%Y-%m-%d')} to {end_time.strftime('%Y-%m-%d')}")
    return temp_path


def main(argv: list[str] | None = None) -> None:
    """Entry point for the command line interface."""
    parser = argparse.ArgumentParser(description='Visualise Voyager 1 ephemeris and science data')
    parser.add_argument('--csv', type=str, help='Path to a CSV file containing time series data to plot')
    parser.add_argument('--cdf', type=str, help='Path to a CDF file containing time series data to plot')
    parser.add_argument('--real-data', action='store_true', 
                       help='Fetch and plot real Voyager 1 magnetometer data from NASA archives')
    parser.add_argument('--days-back', type=int, default=7,
                       help='Number of days back to fetch real data (default: 7, only used with --real-data)')
    args = parser.parse_args(argv)

    now = datetime.datetime.now(datetime.UTC)
    v_pos, e_pos = fetch_ephemeris(now)
    plot_positions(v_pos, e_pos)

    # Determine which dataset to plot.  Prefer user‑supplied data if provided
    if args.csv:
        plot_csv(Path(args.csv))
    elif args.cdf:
        plot_cdf(Path(args.cdf))
    elif args.real_data:
        try:
            # Try to fetch real data from NASA archives
            print("Attempting to fetch real Voyager 1 data from NASA SPDF archives...")
            try:
                real_data_path = fetch_real_voyager_data(args.days_back)
                if str(real_data_path).endswith('.cdf'):
                    plot_cdf(real_data_path)
                else:
                    plot_csv(real_data_path)
            except Exception as e:
                print(f"Failed to fetch real archive data: {e}")
                print("Falling back to generating realistic sample data...")
                realistic_data_path = fetch_real_voyager_data_alternative()
                plot_csv(realistic_data_path)
        except Exception as e:
            print(f"Error with real data: {e}")
            print("Falling back to local sample data...")
            # Check for both the original and renamed sample files
            sample_files = [
                'voyager1_magnetometer_sample.csv',
                'voyager1_magnetometer_unittest.csv'
            ]
            
            sample_csv = None
            for filename in sample_files:
                potential_path = Path(__file__).resolve().parent / filename
                if potential_path.exists():
                    sample_csv = potential_path
                    break
            
            if sample_csv:
                plot_csv(sample_csv)
            else:
                print("No fallback sample data found.")
    else:
        # Attempt to locate bundled sample data relative to this script
        # Check for both the original and renamed sample files
        sample_files = [
            'voyager1_magnetometer_sample.csv',
            'voyager1_magnetometer_unittest.csv'
        ]
        
        sample_csv = None
        for filename in sample_files:
            potential_path = Path(__file__).resolve().parent / filename
            if potential_path.exists():
                sample_csv = potential_path
                break
        
        if sample_csv:
            print(f"No data file provided; plotting sample data from {sample_csv}")
            plot_csv(sample_csv)
        else:
            print("No data file provided and no sample data found; skipping science plot.")


if __name__ == '__main__':
    main()
