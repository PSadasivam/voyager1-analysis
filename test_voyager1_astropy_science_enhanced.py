#!/usr/bin/env python3
"""
test_voyager1_astropy_science_enhanced.py
----------------------------------------

Unit tests for the enhanced Voyager 1 data visualization script.

This test suite covers:
- Ephemeris data fetching
- Data file reading (CSV/CDF)
- Real data fetching and fallback mechanisms
- Command line argument parsing
- Error handling and edge cases

Usage:
    python -m unittest test_voyager1_astropy_science_enhanced.py
    or
    python test_voyager1_astropy_science_enhanced.py

# Run all tests with verbose output
python -m unittest test_voyager1_astropy_science_enhanced.py -v

# Run specific test class
python -m unittest test_voyager1_astropy_science_enhanced.TestEphemerisData -v

# Run directly
python test_voyager1_astropy_science_enhanced.py

"""

import unittest
import datetime
import tempfile
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import io

import numpy as np
import pandas as pd

# Add the project directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import the module to test
import voyager1_astropy_science_enhanced as v1_module


class TestEphemerisData(unittest.TestCase):
    """Test ephemeris data fetching functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_datetime = datetime.datetime(2025, 8, 16, 12, 0, 0)
    
    def test_fetch_ephemeris_fallback(self):
        """Test ephemeris fetching with astroquery unavailable."""
        with patch.object(v1_module, '_ASTROQUERY_AVAILABLE', False):
            v_pos, e_pos = v1_module.fetch_ephemeris(self.test_datetime)
            
            # Should return fallback positions
            expected_voyager = np.array([15.0, 20.0, 25.0])
            expected_earth = np.array([1.0, 0.0, 0.0])
            
            np.testing.assert_array_equal(v_pos, expected_voyager)
            np.testing.assert_array_equal(e_pos, expected_earth)
    
    @patch('voyager1_astropy_science_enhanced.Horizons')
    def test_fetch_ephemeris_success(self, mock_horizons):
        """Test successful ephemeris fetching."""
        # Mock the astroquery response
        mock_eph_voyager = {'x': [100.0], 'y': [200.0], 'z': [300.0]}
        mock_eph_earth = {'x': [1.0], 'y': [0.5], 'z': [0.0]}
        
        mock_obj_voyager = MagicMock()
        mock_obj_voyager.vectors.return_value = mock_eph_voyager
        
        mock_obj_earth = MagicMock()
        mock_obj_earth.vectors.return_value = mock_eph_earth
        
        mock_horizons.side_effect = [mock_obj_voyager, mock_obj_earth]
        
        with patch.object(v1_module, '_ASTROQUERY_AVAILABLE', True):
            v_pos, e_pos = v1_module.fetch_ephemeris(self.test_datetime)
            
            expected_voyager = np.array([100.0, 200.0, 300.0])
            expected_earth = np.array([1.0, 0.5, 0.0])
            
            np.testing.assert_array_equal(v_pos, expected_voyager)
            np.testing.assert_array_equal(e_pos, expected_earth)
    
    @patch('voyager1_astropy_science_enhanced.Horizons')
    def test_fetch_ephemeris_error_fallback(self, mock_horizons):
        """Test ephemeris fetching error handling."""
        mock_horizons.side_effect = Exception("Network error")
        
        with patch.object(v1_module, '_ASTROQUERY_AVAILABLE', True):
            v_pos, e_pos = v1_module.fetch_ephemeris(self.test_datetime)
            
            # Should return fallback positions on error
            expected_voyager = np.array([15.0, 20.0, 25.0])
            expected_earth = np.array([1.0, 0.0, 0.0])
            
            np.testing.assert_array_equal(v_pos, expected_voyager)
            np.testing.assert_array_equal(e_pos, expected_earth)


class TestDataFileHandling(unittest.TestCase):
    """Test CSV and CDF file reading functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary CSV file for testing
        self.temp_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        test_data = """time,B_field_nT
2025-08-16 00:00:00,0.4
2025-08-16 00:01:00,0.41
2025-08-16 00:02:00,0.39
"""
        self.temp_csv.write(test_data)
        self.temp_csv.close()
        self.temp_csv_path = Path(self.temp_csv.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.temp_csv_path.exists():
            self.temp_csv_path.unlink()
    
    @patch('matplotlib.pyplot.show')
    def test_plot_csv_success(self, mock_show):
        """Test successful CSV file plotting."""
        # Should not raise an exception
        try:
            v1_module.plot_csv(self.temp_csv_path)
        except Exception as e:
            self.fail(f"plot_csv raised an exception: {e}")
        
        # Verify that matplotlib.show was called
        mock_show.assert_called_once()
    
    def test_plot_csv_file_not_found(self):
        """Test CSV plotting with non-existent file."""
        non_existent_path = Path("non_existent_file.csv")
        
        with self.assertRaises(RuntimeError):
            v1_module.plot_csv(non_existent_path)
    
    def test_plot_csv_insufficient_columns(self):
        """Test CSV plotting with insufficient columns."""
        # Create a CSV with only one column
        temp_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        test_data = "time\n2025-08-16 00:00:00\n"
        temp_csv.write(test_data)
        temp_csv.close()
        temp_csv_path = Path(temp_csv.name)
        
        try:
            with self.assertRaises(ValueError):
                v1_module.plot_csv(temp_csv_path)
        finally:
            temp_csv_path.unlink()
    
    def test_plot_cdf_without_cdflib(self):
        """Test CDF plotting when cdflib is not available."""
        with patch.object(v1_module, '_CDFLIB_AVAILABLE', False):
            with self.assertRaises(ImportError):
                v1_module.plot_cdf(Path("dummy.cdf"))


class TestRealDataFetching(unittest.TestCase):
    """Test real data fetching from NASA archives."""
    
    @patch('urllib.request.urlretrieve')
    @patch('tempfile.NamedTemporaryFile')
    def test_fetch_real_voyager_data_success(self, mock_tempfile, mock_urlretrieve):
        """Test successful real data fetching."""
        # Mock temporary file creation
        mock_temp = MagicMock()
        mock_temp.name = "/tmp/test_file.cdf"
        mock_tempfile.return_value = mock_temp
        
        # Mock successful download
        mock_urlretrieve.return_value = None
        
        result = v1_module.fetch_real_voyager_data(7)
        
        self.assertIsInstance(result, Path)
        self.assertEqual(str(result), "/tmp/test_file.cdf")
        mock_urlretrieve.assert_called_once()
    
    @patch('urllib.request.urlretrieve')
    def test_fetch_real_voyager_data_failure(self, mock_urlretrieve):
        """Test real data fetching failure and fallback."""
        # Mock download failure for both current and previous year
        mock_urlretrieve.side_effect = Exception("Download failed")
        
        with self.assertRaises(RuntimeError):
            v1_module.fetch_real_voyager_data(7)
    
    def test_fetch_real_voyager_data_alternative(self):
        """Test alternative realistic data generation."""
        result_path = v1_module.fetch_real_voyager_data_alternative()
        
        # Verify the file was created
        self.assertTrue(result_path.exists())
        self.assertTrue(str(result_path).endswith('.csv'))
        
        # Verify the content is valid CSV
        df = pd.read_csv(result_path)
        self.assertEqual(list(df.columns), ['time', 'B_field_nT'])
        self.assertGreater(len(df), 0)
        
        # Verify magnetic field values are reasonable
        self.assertTrue(all(df['B_field_nT'] >= 0))  # Non-negative
        self.assertTrue(all(df['B_field_nT'] < 2.0))  # Reasonable upper bound
        
        # Clean up
        result_path.unlink()


class TestCommandLineInterface(unittest.TestCase):
    """Test command line argument parsing and main function."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a test CSV file
        self.temp_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        test_data = """time,B_field_nT
2025-08-16 00:00:00,0.4
2025-08-16 00:01:00,0.41
"""
        self.temp_csv.write(test_data)
        self.temp_csv.close()
        self.temp_csv_path = Path(self.temp_csv.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.temp_csv_path.exists():
            self.temp_csv_path.unlink()
    
    @patch('matplotlib.pyplot.show')
    @patch('voyager1_astropy_science_enhanced.fetch_ephemeris')
    def test_main_with_csv_argument(self, mock_fetch_eph, mock_show):
        """Test main function with CSV argument."""
        mock_fetch_eph.return_value = (np.array([1, 2, 3]), np.array([4, 5, 6]))
        
        # Test with CSV argument
        argv = ['--csv', str(self.temp_csv_path)]
        
        try:
            v1_module.main(argv)
        except SystemExit:
            pass  # argparse may call sys.exit, which is fine for testing
        
        mock_fetch_eph.assert_called_once()
        self.assertEqual(mock_show.call_count, 2)  # Position plot + CSV plot
    
    @patch('matplotlib.pyplot.show')
    @patch('voyager1_astropy_science_enhanced.fetch_ephemeris')
    @patch('voyager1_astropy_science_enhanced.fetch_real_voyager_data_alternative')
    def test_main_with_real_data_flag(self, mock_fetch_alt, mock_fetch_eph, mock_show):
        """Test main function with real-data flag."""
        mock_fetch_eph.return_value = (np.array([1, 2, 3]), np.array([4, 5, 6]))
        mock_fetch_alt.return_value = self.temp_csv_path
        
        # Test with real-data flag
        argv = ['--real-data', '--days-back', '7']
        
        try:
            v1_module.main(argv)
        except SystemExit:
            pass
        
        mock_fetch_eph.assert_called_once()
    
    @patch('builtins.print')
    @patch('matplotlib.pyplot.show')
    @patch('voyager1_astropy_science_enhanced.fetch_ephemeris')
    def test_main_no_sample_data(self, mock_fetch_eph, mock_show, mock_print):
        """Test main function when no sample data is found."""
        mock_fetch_eph.return_value = (np.array([1, 2, 3]), np.array([4, 5, 6]))
        
        # Test with no arguments and no sample files
        with patch('pathlib.Path.exists', return_value=False):
            try:
                v1_module.main([])
            except SystemExit:
                pass
        
        # Should print message about no sample data
        mock_print.assert_called()
        call_args = [call[0][0] for call in mock_print.call_args_list]
        self.assertTrue(any("No data file provided and no sample data found" in arg for arg in call_args))


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def test_invalid_file_paths(self):
        """Test handling of invalid file paths."""
        invalid_path = Path("/this/path/does/not/exist.csv")
        
        with self.assertRaises(RuntimeError):
            v1_module.plot_csv(invalid_path)
    
    def test_fetch_ephemeris_with_invalid_datetime(self):
        """Test ephemeris fetching with edge case datetime."""
        # Test with a very future date
        future_date = datetime.datetime(3000, 1, 1)
        
        # Should not crash and return some result
        v_pos, e_pos = v1_module.fetch_ephemeris(future_date)
        
        self.assertIsInstance(v_pos, np.ndarray)
        self.assertIsInstance(e_pos, np.ndarray)
        self.assertEqual(len(v_pos), 3)
        self.assertEqual(len(e_pos), 3)


class TestDataValidation(unittest.TestCase):
    """Test data validation and scientific accuracy."""
    
    def test_realistic_data_generation(self):
        """Test that generated realistic data has scientific properties."""
        data_path = v1_module.fetch_real_voyager_data_alternative()
        
        try:
            df = pd.read_csv(data_path)
            
            # Test time series properties
            self.assertTrue('time' in df.columns)
            self.assertTrue('B_field_nT' in df.columns)
            
            # Convert time column to datetime
            df['time'] = pd.to_datetime(df['time'])
            
            # Check time series is sequential
            time_diffs = df['time'].diff().dropna()
            self.assertTrue(all(time_diffs > pd.Timedelta(0)))  # Monotonic increasing
            
            # Check magnetic field values are in realistic range for interstellar space
            b_field = df['B_field_nT']
            self.assertTrue(all(b_field >= 0))  # Non-negative
            self.assertTrue(all(b_field <= 2.0))  # Reasonable upper bound
            mean_field = b_field.mean()
            self.assertAlmostEqual(mean_field, 0.4, delta=0.2)  # Around expected interstellar value
            
        finally:
            data_path.unlink()


if __name__ == '__main__':
    # Configure test runner
    unittest.main(verbosity=2, buffer=True)
