#!/usr/bin/env python3
"""
voyager1_plasma_wave_analysis.py
---------------------------------

Parse and analyze Voyager 1 Plasma Wave Subsystem (PWS) data to study plasma waves 
in the heliosheath and interstellar medium.

The PWS instrument measures:
- Electric field fluctuations (plasma waves)
- Wave frequency spectra (10 Hz to 56 kHz)
- Wave intensity and polarization
- Electron density estimates

Key science objectives:
- Monitor transition from heliosheath to interstellar medium
- Detect shock waves and turbulence
- Study electron plasma oscillations
- Analyze wave-particle interactions

Usage:
    python voyager1_plasma_wave_analysis.py --real-data --days-back 30
    python voyager1_plasma_wave_analysis.py --synthetic --frequency-range 100 1000
    python voyager1_plasma_wave_analysis.py --spectrogram --time-window 24

    
X-axis (Time, UTC): Covers ~one Earth day (Aug 16–17, 2025). Each vertical slice is a spectrum at that time.
Y-axis (Frequency, Hz): Log scale from ~10 Hz to 10,000 Hz. This is the range of plasma wave oscillations detected.
Color (Wave Intensity, V²/m²/Hz): Bright colors = stronger signals, darker colors = weaker background. The scale bar at right shows intensity on a logarithmic scale.

# Basic density extraction with process visualization
C:/Deep-Space-Research/voyager1_project/.venv/Scripts/python.exe voyager1_density_extraction.py --synthetic --duration-hours 24

# NASA-style publication plot
C:/Deep-Space-Research/voyager1_project/.venv/Scripts/python.exe voyager1_density_extraction.py --synthetic --nasa-style --duration-hours 48

# Export results to CSV
C:/Deep-Space-Research/voyager1_project/.venv/Scripts/python.exe voyager1_density_extraction.py --synthetic --export-csv density_results.csv

# Focus on specific frequency range
C:/Deep-Space-Research/voyager1_project/.venv/Scripts/python.exe voyager1_density_extraction.py --synthetic --freq-range 1000 5000 --smooth-window 7

# Attempt real data analysis
C:/Deep-Space-Research/voyager1_project/.venv/Scripts/python.exe voyager1_density_extraction.py --real-data --days-back 14 --nasa-style

"""

import argparse
import datetime
import tempfile
import urllib.request
import urllib.error
from pathlib import Path
from typing import Tuple, Optional, List
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LogNorm

try:
    import cdflib
    _CDFLIB_AVAILABLE = True
except ImportError:
    _CDFLIB_AVAILABLE = False

try:
    from scipy import signal
    from scipy.interpolate import interp1d
    _SCIPY_AVAILABLE = True
except ImportError:
    _SCIPY_AVAILABLE = False


