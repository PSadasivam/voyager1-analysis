import unittest
from pathlib import Path
import tempfile
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for tests
import voyager1_magneticfield_nTS_analysis as v1mag

class TestVoyager1MagneticFieldAnalysis(unittest.TestCase):
    def setUp(self):
        # Use the provided CSV file for tests
        self.csv_path = Path(__file__).resolve().parent / 'voyager1_magnetometer_unittest.csv'
        self.df = pd.read_csv(self.csv_path, parse_dates=['time'])

    def test_plot_csv_runs_without_error(self):
        # Should not raise any exceptions
        try:
            v1mag.plot_csv(self.csv_path)
        except Exception as e:
            self.fail(f"plot_csv raised an exception: {e}")

    def test_csv_data_shape(self):
        # Check that the CSV has the expected columns and rows
        self.assertIn('time', self.df.columns)
        self.assertIn('B_nT', self.df.columns)
        self.assertEqual(len(self.df), 5)

    def test_fetch_ephemeris_returns_arrays(self):
        import datetime
        now = datetime.datetime.now(datetime.UTC)
        v_pos, e_pos = v1mag.fetch_ephemeris(now)
        self.assertEqual(len(v_pos), 3)
        self.assertEqual(len(e_pos), 3)
        self.assertIsInstance(v_pos, type(e_pos))

    def test_main_with_csv(self):
        # Simulate running main with --csv argument
        argv = ["--csv", str(self.csv_path)]
        try:
            v1mag.main(argv)
        except Exception as e:
            self.fail(f"main(argv) with --csv raised an exception: {e}")

if __name__ == "__main__":
    unittest.main()
