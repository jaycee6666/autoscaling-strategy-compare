import os
import tempfile

import pytest

from scripts.load_generator import LoadGenerator


def test_load_generator_initialization() -> None:
    """Test LoadGenerator initializes with correct parameters."""
    gen = LoadGenerator(
        target_url="http://example.com",
        request_rate=10,
        duration_seconds=5,
        pattern="constant",
    )
    assert gen.target_url == "http://example.com"
    assert gen.request_rate == 10
    assert gen.duration_seconds == 5
    assert gen.pattern == "constant"


def test_load_generator_constant_pattern() -> None:
    """Test constant rate pattern generates correct number of requests."""
    gen = LoadGenerator(
        target_url="http://httpbin.org/get",
        request_rate=5,
        duration_seconds=2,
        pattern="constant",
    )
    stats = gen.generate_load()

    # Should generate approximately 10 requests (5 req/s * 2s)
    assert 8 <= stats["total_requests"] <= 12
    assert stats["total_requests"] > 0
    assert "response_times" in stats
    assert "errors" in stats


def test_load_generator_invalid_pattern() -> None:
    """Test invalid pattern raises error."""
    with pytest.raises(ValueError):
        LoadGenerator(
            target_url="http://example.com",
            request_rate=10,
            duration_seconds=5,
            pattern="invalid_pattern",
        )


def test_load_generator_stats_export() -> None:
    """Test statistics can be exported to CSV."""
    gen = LoadGenerator(
        target_url="http://httpbin.org/get",
        request_rate=2,
        duration_seconds=1,
        pattern="constant",
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = os.path.join(tmpdir, "stats.csv")
        stats = gen.generate_load()
        gen.export_stats_to_csv(output_file, stats)

        assert os.path.exists(output_file)
        with open(output_file, "r", encoding="utf-8") as f:
            content = f.read()
            assert "Total Requests" in content