class VoyagerPWSData:
    """Class to handle Voyager 1 Plasma Wave Subsystem data."""
    
    def __init__(self):
        self.time = None
        self.frequencies = None
        self.wave_intensity = None
        self.electric_field = None
        self.metadata = {}
    
    def load_from_cdf(self, cdf_path: Path) -> bool:
        """Load PWS data from CDF file."""
        if not _CDFLIB_AVAILABLE:
            raise ImportError("cdflib required for CDF file reading")
        
        try:
            cdf = cdflib.CDF(str(cdf_path))
            info = cdf.cdf_info()
            print(f"CDF variables: {info['rVariables']}")
            
            # Common PWS variable names
            time_vars = ['Epoch', 'EPOCH', 'time', 'TIME']
            freq_vars = ['Frequency', 'FREQUENCY', 'freq', 'FREQ']
            intensity_vars = ['Intensity', 'INTENSITY', 'Wave_Intensity', 'Electric_Field']
            
            # Find available variables
            time_var = next((v for v in time_vars if v in info['rVariables']), None)
            freq_var = next((v for v in freq_vars if v in info['rVariables']), None)
            intensity_var = next((v for v in intensity_vars if v in info['rVariables']), None)
            
            if time_var:
                time_data = cdf.varget(time_var)
                self.time = cdflib.cdfepoch.to_datetime(time_data)
            
            if freq_var:
                self.frequencies = cdf.varget(freq_var)
            
            if intensity_var:
                self.wave_intensity = cdf.varget(intensity_var)
            
            self.metadata = {
                'source': 'CDF file',
                'file_path': str(cdf_path),
                'variables': info['rVariables']
            }
            
            return True
            
        except Exception as e:
            print(f"Error loading CDF: {e}")
            return False
    
    def load_synthetic_data(self, duration_hours: float = 24, 
                           freq_range: Tuple[float, float] = (10, 1000)) -> None:
        """Generate synthetic PWS data for testing and demonstration."""
        print(f"Generating synthetic PWS data for {duration_hours} hours...")
        
        # Time array (1-minute resolution)
        n_points = int(duration_hours * 60)
        end_time = datetime.datetime.now(datetime.timezone.utc)
        start_time = end_time - datetime.timedelta(hours=duration_hours)
        self.time = pd.date_range(start_time, end_time, periods=n_points).to_pydatetime()
        
        # Frequency array (logarithmically spaced)
        n_freq = 64
        self.frequencies = np.logspace(np.log10(freq_range[0]), np.log10(freq_range[1]), n_freq)
        
        # Generate realistic plasma wave intensity
        self.wave_intensity = np.zeros((n_points, n_freq))
        
        for i, t in enumerate(self.time):
            # Base noise level
            base_noise = np.random.lognormal(mean=-2, sigma=0.5, size=n_freq)
            
            # Plasma frequency cutoff (~2-4 kHz in interstellar medium)
            plasma_freq = 2000 + 500 * np.sin(2 * np.pi * i / (n_points / 10))
            cutoff_effect = np.exp(-(self.frequencies - plasma_freq)**2 / (500**2))
            
            # Langmuir waves near plasma frequency
            langmuir_enhancement = 10 * cutoff_effect
            
            # Low-frequency turbulence (Alfvén waves, etc.)
            turbulence = 5 * np.exp(-self.frequencies / 100) * (1 + 0.3 * np.random.randn())
            
            # Occasional wave events (solar wind interactions, etc.)
            if np.random.random() < 0.05:  # 5% chance
                event_freq = np.random.uniform(50, 800)
                event_strength = np.random.uniform(20, 100)
                event_width = np.random.uniform(10, 50)
                event_enhancement = event_strength * np.exp(-(self.frequencies - event_freq)**2 / event_width**2)
            else:
                event_enhancement = 0
            
            # Combine all components
            self.wave_intensity[i, :] = base_noise + langmuir_enhancement + turbulence + event_enhancement
        
        # Add electric field estimate (simplified)
        self.electric_field = np.mean(self.wave_intensity, axis=1)
        
        self.metadata = {
            'source': 'synthetic',
            'duration_hours': duration_hours,
            'frequency_range': freq_range,
            'time_resolution': '1 minute',
            'frequency_channels': n_freq
        }


def fetch_real_pws_data(days_back: int = 7) -> Optional[Path]:
    """Attempt to fetch real Voyager 1 PWS data from NASA archives."""
    end_date = datetime.datetime.now(datetime.timezone.utc)
    start_date = end_date - datetime.timedelta(days=days_back)
    
    # NASA PDS Planetary Plasma Interactions (PPI) node URLs
    base_urls = [
        "https://pds-ppi.igpp.ucla.edu/data/VG1-S-PWS-4-SUMM-SA/",
        "https://spdf.gsfc.nasa.gov/pub/data/voyager/voyager1/plasma_wave/"
    ]
    
    for base_url in base_urls:
        try:
            year = end_date.year
            filename = f"vg1_pws_sa_{year}.cdf"
            url = f"{base_url}{year}/{filename}"
            
            print(f"Attempting to fetch PWS data from: {url}")
            
            temp_file = tempfile.NamedTemporaryFile(suffix='.cdf', delete=False)
            temp_path = Path(temp_file.name)
            temp_file.close()
            
            urllib.request.urlretrieve(url, temp_path)
            print(f"Successfully downloaded PWS data to: {temp_path}")
            return temp_path
            
        except Exception as e:
            print(f"Failed to fetch from {base_url}: {e}")
            continue
    
    return None


