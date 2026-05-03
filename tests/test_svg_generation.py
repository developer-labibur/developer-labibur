"""Tests for SVG generation (SVGBuilder + templates)."""

import pytest

from generator.config import validate_config
from generator.svg_builder import SVGBuilder


class TestSVGBuilder:
    def test_init(self, svg_builder):
        assert svg_builder.config["username"] == "galaxy-dev"

    def test_render_galaxy_header_valid_svg(self, svg_builder):
        svg = svg_builder.render_galaxy_header()
        assert svg.strip().startswith("<svg")
        assert svg.strip().endswith("</svg>")

    def test_galaxy_header_contains_name(self, svg_builder):
        svg = svg_builder.render_galaxy_header()
        assert "Nyx Orion" in svg

    def test_galaxy_header_contains_animations(self, svg_builder):
        svg = svg_builder.render_galaxy_header()
        assert "animate" in svg

    def test_render_stats_card_valid_svg(self, svg_builder):
        svg = svg_builder.render_stats_card()
        assert svg.strip().startswith("<svg")
        assert svg.strip().endswith("</svg>")

    def test_stats_card_contains_formatted_values(self, svg_builder):
        svg = svg_builder.render_stats_card()
        assert "1.8k" in svg  # commits=1847
        assert "342" in svg   # stars
        assert "156" in svg   # prs

    def test_render_tech_stack_valid_svg(self, svg_builder):
        svg = svg_builder.render_tech_stack()
        assert svg.strip().startswith("<svg")
        assert svg.strip().endswith("</svg>")

    def test_tech_stack_contains_language_names(self, svg_builder):
        svg = svg_builder.render_tech_stack()
        assert "Python" in svg
        assert "TypeScript" in svg

    def test_render_projects_constellation_valid_svg(self, svg_builder):
        svg = svg_builder.render_projects_constellation()
        assert svg.strip().startswith("<svg")
        assert svg.strip().endswith("</svg>")

    def test_projects_constellation_contains_repo_names(self, svg_builder):
        svg = svg_builder.render_projects_constellation()
        assert "nebula-ui" in svg
        assert "stargate-api" in svg


class TestEdgeCases:
    def test_empty_projects(self, cfg, sample_stats, sample_languages):
        cfg["projects"] = []
        config = validate_config(cfg)
        builder = SVGBuilder(config, sample_stats, sample_languages)
        svg = builder.render_projects_constellation()
        assert svg.strip().startswith("<svg")
        assert svg.strip().endswith("</svg>")

    def test_empty_languages(self, cfg, sample_stats):
        config = validate_config(cfg)
        builder = SVGBuilder(config, sample_stats, {})
        svg = builder.render_tech_stack()
        assert svg.strip().startswith("<svg")
        assert svg.strip().endswith("</svg>")

    def test_zero_stats(self, cfg, sample_languages):
        config = validate_config(cfg)
        zero_stats = {"commits": 0, "stars": 0, "prs": 0, "issues": 0, "repos": 0}
        builder = SVGBuilder(config, zero_stats, sample_languages)
        svg = builder.render_stats_card()
        assert svg.strip().startswith("<svg")
        assert svg.strip().endswith("</svg>")
