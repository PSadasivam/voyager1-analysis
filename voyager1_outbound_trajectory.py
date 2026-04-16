#!/usr/bin/env python3
"""
voyager1_outbound_trajectory.py
-------------------------------

Enhanced Voyager 1 trajectory visualization showing the full outbound path from launch
through Jupiter and Saturn flybys to current position, overlaid on a 3D heliocentric plot.

Based on voyager1_magneticfield_nTS_analysis.py but extended to show trajectory over time
rather than just a snapshot position.

Key mission events:
- Launch: September 5, 1977
- Jupiter flyby: March 5, 1979  
- Saturn flyby: November 12, 1980
- Heliopause crossing: August 25, 2012
- Current position: Dynamic (today's date)

Usage:
    python voyager1_outbound_trajectory.py
    python voyager1_outbound_trajectory.py --step-days 30
    python voyager1_outbound_trajectory.py --fallback
"""

import argparse
import datetime
import sys
from pathlib import Path
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    from astroquery.jplhorizons import Horizons
    _ASTROQUERY_AVAILABLE = True
except Exception:
    _ASTROQUERY_AVAILABLE = False

try:
    from astropy import units as u
    from astropy.coordinates import SkyCoord
    _ASTROPY_AVAILABLE = True
except Exception:
    _ASTROPY_AVAILABLE = False


@dataclass
class MissionEvent:
    """Represents a key mission event with date and visualization properties."""
    name: str
    date: datetime.datetime
    color: str
    marker: str = 'o'
    size: int = 80


# Key Voyager 1 mission events
MISSION_EVENTS = [
    MissionEvent("Launch", datetime.datetime(1977, 9, 5, tzinfo=datetime.timezone.utc), 
                 "#1f77b4", marker='*', size=120),
    MissionEvent("Jupiter Flyby", datetime.datetime(1979, 3, 5, tzinfo=datetime.timezone.utc), 
                 "#ff7f0e", marker='o', size=100),
    MissionEvent("Saturn Flyby", datetime.datetime(1980, 11, 12, tzinfo=datetime.timezone.utc), 
                 "#2ca02c", marker='s', size=100),
    MissionEvent("Pale Blue Dot", datetime.datetime(1990, 2, 14, tzinfo=datetime.timezone.utc), 
                 "#17becf", marker='p', size=90),
    MissionEvent("Termination Shock", datetime.datetime(2004, 12, 16, tzinfo=datetime.timezone.utc), 
                 "#e377c2", marker='^', size=90),
    MissionEvent("Heliopause", datetime.datetime(2012, 8, 25, tzinfo=datetime.timezone.utc), 
                 "#d62728", marker='D', size=90),
]


def fetch_trajectory_real(start_date: datetime.datetime, end_date: datetime.datetime, 
                         step_days: int = 30) -> Tuple[np.ndarray, List[datetime.datetime]]:
    """
    Fetch real Voyager 1 trajectory data from JPL HORIZONS.
    
    Parameters
    ----------
    start_date : datetime.datetime
        Start date for trajectory query
    end_date : datetime.datetime  
        End date for trajectory query
    step_days : int
        Time step in days between trajectory points
        
    Returns
    -------
    trajectory : np.ndarray
        Array of shape (N, 3) containing [x, y, z] positions in AU
    dates : List[datetime.datetime]
        Corresponding dates for each trajectory point
    """
    if not _ASTROQUERY_AVAILABLE:
        raise RuntimeError("astroquery not available for real trajectory data")
    
    try:
        # Format dates for HORIZONS
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        step_str = f"{step_days}d"
        
        print(f"Querying JPL HORIZONS for Voyager 1 trajectory...")
        print(f"Date range: {start_str} to {end_str}, step: {step_str}")
        
        # Query Voyager 1 heliocentric trajectory
        obj = Horizons(id="Voyager 1", location="@sun", 
                      epochs={'start': start_str, 'stop': end_str, 'step': step_str})
        vectors = obj.vectors()
        
        # Extract position vectors
        x_coords = np.array(vectors['x'], dtype=float)
        y_coords = np.array(vectors['y'], dtype=float) 
        z_coords = np.array(vectors['z'], dtype=float)
        
        trajectory = np.column_stack([x_coords, y_coords, z_coords])
        
        # Generate corresponding dates
        dates = []
        current_date = start_date
        delta = datetime.timedelta(days=step_days)
        for _ in range(len(trajectory)):
            dates.append(current_date)
            current_date += delta
            
        print(f"Successfully retrieved {len(trajectory)} trajectory points")
        return trajectory, dates
        
    except Exception as e:
        raise RuntimeError(f"Failed to query HORIZONS: {e}")