def plot_wave_spectrum(pws_data: VoyagerPWSData, time_index: Optional[int] = None) -> None:
    """Plot frequency spectrum at a specific time."""
    if time_index is None:
        time_index = len(pws_data.time) // 2  # Middle of dataset
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    spectrum = pws_data.wave_intensity[time_index, :]
    ax.loglog(pws_data.frequencies, spectrum, 'b-', linewidth=2)
    
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Wave Intensity (V²/m²/Hz)')
    ax.set_title(f'Voyager 1 PWS Spectrum\n{pws_data.time[time_index].strftime("%Y-%m-%d %H:%M UTC")}')
    ax.grid(True, alpha=0.3)
    
    # Annotate key frequency ranges
    ax.axvspan(10, 100, alpha=0.2, color='red', label='Low-freq turbulence')
    ax.axvspan(1000, 5000, alpha=0.2, color='orange', label='Plasma frequency range')
    ax.axvspan(10000, 50000, alpha=0.2, color='green', label='Upper hybrid range')
    
    ax.legend()
    plt.tight_layout()
    plt.show()


def plot_spectrogram(pws_data: VoyagerPWSData, freq_range: Optional[Tuple[float, float]] = None) -> None:
    """Create dynamic spectrogram of plasma wave data."""
    if freq_range:
        freq_mask = (pws_data.frequencies >= freq_range[0]) & (pws_data.frequencies <= freq_range[1])
        frequencies = pws_data.frequencies[freq_mask]
        intensity = pws_data.wave_intensity[:, freq_mask]
    else:
        frequencies = pws_data.frequencies
        intensity = pws_data.wave_intensity
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Convert time to matplotlib format
    time_nums = mdates.date2num(pws_data.time)
    
    # Create meshgrid for plotting
    T, F = np.meshgrid(time_nums, frequencies)
    
    # Plot spectrogram
    im = ax.pcolormesh(T, F, intensity.T, norm=LogNorm(vmin=0.01, vmax=100), 
                       cmap='viridis', shading='auto')
    
    ax.set_yscale('log')
    ax.set_ylabel('Frequency (Hz)')
    ax.set_xlabel('Time (UTC)')
    ax.set_title('Voyager 1 Plasma Wave Spectrogram')
    
    # Format x-axis dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
    plt.xticks(rotation=45)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Wave Intensity (V²/m²/Hz)')
    
    plt.tight_layout()
    plt.show()


def plot_time_series(pws_data: VoyagerPWSData, freq_band: Optional[Tuple[float, float]] = None) -> None:
    """Plot time series of integrated wave intensity."""
    if freq_band:
        freq_mask = (pws_data.frequencies >= freq_band[0]) & (pws_data.frequencies <= freq_band[1])
        integrated_intensity = np.mean(pws_data.wave_intensity[:, freq_mask], axis=1)
        title_suffix = f" ({freq_band[0]:.0f}-{freq_band[1]:.0f} Hz)"
    else:
        integrated_intensity = np.mean(pws_data.wave_intensity, axis=1)
        title_suffix = " (All frequencies)"
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Wave intensity
    ax1.plot(pws_data.time, integrated_intensity, 'b-', linewidth=1)
    ax1.set_ylabel('Integrated Wave Intensity')
    ax1.set_title(f'Voyager 1 PWS Time Series{title_suffix}')
    ax1.grid(True, alpha=0.3)
    
    # Electric field (if available)
    if pws_data.electric_field is not None:
        ax2.plot(pws_data.time, pws_data.electric_field, 'r-', linewidth=1)
        ax2.set_ylabel('Electric Field (mV/m)')
        ax2.grid(True, alpha=0.3)
    
    ax2.set_xlabel('Time (UTC)')
    
    # Format x-axis
    for ax in [ax1, ax2]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def analyze_plasma_density(pws_data: VoyagerPWSData) -> None:
    """Estimate electron plasma density from wave data."""
    print("\n=== Plasma Density Analysis ===")
    
    # Find approximate plasma frequency (peak in low-frequency range)
    low_freq_mask = (pws_data.frequencies >= 1000) & (pws_data.frequencies <= 5000)
    
    plasma_frequencies = []
    for i in range(len(pws_data.time)):
        spectrum = pws_data.wave_intensity[i, low_freq_mask]
        freq_subset = pws_data.frequencies[low_freq_mask]
        
        # Find peak frequency
        peak_idx = np.argmax(spectrum)
        peak_freq = freq_subset[peak_idx]
        plasma_frequencies.append(peak_freq)
    
    plasma_frequencies = np.array(plasma_frequencies)
    
    # Convert to electron density using plasma frequency relation:
    # f_pe = (1/2π) * sqrt(n_e * e² / (ε_0 * m_e))
    # n_e = (2π * f_pe)² * ε_0 * m_e / e²
    
    e = 1.602e-19  # electron charge (C)
    m_e = 9.109e-31  # electron mass (kg)
    epsilon_0 = 8.854e-12  # permittivity (F/m)
    
    electron_density = (2 * np.pi * plasma_frequencies)**2 * epsilon_0 * m_e / e**2
    electron_density /= 1e6  # convert to cm⁻³
    
    print(f"Mean plasma frequency: {np.mean(plasma_frequencies):.0f} ± {np.std(plasma_frequencies):.0f} Hz")
    print(f"Mean electron density: {np.mean(electron_density):.3f} ± {np.std(electron_density):.3f} cm⁻³")
    print(f"Density range: {np.min(electron_density):.3f} - {np.max(electron_density):.3f} cm⁻³")
    
    # Typical interstellar medium: 0.1-1 cm⁻³
    print("\nReference values:")
    print("• Heliosheath: ~0.01-0.1 cm⁻³")
    print("• Local interstellar medium: ~0.1-1 cm⁻³")
    print("• Solar wind (1 AU): ~5-10 cm⁻³")


