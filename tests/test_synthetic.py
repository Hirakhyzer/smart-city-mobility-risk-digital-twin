from mobilitytwin.synthetic import SyntheticMobilityConfig, generate_synthetic_mobility_data


def test_synthetic_shapes_and_keys():
    data = generate_synthetic_mobility_data(SyntheticMobilityConfig(zones=8, segments=14, time_steps=12, seed=3))
    assert set(data) == {"zones", "roads", "facilities", "transit_stops", "traffic_traces"}
    assert len(data["zones"]) == 8
    assert len(data["roads"]) == 14
    assert data["traffic_traces"]["time_step"].nunique() == 12
    assert data["traffic_traces"]["segment_id"].nunique() == 14


def test_invalid_config_rejected():
    try:
        SyntheticMobilityConfig(zones=4, segments=4, time_steps=8)
    except ValueError:
        assert True
    else:
        raise AssertionError("invalid synthetic mobility config should fail")