def fetch_trajectory_synthetic(start_date: datetime.datetime, end_date: datetime.datetime,
                              step_days: int = 30) -> Tuple[np.ndarray, List[datetime.datetime]]:
    """
    Generate synthetic Voyager 1 trajectory based on known mission parameters.
    
    Uses approximate distances and directions based on actual mission data.
    """
    print("Generating synthetic Voyager 1 trajectory...")
    
    # Key distances at mission events (AU, based on NASA data)
    event_distances = {
        datetime.datetime(1977, 9, 5, tzinfo=datetime.timezone.utc): 1.0,      # Launch
        datetime.datetime(1979, 3, 5, tzinfo=datetime.timezone.utc): 5.2,     # Jupiter  
        datetime.datetime(1980, 11, 12, tzinfo=datetime.timezone.utc): 9.5,   # Saturn
        datetime.datetime(1990, 2, 14, tzinfo=datetime.timezone.utc): 40.0,   # Pale Blue Dot
        datetime.datetime(2004, 12, 16, tzinfo=datetime.timezone.utc): 94.0,  # Termination Shock
        datetime.datetime(2012, 8, 25, tzinfo=datetime.timezone.utc): 121.0,  # Heliopause
        # Updated calculation for current position (more accurate)
        # Voyager 1 moves ~3.6 AU/year since heliopause crossing
        end_date: 121.0 + ((end_date - datetime.datetime(2012, 8, 25, tzinfo=datetime.timezone.utc)).days / 365.25) * 3.6
    }
    
    # Updated Voyager 1 direction based on more recent data
    # Current heading: RA ≈ 17h 13m, Dec ≈ +12° 5' (J2000)
    ra_hours = 17.22  # More precise RA
    dec_degrees = 12.08  # More precise Dec
    ra_rad = math.radians(ra_hours * 15.0)
    dec_rad = math.radians(dec_degrees)
    
    # Unit direction vector
    direction = np.array([
        math.cos(dec_rad) * math.cos(ra_rad),
        math.cos(dec_rad) * math.sin(ra_rad), 
        math.sin(dec_rad)
    ])
    
    # Generate time points
    dates = []
    current_date = start_date
    delta = datetime.timedelta(days=step_days)
    while current_date <= end_date:
        dates.append(current_date)
        current_date += delta
    
    # Interpolate distances for each time point
    trajectory = []
    event_dates = sorted(event_distances.keys())
    
    for date in dates:
        # Find surrounding event dates for interpolation
        distance = 1.0  # default
        
        for i in range(len(event_dates) - 1):
            date1, date2 = event_dates[i], event_dates[i + 1]
            if date1 <= date <= date2:
                # Linear interpolation between events
                t = (date - date1).total_seconds() / (date2 - date1).total_seconds()
                dist1, dist2 = event_distances[date1], event_distances[date2]
                distance = dist1 + t * (dist2 - dist1)
                break
        else:
            # If beyond last event, use final distance
            if date >= event_dates[-1]:
                distance = event_distances[event_dates[-1]]
        
        # Position = distance * direction
        position = distance * direction
        trajectory.append(position)
    
    trajectory = np.array(trajectory)
    print(f"Generated {len(trajectory)} synthetic trajectory points")
    return trajectory, dates


def fetch_current_earth_position() -> Optional[np.ndarray]:
    """Fetch current Earth position for reference."""
    if not _ASTROQUERY_AVAILABLE:
        return None
        
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        epoch = now.strftime('%Y-%m-%d %H:%M')
        obj_earth = Horizons(id=399, location="@sun", epochs=epoch)
        eph_earth = obj_earth.vectors()
        return np.array([float(eph_earth['x'][0]), 
                        float(eph_earth['y'][0]), 
                        float(eph_earth['z'][0])])
    except Exception:
        return None


