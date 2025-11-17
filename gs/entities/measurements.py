from dataclasses import dataclass, field
from typing import List, Dict, Optional
import numpy as np
from scipy import signal


@dataclass
class SingleHit:
    """Holds raw time data for a single hammer strike."""

    id: int
    force: np.ndarray
    response: np.ndarray
    fs: int
    is_valid: bool = True  # If user rejects this hit, set to False

    @property
    def duration(self, fs: int) -> float:
        return len(self.force) / fs

    def check_overload(self, limit: float = 0.95) -> bool:
        """Returns True if signal clipped."""
        return np.max(np.abs(self.force)) > limit


@dataclass
class PointMeasurement:
    """Represents one physical point (e.g. 'Bridge G-String side')."""

    name: str
    coords: tuple = (0, 0, 0)  # (x, y, z) for Modal Analysis later
    hits: List[SingleHit] = field(default_factory=list)

    # Caching the result so we don't re-compute FFTs every time we plot
    _cached_frf: Optional[np.ndarray] = None
    _cached_coherence: Optional[np.ndarray] = None
    _freq_vector: Optional[np.ndarray] = None

    def add_hit(self, force, response):
        new_id = len(self.hits) + 1
        hit = SingleHit(new_id, force, response)
        self.hits.append(hit)
        self.invalidate_cache()

    def invalidate_cache(self):
        self._cached_frf = None

    def compute_frf(self, fs: int):
        """
        The Heavy Lifting: Calculates H1 Estimator from VALID hits only.
        """
        if self._cached_frf is not None:
            return self._freq_vector, self._cached_frf, self._cached_coherence

        valid_hits = [h for h in self.hits if h.is_valid]
        if not valid_hits:
            return None, None, None

        # Accumulators for Spectral Density
        nperseg = len(valid_hits[0].force)
        Gxy_sum = np.zeros(nperseg // 2 + 1, dtype=complex)
        Gxx_sum = np.zeros(nperseg // 2 + 1, dtype=complex)
        Gyy_sum = np.zeros(nperseg // 2 + 1, dtype=complex)

        for hit in valid_hits:
            # 1. Windowing (Force=Boxcar, Response=Exponential)
            # (Simplification: Assuming windowing happens inside compute_spectra)
            f, Pxx = signal.welch(hit.force, fs=fs, nperseg=nperseg, window="boxcar")
            f, Pyy = signal.welch(
                hit.response, fs=fs, nperseg=nperseg, window="exponential"
            )
            f, Pxy = signal.csd(hit.force, hit.response, fs=fs, nperseg=nperseg)

            # Note: standard scipy.welch averages segments.
            # Since we have transient hits, we usually do FFT directly.
            # This is just pseudocode logic for the structure.

            Gxx_sum += Pxx
            Gyy_sum += Pyy
            Gxy_sum += Pxy

        # H1 Estimator
        self._freq_vector = f
        self._cached_frf = Gxy_sum / Gxx_sum

        # Coherence
        self._cached_coherence = (np.abs(Gxy_sum) ** 2) / (Gxx_sum * Gyy_sum)

        return self._freq_vector, self._cached_frf, self._cached_coherence


@dataclass
class MeasurementSession:
    """Holds the entire project state."""

    violin_name: str
    maker: str
    date: str
    fs: int
    # Key = Point Name (e.g., "Point_1"), Value = PointMeasurement Object
    points: Dict[str, PointMeasurement] = field(default_factory=dict)

    def create_point(self, name, coords=(0, 0, 0)):
        if name not in self.points:
            self.points[name] = PointMeasurement(name, coords)
        return self.points[name]

    def add_data_to_point(self, point_name, force, response):
        if point_name not in self.points:
            self.points[point_name] = PointMeasurement(point_name)
        self.points[point_name].add_hit(force, response)

    def calculate_point_result(self, point_name):
        point = self.points[point_name]
        return point.compute_frf(self.fs)

    def get_all_frfs(self):
        """Returns a dict of all calculated FRFs for plotting"""
        results = {}
        for name, point in self.points.items():
            f, h, c = point.compute_frf()
            results[name] = h
        return results
