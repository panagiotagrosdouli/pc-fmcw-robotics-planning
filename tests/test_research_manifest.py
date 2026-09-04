from pc_fmcw_robustness.manifest import ResearchMethodManifest


def test_research_manifest_round_trip_dict():
    manifest = ResearchMethodManifest(
        protocol_version="research-framework-v1",
        planner="P2-risk",
        information_level="causal_prediction",
        risk_mode="cvar",
        horizon_s=2.0,
        mc_samples=32,
        connectivity_weight=1.0,
    )
    assert manifest.to_dict()["risk_mode"] == "cvar"