def plot_trajectory_3d(trajectory: np.ndarray, dates: List[datetime.datetime], 
                      show_earth: bool = True) -> None:
    """
    Create 3D plot of Voyager 1's complete outbound trajectory.
    
    Parameters
    ----------
    trajectory : np.ndarray
        Trajectory points as (N, 3) array in AU
    dates : List[datetime.datetime]
        Corresponding dates for trajectory points
    show_earth : bool
        Whether to show current Earth position
    """
    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot main trajectory path
    ax.plot(trajectory[:, 0], trajectory[:, 1], trajectory[:, 2], 
            'k-', linewidth=2, alpha=0.7, label='Voyager 1 Trajectory')
    
    # Mark mission events
    for i, event in enumerate(MISSION_EVENTS):
        # Find closest trajectory point to event date
        time_diffs = [abs((date - event.date).total_seconds()) for date in dates]
        closest_idx = np.argmin(time_diffs)
        
        pos = trajectory[closest_idx]
        ax.scatter(pos[0], pos[1], pos[2], 
                  c=event.color, marker=event.marker, s=event.size,
                  label=event.name, edgecolors='black', linewidth=1)
        
        # Add annotation with arrows for clear connection to markers
        # Use different offsets for events near the Sun/Earth region
        distance_from_origin = np.linalg.norm(pos)
        
        if distance_from_origin < 15.0:  # Events near Sun (Launch, Jupiter, Saturn)
            # Use varying offsets for clustered points near origin
            offset_base = 8.0  # AU shift to separate text from point (increased for arrow space)
            if event.name == "Launch":
                offset = np.array([offset_base, offset_base, offset_base])
                color = "navy"
                arrow_color = "darkblue"
            elif event.name == "Jupiter Flyby":
                offset = np.array([offset_base, -offset_base, 0])
                color = "darkorange"
                arrow_color = "orange"
            elif event.name == "Saturn Flyby":
                offset = np.array([-offset_base, offset_base, 0])
                color = "darkgreen"
                arrow_color = "green"
            else:
                offset = np.array([offset_base, 0, offset_base])
                color = "black"
                arrow_color = "gray"
        else:  # Events far from Sun (Heliopause, Current)
            # Use proportional offset for distant events
            offset = pos * 0.25  # 25% offset from the point (increased for arrow space)
            color = "black"
            arrow_color = "gray"
        
        text_pos = pos + offset
        
        # Use annotate with arrow and enhanced styling for key events
        # Determine if this is a major milestone for enhanced styling
        is_key_event = event.name in ["Launch", "Jupiter Flyby", "Saturn Flyby", "Heliopause"]
        
        if is_key_event:
            fontsize = 10
            fontweight = "bold"
            if event.name == "Heliopause":
                bbox_props = dict(boxstyle="round,pad=0.4", facecolor="lightcoral", alpha=0.8, edgecolor="darkred")
            elif event.name == "Launch":
                bbox_props = dict(boxstyle="round,pad=0.4", facecolor="lightsteelblue", alpha=0.8, edgecolor="navy")
            elif event.name == "Jupiter Flyby":
                bbox_props = dict(boxstyle="round,pad=0.4", facecolor="moccasin", alpha=0.8, edgecolor="darkorange")
            elif event.name == "Saturn Flyby":
                bbox_props = dict(boxstyle="round,pad=0.4", facecolor="lightgreen", alpha=0.8, edgecolor="darkgreen")
            else:
                bbox_props = dict(boxstyle="round,pad=0.4", facecolor="lightgray", alpha=0.8, edgecolor=arrow_color)
        else:
            fontsize = 9
            fontweight = "normal"
            bbox_props = dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8, edgecolor=arrow_color)
        
        ax.text(text_pos[0], text_pos[1], text_pos[2], 
                f'{event.name}\n{event.date.strftime("%Y-%m-%d")}',
                fontsize=fontsize, ha='center', va='center', color=color, weight=fontweight,
                bbox=bbox_props)
        
        # Draw arrow from text to marker (simulate 3D annotation)
        # Project to 2D for arrow drawing
        ax.plot([pos[0], text_pos[0]], [pos[1], text_pos[1]], [pos[2], text_pos[2]], 
                color=arrow_color, linewidth=1.5, alpha=0.7, linestyle='--')
    
    # Add current position marker
    current_pos = trajectory[-1]
    ax.scatter(current_pos[0], current_pos[1], current_pos[2],
              c='purple', marker='X', s=120, label='Current Position',
              edgecolors='black', linewidth=1)
    
    # Add a faint dashed line from the Sun to Voyager's current position
    ax.plot([0, current_pos[0]], [0, current_pos[1]], [0, current_pos[2]],
            linestyle="--", color="gray", alpha=0.5, linewidth=1.5, 
            label="Sun-Voyager Line")
    
    # Add Sun at origin
    ax.scatter(0, 0, 0, c='yellow', s=200, marker='*', 
              label='Sun', edgecolors='orange', linewidth=2)
    
    # Add Sun annotation with enhanced styling
    sun_offset = np.array([-8.0, 0, 8.0])  # AU shift for Sun label
    sun_text_pos = sun_offset
    ax.text(sun_text_pos[0], sun_text_pos[1], sun_text_pos[2], 'Sun', 
            fontsize=12, ha='center', va='center', color='gold', weight='bold',
            bbox=dict(boxstyle="round,pad=0.4", facecolor='yellow', alpha=0.9, edgecolor='orange'))
    
    # Draw arrow from Sun label to Sun marker
    ax.plot([0, sun_text_pos[0]], [0, sun_text_pos[1]], [0, sun_text_pos[2]], 
            color='orange', linewidth=2, alpha=0.7, linestyle='--')
    
    # Add current Earth position if available
    if show_earth:
        earth_pos = fetch_current_earth_position()
        if earth_pos is not None:
            ax.scatter(earth_pos[0], earth_pos[1], earth_pos[2],
                      c='blue', s=80, marker='o', label='Earth (current)',
                      edgecolors='darkblue', linewidth=1)
            
            # Add Earth annotation with arrow
            earth_offset = np.array([3.0, 3.0, 1.0])  # Offset for Earth label
            earth_text_pos = earth_pos + earth_offset
            ax.text(earth_text_pos[0], earth_text_pos[1], earth_text_pos[2],
                   'Earth\n(current)', fontsize=9, ha='center', va='center', 
                   color='darkblue', weight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.8, edgecolor='darkblue'))
            
            # Draw arrow from Earth label to Earth marker
            ax.plot([earth_pos[0], earth_text_pos[0]], [earth_pos[1], earth_text_pos[1]], 
                    [earth_pos[2], earth_text_pos[2]], 
                    color='darkblue', linewidth=1.5, alpha=0.7, linestyle='--')
    
    # Set labels and title
    ax.set_xlabel('X (AU)', fontsize=12)
    ax.set_ylabel('Y (AU)', fontsize=12)
    ax.set_zlabel('Z (AU)', fontsize=12)
    ax.set_title('Voyager 1 Complete Outbound Trajectory\n(Heliocentric Coordinates)', 
                fontsize=14, fontweight='bold')
    
    # Equal aspect ratio
    max_range = np.max(np.ptp(trajectory, axis=0))
    mid_point = np.mean(trajectory, axis=0)
    ax.set_xlim(mid_point[0] - max_range/2, mid_point[0] + max_range/2)
    ax.set_ylim(mid_point[1] - max_range/2, mid_point[1] + max_range/2)
    ax.set_zlim(mid_point[2] - max_range/2, mid_point[2] + max_range/2)
    
    # Legend
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    # Print trajectory info with accuracy notes
    total_distance = np.linalg.norm(current_pos)
    print(f"\nTrajectory Summary:")
    print(f"Launch date: {dates[0].strftime('%Y-%m-%d')}")
    print(f"Current date: {dates[-1].strftime('%Y-%m-%d')}")
    print(f"Current distance from Sun: {total_distance:.1f} AU")
    print(f"Total trajectory points: {len(trajectory)}")
    
    # Calculate years since heliopause for verification
    heliopause_date = datetime.datetime(2012, 8, 25, tzinfo=datetime.timezone.utc)
    years_since_hp = (dates[-1] - heliopause_date).days / 365.25
    expected_distance = 121.0 + years_since_hp * 3.6
    print(f"Years since heliopause crossing: {years_since_hp:.1f}")
    print(f"Expected distance (121 + {years_since_hp:.1f} × 3.6): {expected_distance:.1f} AU")
    print(f"Model accuracy: {abs(total_distance - expected_distance):.1f} AU difference")
    
    # Convert to galactic coordinates if astropy available
    if _ASTROPY_AVAILABLE:
        try:
            coord = SkyCoord(x=current_pos[0] * u.au, y=current_pos[1] * u.au, 
                           z=current_pos[2] * u.au, representation_type='cartesian')
            gal = coord.galactic
            print(f"Current galactic longitude: {gal.l.deg:.2f}°")
            print(f"Current galactic latitude: {gal.b.deg:.2f}°")
        except Exception:
            pass
    
    plt.tight_layout()
    plt.show()


