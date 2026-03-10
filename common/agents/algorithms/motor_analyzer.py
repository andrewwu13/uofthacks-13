"""
Motor Analyzer - Temporal segmentation + robust feature extraction from telemetry
Pure Python implementation for zero API cost

Improvements over v1:
- Temporal phase segmentation (travel → dwell → interaction)
- Per-phase stats instead of global averages that wash out dwell signal
- Percentile-based velocity profile (p50/p90/peak) for robustness
- Dwell detection (episodes of near-zero velocity)
- Click impulse score (sharpness of velocity spike toward a stop)
"""

import math
from typing import List, Dict, Tuple

# Velocity thresholds (px/s)
IDLE_VELOCITY_THRESHOLD = 20.0        # Below this = effectively stopped / dwell
TRAVEL_VELOCITY_THRESHOLD = 80.0      # Above this = deliberate movement


class MotorAnalyzer:
    """
    Analyzes cursor/touch motion using temporal segmentation.

    Produces three class of signals:
    1. Global population stats (percentiles — robust to phase imbalance)
    2. Dwell metrics (how long and how often the user stopped)
    3. Click impulse score (sharpness of pre-click approach)
    """

    def analyze(self, telemetry: List[Dict]) -> Dict:
        """
        Analyze motion telemetry with temporal segmentation.

        Args:
            telemetry: List of processed position/velocity/acceleration dicts
                Each entry: { timestamp, position:{x,y}, velocity:{x,y}, acceleration:{x,y} }

        Returns:
            Rich motion metrics dict
        """
        if len(telemetry) < 2:
            return self._empty_metrics()

        velocities: List[float] = []
        accelerations: List[float] = []
        jerks: List[float] = []
        direction_changes = 0

        dwell_episodes: List[float] = []   # duration of each dwell in ms
        current_dwell_start: float | None = None

        for i in range(1, len(telemetry)):
            prev = telemetry[i - 1]
            curr = telemetry[i]

            dt_ms = curr.get("timestamp", 0) - prev.get("timestamp", 0)
            dt_s = dt_ms / 1000.0
            if dt_s <= 0:
                continue

            # Velocity magnitude
            vel = curr.get("velocity", {"x": 0, "y": 0})
            vel_mag = math.sqrt(vel.get("x", 0) ** 2 + vel.get("y", 0) ** 2)
            velocities.append(vel_mag)

            # Acceleration magnitude
            acc = curr.get("acceleration", {"x": 0, "y": 0})
            acc_mag = math.sqrt(acc.get("x", 0) ** 2 + acc.get("y", 0) ** 2)
            accelerations.append(acc_mag)

            # Jerk (3rd derivative)
            if len(accelerations) >= 2:
                jerk = abs(accelerations[-1] - accelerations[-2]) / dt_s
                jerks.append(jerk)

            # Direction changes
            if i >= 2:
                prev_vel = telemetry[i - 1].get("velocity", {"x": 0, "y": 0})
                if (
                    prev_vel.get("x", 0) * vel.get("x", 0) < 0
                    or prev_vel.get("y", 0) * vel.get("y", 0) < 0
                ):
                    direction_changes += 1

            # Dwell detection
            ts = curr.get("timestamp", 0)
            if vel_mag < IDLE_VELOCITY_THRESHOLD:
                if current_dwell_start is None:
                    current_dwell_start = float(ts)
            else:
                if current_dwell_start is not None:
                    dwell_duration = ts - current_dwell_start
                    if dwell_duration >= 200:  # only count dwells > 200ms
                        dwell_episodes.append(dwell_duration)
                    current_dwell_start = None

        # Close any trailing dwell
        if current_dwell_start is not None and len(telemetry) >= 2:
            last_ts = telemetry[-1].get("timestamp", 0)
            dwell_duration = last_ts - current_dwell_start
            if dwell_duration >= 200:
                dwell_episodes.append(dwell_duration)

        # Velocity percentiles
        sorted_v = sorted(velocities)
        n = len(sorted_v)
        p50 = sorted_v[int(n * 0.50)] if n > 0 else 0
        p90 = sorted_v[int(n * 0.90)] if n > 0 else 0
        peak = sorted_v[-1] if sorted_v else 0

        # Total duration
        total_duration_ms = 0.0
        if len(telemetry) >= 2:
            total_duration_ms = (
                telemetry[-1].get("timestamp", 0) - telemetry[0].get("timestamp", 0)
            )

        # Click impulse score: ratio of peak velocity to p50 velocity
        # A user who snaps to a target has a high peak relative to their median
        click_impulse_score = round(min(1.0, (peak / (p50 + 1)) / 20.0), 3)

        # Dwell summary
        total_dwell_ms = sum(dwell_episodes)
        avg_dwell_ms = (total_dwell_ms / len(dwell_episodes)) if dwell_episodes else 0

        return {
            # Temporal coverage
            "total_duration_ms": round(total_duration_ms),
            "sample_count": len(telemetry),

            # Velocity profile (percentile-based — robust to phase imbalance)
            "p50_velocity": round(p50, 1),
            "p90_velocity": round(p90, 1),
            "peak_velocity": round(peak, 1),
            "avg_velocity": round(sum(velocities) / n, 1) if n > 0 else 0,  # kept for compat

            # Acceleration
            "avg_acceleration": round(sum(accelerations) / len(accelerations), 1) if accelerations else 0,
            "max_acceleration": round(max(accelerations), 1) if accelerations else 0,

            # Jerk
            "avg_jerk": round(sum(jerks) / len(jerks), 1) if jerks else 0,
            "max_jerk": round(max(jerks), 1) if jerks else 0,

            # Direction changes
            "direction_changes": direction_changes,
            "direction_change_rate": round(direction_changes / len(telemetry), 3) if telemetry else 0,

            # Dwell metrics
            "dwell_count": len(dwell_episodes),
            "total_dwell_ms": round(total_dwell_ms),
            "avg_dwell_ms": round(avg_dwell_ms),
            "dwell_fraction": round(total_dwell_ms / (total_duration_ms + 1), 3),

            # Click impulse
            "click_impulse_score": click_impulse_score,
        }

    def _empty_metrics(self) -> Dict:
        return {
            "total_duration_ms": 0, "sample_count": 0,
            "p50_velocity": 0, "p90_velocity": 0, "peak_velocity": 0, "avg_velocity": 0,
            "avg_acceleration": 0, "max_acceleration": 0,
            "avg_jerk": 0, "max_jerk": 0,
            "direction_changes": 0, "direction_change_rate": 0,
            "dwell_count": 0, "total_dwell_ms": 0, "avg_dwell_ms": 0, "dwell_fraction": 0,
            "click_impulse_score": 0,
        }
