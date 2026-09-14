import inspect

import numpy as np
import pytest

from iscai.evaluation.actionability import (
    changed_action_outcome,
    decision_regret,
    select_actionable_candidate,
)


def test_selection_api_has_no_realized_outcome_argument():
    params = inspect.signature(select_actionable_candidate).parameters
    forbidden = {"future_qos", "realized_qos", "measured_qos", "truth", "outcome"}
    assert forbidden.isdisjoint(params)


def test_unsupported_candidate_cannot_trigger_motion_change():
    choice = select_actionable_candidate(
        lower_bounds=[20.0, 10.0],
        upper_bounds=[22.0, 12.0],
        supported=[True, False],
        mobility_penalties=[0.0, 0.0],
    )
    assert choice.index == 0
    assert choice.changed is False


def test_conservative_gain_must_clear_mobility_penalty():
    choice = select_actionable_candidate(
        lower_bounds=[20.0, 15.0, 14.0],
        upper_bounds=[22.0, 18.0, 17.0],
        supported=[True, True, True],
        mobility_penalties=[0.0, 3.0, 1.0],
    )
    # Candidate 1: gain 2 - penalty 3 = -1. Candidate 2: gain 3 - 1 = 2.
    assert choice.index == 2
    assert choice.changed is True
    assert np.isclose(choice.net_conservative_gain, 2.0)


def test_frozen_minimum_net_gain_can_force_reference_action():
    choice = select_actionable_candidate(
        lower_bounds=[20.0, 15.0],
        upper_bounds=[22.0, 18.0],
        supported=[True, True],
        mobility_penalties=[0.0, 1.5],
        min_net_gain=1.0,
    )
    # Conservative net gain is only 0.5, so the gate must not change motion.
    assert choice.index == 0
    assert choice.changed is False


def test_regret_is_post_selection_and_nonnegative_for_observed_set():
    realized = np.array([25.0, 20.0, 23.0])
    chosen_index = 2
    regret = decision_regret(realized[chosen_index], realized)
    assert np.isclose(regret, 3.0)


def test_changed_action_outcome_uses_lower_is_better_sign_convention():
    assert changed_action_outcome(25.0, 20.0) == "beneficial"
    assert changed_action_outcome(25.0, 30.0) == "harmful"
    assert changed_action_outcome(25.0, 25.0) == "neutral"


def test_invalid_candidate_arrays_are_rejected():
    with pytest.raises(ValueError):
        select_actionable_candidate([1.0], [1.0, 2.0], [True], [0.0])
