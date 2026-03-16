from stock_selection.data.fixtures import load_sample_csv


def test_load_sample_csv() -> None:
    frame = load_sample_csv("securities.csv")
    assert set(frame.columns) >= {"ticker", "sector"}
    assert len(frame) >= 2
