from typing import List, Tuple, Dict, Optional, Set

class TSPSolution:
    """Solution TSP"""

    def __init__(
        self,
        tour: Optional[List[int]] = None,
        cost: float = float('inf'),
        iterations: int = 0,
        time_seconds: float = 0.0,
        lower_bound: Optional[float] = None,
        cuts_added: int = 0,
    ):
        self.tour = tour
        self.cost = cost
        self.iterations = iterations
        self.time_seconds = time_seconds
        self.lower_bound = lower_bound
        self.cuts_added = cuts_added

    def gap(self) -> Optional[float]:
        if self.lower_bound is None or self.lower_bound == 0:
            return None
        if self.cost == float('inf'):
            return None
        return ((self.cost / self.lower_bound) - 1) * 100

    def __repr__(self):
        return (
            f"Solution(tour={self.tour}, cost={self.cost}, iterations={self.iterations}, "
            f"time_seconds={self.time_seconds}, lower_bound={self.lower_bound}, "
            f"cuts_added={self.cuts_added})"
        )