def main(argv: List[str] = None) -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Plot Voyager 1 complete outbound trajectory with mission events'
    )
    parser.add_argument('--step-days', type=int, default=30,
                       help='Time step between trajectory points in days (default: 30)')
    parser.add_argument('--fallback', action='store_true',
                       help='Use synthetic trajectory instead of querying HORIZONS')
    parser.add_argument('--no-earth', action='store_true',
                       help='Do not show current Earth position')
    
    args = parser.parse_args(argv)
    
    # Date range: from launch to current
    start_date = MISSION_EVENTS[0].date  # Launch date
    end_date = datetime.datetime.now(datetime.timezone.utc)
    
    # Add current position as final event
    current_event = MissionEvent("Current", end_date, "#9467bd", marker='X', size=120)
    MISSION_EVENTS.append(current_event)
    
    try:
        if args.fallback:
            print("Using synthetic trajectory (offline mode)")
            trajectory, dates = fetch_trajectory_synthetic(start_date, end_date, args.step_days)
        else:
            try:
                trajectory, dates = fetch_trajectory_real(start_date, end_date, args.step_days)
            except Exception as e:
                print(f"Real trajectory failed: {e}")
                print("Falling back to synthetic trajectory")
                trajectory, dates = fetch_trajectory_synthetic(start_date, end_date, args.step_days)
        
        # Create the 3D trajectory plot
        plot_trajectory_3d(trajectory, dates, show_earth=not args.no_earth)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
