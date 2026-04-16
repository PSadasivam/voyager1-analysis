#!/usr/bin/env python3
"""
verify_voyager_position.py
--------------------------
Verify the accuracy of Voyager 1 current position in our trajectory script.
"""

import datetime
import numpy as np

try:
    from astroquery.jplhorizons import Horizons
    from astropy.coordinates import SkyCoord
    from astropy import units as u
    _ASTROQUERY_AVAILABLE = True
except Exception:
    _ASTROQUERY_AVAILABLE = False

def check_current_position():
    """Check actual vs synthetic Voyager 1 position."""
    now = datetime.datetime.now(datetime.timezone.utc)
    print(f"=== Voyager 1 Position Verification ===")
    print(f"Date: {now.strftime('%Y-%m-%d %H:%M UTC')}")
    print()
    
    # Synthetic model from our script
    synthetic_distance = 160.0 + max(0, (now.year - 2025)) * 3.2
    
    # Approximate direction (RA ~17h, Dec ~12°)
    ra_hours = 17.0
    dec_degrees = 12.0
    ra_rad = np.radians(ra_hours * 15.0)
    dec_rad = np.radians(dec_degrees)
    
    direction = np.array([
        np.cos(dec_rad) * np.cos(ra_rad),
        np.cos(dec_rad) * np.sin(ra_rad),
        np.sin(dec_rad)
    ])
    
    synthetic_pos = synthetic_distance * direction
    
    print("SYNTHETIC MODEL:")
    print(f"Distance: {synthetic_distance:.2f} AU")
    print(f"X: {synthetic_pos[0]:.3f} AU")
    print(f"Y: {synthetic_pos[1]:.3f} AU") 
    print(f"Z: {synthetic_pos[2]:.3f} AU")
    print(f"RA: {ra_hours:.1f} hours")
    print(f"Dec: {dec_degrees:.1f} degrees")
    print()
    
    if _ASTROQUERY_AVAILABLE:
        try:
            print("REAL DATA (JPL HORIZONS):")
            obj = Horizons(id='Voyager 1', location='@sun', epochs=now.strftime('%Y-%m-%d %H:%M'))
            vectors = obj.vectors()
            
            x = float(vectors['x'][0])
            y = float(vectors['y'][0])
            z = float(vectors['z'][0])
            real_distance = np.sqrt(x**2 + y**2 + z**2)
            
            print(f"Distance: {real_distance:.2f} AU")
            print(f"X: {x:.3f} AU")
            print(f"Y: {y:.3f} AU")
            print(f"Z: {z:.3f} AU")
            
            # Convert to RA/Dec
            coord = SkyCoord(x=x*u.au, y=y*u.au, z=z*u.au, representation_type='cartesian')
            ra_dec = coord.icrs
            print(f"RA: {ra_dec.ra.to(u.hourangle):.1f}")
            print(f"Dec: {ra_dec.dec:.1f}")
            print()
            
            # Accuracy analysis
            print("ACCURACY ANALYSIS:")
            distance_error = abs(real_distance - synthetic_distance)
            position_error = np.linalg.norm([x - synthetic_pos[0], 
                                           y - synthetic_pos[1], 
                                           z - synthetic_pos[2]])
            
            print(f"Distance error: {distance_error:.2f} AU ({distance_error/real_distance*100:.1f}%)")
            print(f"Position error: {position_error:.2f} AU")
            
            if distance_error < 5.0:
                print("[PASS] Distance accuracy: GOOD (within 5 AU)")
            else:
                print("[WARN] Distance accuracy: POOR (>5 AU error)")
                
            if position_error < 10.0:
                print("[PASS] Position accuracy: GOOD (within 10 AU)")
            else:
                print("[WARN] Position accuracy: POOR (>10 AU error)")
                
            # Known facts about Voyager 1 (as of 2025)
            print()
            print("KNOWN FACTS (for reference):")
            print("• Voyager 1 is moving ~3.6 AU/year outward")
            print("• It crossed heliopause at ~121 AU in Aug 2012")
            print("• As of 2025, it should be ~160+ AU from Sun")
            print("• Direction: roughly toward constellation Ophiuchus")
            
        except Exception as e:
            print(f"Could not fetch real data: {e}")
            print("Using synthetic model only.")
    else:
        print("astroquery not available - cannot verify against real data")

if __name__ == '__main__':
    check_current_position()
