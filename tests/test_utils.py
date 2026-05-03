"""Tests for generator.utils."""

import pytest

from generator.utils import (
    DEFAULT_THEME,
    calculate_language_percentages,
    deterministic_random,
    esc,
    format_number,
    get_language_color,
    resolve_theme,
    spiral_points,
    wrap_text,
)


class TestFormatNumber:
    def test_zero(self):
        assert format_number(0) == "0"

    def test_small_number(self):
        assert format_number(42) == "42"

    def test_999(self):
        assert format_number(999) == "999"

    def test_1000(self):
        assert format_number(1000) == "1.0k"

    def test_1234(self):
        assert format_number(1234) == "1.2k"

    def test_million(self):
        assert format_number(1000000) == "1.0M"

    def test_1500000(self):
        assert format_number(1500000) == "1.5M"


class TestCalculateLanguagePercentages:
    def test_basic_calculation(self):
        langs = {"Python": 700, "Go": 300}
        result = calculate_language_percentages(langs, [], 8)
        assert len(result) == 2
        assert result[0]["name"] == "Python"
        assert result[0]["percentage"] == 70.0
        assert result[1]["name"] == "Go"
        assert result[1]["percentage"] == 30.0

    def test_exclude(self):
        langs = {"Python": 700, "Go": 300, "HTML": 100}
        result = calculate_language_percentages(langs, ["HTML"], 8)
        assert all(r["name"] != "HTML" for r in result)

    def test_max_display(self):
        langs = {f"Lang{i}": 100 * (10 - i) for i in range(10)}
        result = calculate_language_percentages(langs, [], 3)
        assert len(result) == 3

    def test_empty_languages(self):
        result = calculate_language_percentages({}, [], 8)
        assert result == []

    def test_all_excluded(self):
        langs = {"Python": 700}
        result = calculate_language_percentages(langs, ["Python"], 8)
        assert result == []

    def test_color_assigned(self):
        langs = {"Python": 100}
        result = calculate_language_percentages(langs, [], 8)
        assert result[0]["color"] == "#3572A5"


class TestWrapText:
    def test_short_text(self):
        result = wrap_text("hello", 20)
        assert result == ["hello"]

    def test_word_wrap(self):
        result = wrap_text("hello world foo bar", 12)
        assert len(result) >= 2
        assert all(len(line) <= 15 for line in result)  # reasonable wrapping

    def test_single_long_word(self):
        result = wrap_text("superlongword", 5)
        assert result == ["superlongword"]

    def test_empty(self):
        result = wrap_text("", 20)
        assert result == []


class TestDeterministicRandom:
    def test_deterministic(self):
        a = deterministic_random("seed", 5, 0, 100)
        b = deterministic_random("seed", 5, 0, 100)
        assert a == b

    def test_different_seeds(self):
        a = deterministic_random("seed_a", 5, 0, 100)
        b = deterministic_random("seed_b", 5, 0, 100)
        assert a != b

    def test_range(self):
        values = deterministic_random("test", 20, 10, 50)
        assert all(10 <= v <= 50 for v in values)

    def test_count(self):
        values = deterministic_random("test", 7, 0, 1)
        assert len(values) == 7


class TestEsc:
    def test_xml_special_chars(self):
        assert "&amp;" in esc("&")
        assert "&lt;" in esc("<")
        assert "&gt;" in esc(">")

    def test_quotes(self):
        assert "&quot;" in esc('"')
        assert "&apos;" in esc("'")

    def test_normal_text(self):
        assert esc("hello") == "hello"


class TestSpiralPoints:
    def test_count(self):
        pts = spiral_points(0, 0, 0, 10, 100)
        assert len(pts) == 10

    def test_format(self):
        pts = spiral_points(0, 0, 0, 5, 50)
        for pt in pts:
            assert len(pt) == 2
            assert isinstance(pt[0], float)
            assert isinstance(pt[1], float)

    def test_first_point_at_center(self):
        pts = spiral_points(100, 200, 0, 10, 50)
        assert pts[0][0] == pytest.approx(100, abs=1)
        assert pts[0][1] == pytest.approx(200, abs=1)


class TestResolveTheme:
    def test_empty_override(self):
        result = resolve_theme({})
        assert result == DEFAULT_THEME

    def test_partial_override(self):
        result = resolve_theme({"void": "#ffffff"})
        assert result["void"] == "#ffffff"
        assert result["synapse_cyan"] == "#00d4ff"

    def test_none_override(self):
        result = resolve_theme(None)
        assert result == DEFAULT_THEME


class TestGetLanguageColor:
    def test_known_language(self):
        assert get_language_color("Python") == "#3572A5"
        assert get_language_color("TypeScript") == "#3178c6"

    def test_unknown_language(self):
        assert get_language_color("UnknownLang") == "#8b949e"
