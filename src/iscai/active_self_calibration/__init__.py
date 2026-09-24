"""Decision-triggered active self-calibration research extension."""

from .belief import GridBelief, normalized_parameter_error
from .benchmark import CalibrationBenchmarkSettings, run_study
from .link_model import (
    LatentLinkParameters,
    NOMINAL_LATENT_PARAMETERS,
    ParameterizedPCFMCWLinkModel,
)
from .planners import (
    CALIBRATION_PLANNERS,
    ActiveSelfCalibrationPlanner,
    CalibrationPlanningResult,
    decision_diagnostics,
)
from .scenarios import CalibrationScenario, make_identifiability_scenarios

__all__ = [
    "GridBelief",
    "normalized_parameter_error",
    "CalibrationBenchmarkSettings",
    "run_study",
    "LatentLinkParameters",
    "NOMINAL_LATENT_PARAMETERS",
    "ParameterizedPCFMCWLinkModel",
    "CALIBRATION_PLANNERS",
    "ActiveSelfCalibrationPlanner",
    "CalibrationPlanningResult",
    "decision_diagnostics",
    "CalibrationScenario",
    "make_identifiability_scenarios",
]
