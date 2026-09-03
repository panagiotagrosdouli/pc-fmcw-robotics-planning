from iscai.connectivity.pc_fmcw_bridge import PCFMCWPlanningLinkPredictor


def test_pc_fmcw_provenance_keeps_unverified_parameters_conservative():
    provenance = PCFMCWPlanningLinkPredictor().provenance()

    assert provenance["system_context"] == "PanagiotaGr/ISCAI_pc_fmcw"
    assert provenance["reference_parameters_explicit"] is True
    assert provenance["upstream_parameter_provenance_verified"] is False
    assert provenance["optical_geometry_model"] == "simulation_assumption"
    assert provenance["measured_optical_link"] is False
    assert provenance["real_world_validation"] is False


def test_provenance_does_not_reintroduce_unverified_traceability_claim():
    provenance = PCFMCWPlanningLinkPredictor().provenance()

    forbidden_true_flags = {
        "waveform_parameters_traced",
        "upstream_parameter_provenance_verified",
        "measured_optical_link",
        "real_world_validation",
    }
    for key in forbidden_true_flags:
        assert provenance.get(key, False) is False
