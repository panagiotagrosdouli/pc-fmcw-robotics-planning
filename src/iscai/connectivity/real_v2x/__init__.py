"""Real-measurement V2X QoS modeling for support-aware planning."""
from .datasets import load_cicv5g_file, discover_cicv5g_files, add_run_metadata
from .predictors import PersistencePredictor, SpatialKNNPredictor, TreeQoSPredictor
from .uncertainty import ResidualConformalCalibrator
from .support import SpatialSupportModel
from .planner import score_candidates, PlannerMode

__all__ = [
    "load_cicv5g_file", "discover_cicv5g_files", "add_run_metadata",
    "PersistencePredictor", "SpatialKNNPredictor", "TreeQoSPredictor",
    "ResidualConformalCalibrator", "SpatialSupportModel", "score_candidates", "PlannerMode",
]