def main(argv: Optional[List[str]] = None) -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Analyze Voyager 1 Plasma Wave Subsystem data')
    
    parser.add_argument('--real-data', action='store_true',
                       help='Attempt to fetch real PWS data from NASA archives')
    parser.add_argument('--synthetic', action='store_true',
                       help='Use synthetic PWS data for demonstration')
    parser.add_argument('--days-back', type=int, default=7,
                       help='Days of historical data to fetch (default: 7)')
    parser.add_argument('--duration-hours', type=float, default=24,
                       help='Hours of synthetic data to generate (default: 24)')
    parser.add_argument('--frequency-range', type=float, nargs=2, default=[10, 10000],
                       help='Frequency range for analysis in Hz (default: 10 10000)')
    parser.add_argument('--spectrogram', action='store_true',
                       help='Show dynamic spectrogram')
    parser.add_argument('--time-series', action='store_true',
                       help='Show time series plot')
    parser.add_argument('--spectrum', action='store_true',
                       help='Show frequency spectrum')
    parser.add_argument('--density-analysis', action='store_true',
                       help='Perform plasma density analysis')
    
    args = parser.parse_args(argv)
    
    # Initialize PWS data object
    pws_data = VoyagerPWSData()
    
    # Load data
    if args.real_data:
        print("Attempting to fetch real Voyager 1 PWS data...")
        cdf_path = fetch_real_pws_data(args.days_back)
        if cdf_path and pws_data.load_from_cdf(cdf_path):
            print("Successfully loaded real PWS data")
        else:
            print("Failed to load real data, falling back to synthetic")
            pws_data.load_synthetic_data(args.duration_hours, tuple(args.frequency_range))
    else:
        pws_data.load_synthetic_data(args.duration_hours, tuple(args.frequency_range))
    
    # Print data summary
    print(f"\n=== PWS Data Summary ===")
    print(f"Source: {pws_data.metadata.get('source', 'Unknown')}")
    print(f"Time range: {pws_data.time[0]} to {pws_data.time[-1]}")
    print(f"Duration: {len(pws_data.time)} time points")
    print(f"Frequency range: {pws_data.frequencies[0]:.1f} - {pws_data.frequencies[-1]:.1f} Hz")
    print(f"Frequency channels: {len(pws_data.frequencies)}")
    
    # Generate plots based on arguments
    if args.spectrogram or not any([args.time_series, args.spectrum, args.density_analysis]):
        plot_spectrogram(pws_data, tuple(args.frequency_range) if args.frequency_range != [10, 10000] else None)
    
    if args.time_series:
        plot_time_series(pws_data, tuple(args.frequency_range) if args.frequency_range != [10, 10000] else None)
    
    if args.spectrum:
        plot_wave_spectrum(pws_data)
    
    if args.density_analysis:
        analyze_plasma_density(pws_data)


if __name__ == '__main__':
    main()
