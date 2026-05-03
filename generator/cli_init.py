"""Interactive setup wizard for Galaxy Profile configuration."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

import yaml
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator

from generator.config import ConfigError, validate_config
from generator.tech_catalog import get_all_techs
from generator.utils import DEFAULT_THEME, HEX_COLOR_RE
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yml")

ARM_COLORS = [
    {"name": "synapse_cyan  (#00d4ff)", "value": "synapse_cyan"},
    {"name": "dendrite_violet (#a78bfa)", "value": "dendrite_violet"},
    {"name": "axon_amber  (#ffb020)", "value": "axon_amber"},
]

ALL_METRICS = ["commits", "stars", "prs", "issues", "repos"]


def run_init():
    """Orchestrate the full interactive setup wizard."""
    print("\n🌌 Galaxy Profile — Interactive Setup\n")

    existing = _detect_existing_config()
    defaults = {}

    if existing is not None:
        action, defaults = _handle_existing_config(existing)
        if action == "cancel":
            print("Setup cancelled.")
            return

    essential = _prompt_essential(defaults)
    arms = _prompt_galaxy_arms(defaults)

    configure_advanced = inquirer.confirm(
        message="Configure advanced options (bio, social, projects, theme)?",
        default=False,
    ).execute()

    advanced = _prompt_advanced(defaults) if configure_advanced else {}

    config = _build_config(essential, arms, advanced)
    path = _save_config(config)

    # Validate
    try:
        with open(path, "r") as f:
            raw = yaml.safe_load(f)
        validate_config(raw)
        print(f"\n✅ Config saved and validated: {path}")
    except ConfigError as e:
        print(f"\n⚠️  Config saved to {path} but validation found issues: {e}")

    _offer_generation()


def _detect_existing_config() -> dict | None:
    """Check if config.yml already exists. Return the parsed dict or None."""
    path = os.path.normpath(_CONFIG_PATH)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def _handle_existing_config(existing: dict) -> tuple[str, dict]:
    """Ask user what to do with existing config. Return (action, defaults)."""
    action = inquirer.select(
        message="config.yml already exists. What would you like to do?",
        choices=[
            {"name": "Overwrite — start from scratch", "value": "overwrite"},
            {"name": "Edit — use current values as defaults", "value": "edit"},
            {"name": "Cancel", "value": "cancel"},
        ],
    ).execute()

    if action == "cancel":
        return ("cancel", {})
    if action == "edit":
        return ("edit", existing if isinstance(existing, dict) else {})
    return ("overwrite", {})


def _prompt_essential(defaults: dict) -> dict:
    """Collect essential fields: username, name, tagline."""
    profile_defaults = defaults.get("profile", {})

    username = inquirer.text(
        message="GitHub username:",
        default=defaults.get("username", ""),
        validate=EmptyInputValidator("Username cannot be empty."),
    ).execute()

    name = inquirer.text(
        message="Display name:",
        default=profile_defaults.get("name", ""),
        validate=EmptyInputValidator("Name cannot be empty."),
    ).execute()

    tagline = inquirer.text(
        message="Tagline (short description):",
        default=profile_defaults.get("tagline", ""),
    ).execute()

    return {"username": username, "name": name, "tagline": tagline}


def _prompt_galaxy_arms(defaults: dict) -> list:
    """Collect 3 galaxy arms, each with name, color, and technologies."""
    all_techs = get_all_techs()
    default_arms = defaults.get("galaxy_arms", [])
    arms = []

    for i in range(3):
        print(f"\n--- Galaxy Arm {i + 1}/3 ---")
        arm_default = default_arms[i] if i < len(default_arms) else {}

        arm_name = inquirer.text(
            message=f"Arm {i + 1} name (e.g. Frontend, Backend, DevOps):",
            default=arm_default.get("name", ""),
            validate=EmptyInputValidator("Arm name cannot be empty."),
        ).execute()

        default_color = arm_default.get("color", ARM_COLORS[i]["value"])
        arm_color = inquirer.select(
            message=f"Arm {i + 1} color:",
            choices=ARM_COLORS,
            default=default_color,
        ).execute()

        default_items = arm_default.get("items", [])
        arm_techs = inquirer.fuzzy(
            message=f"Arm {i + 1} technologies (type to filter, space to select):",
            choices=all_techs,
            default=default_items,
            multiselect=True,
            validate=lambda result: len(result) > 0,
            invalid_message="Select at least one technology.",
        ).execute()

        arms.append({
            "name": arm_name,
            "color": arm_color,
            "items": arm_techs,
        })

    return arms


def _prompt_advanced(defaults: dict) -> dict:
    """Collect optional advanced fields."""
    result = {}
    profile_defaults = defaults.get("profile", {})
    social_defaults = defaults.get("social", {})

    # Bio, company, location, philosophy
    profile_fields = [
        ("bio", "Bio (multi-line, use \\n for newlines):"),
        ("company", "Company:"),
        ("location", "Location:"),
        ("philosophy", "Philosophy quote:"),
    ]
    for key, prompt in profile_fields:
        default = profile_defaults.get(key, "")
        if key == "bio":
            default = default.strip()
        value = inquirer.text(message=prompt, default=default).execute()
        if value:
            result[key] = value.replace("\\n", "\n") if key == "bio" else value

    # Social links
    print("\n--- Social Links (leave blank to skip) ---")
    social_fields = [("email", "Email:"), ("linkedin", "LinkedIn username:"), ("website", "Website URL:")]
    social = {}
    for key, prompt in social_fields:
        value = inquirer.text(
            message=prompt,
            default=social_defaults.get(key, ""),
        ).execute()
        if value:
            social[key] = value
    if social:
        result["social"] = social

    # Projects
    projects = _prompt_projects(defaults)
    if projects:
        result["projects"] = projects

    # Theme
    customize_theme = inquirer.confirm(
        message="Customize theme colors?",
        default=False,
    ).execute()
    if customize_theme:
        result["theme"] = _prompt_theme(defaults.get("theme", {}))

    # Stats
    metrics = inquirer.checkbox(
        message="Which stats metrics to display?",
        choices=[
            {"name": "Commits", "value": "commits", "enabled": True},
            {"name": "Stars", "value": "stars", "enabled": True},
            {"name": "PRs", "value": "prs", "enabled": True},
            {"name": "Issues", "value": "issues", "enabled": True},
            {"name": "Repos", "value": "repos", "enabled": True},
        ],
    ).execute()
    if metrics:
        result["stats"] = {"metrics": metrics}

    # Languages
    print("\n--- Language Display Settings ---")
    exclude_input = inquirer.text(
        message="Languages to exclude (comma-separated, e.g. HTML,CSS,Shell):",
        default=",".join(defaults.get("languages", {}).get("exclude", [])),
    ).execute()
    if exclude_input.strip():
        exclude = [lang.strip() for lang in exclude_input.split(",") if lang.strip()]
    else:
        exclude = []

    max_display = inquirer.text(
        message="Max languages to display:",
        default=str(defaults.get("languages", {}).get("max_display", 8)),
    ).execute()
    result["languages"] = {
        "exclude": exclude,
        "max_display": int(max_display) if max_display.isdigit() else 8,
    }

    return result


def _prompt_projects(defaults: dict) -> list:
    """Collect featured projects in a loop."""
    default_projects = defaults.get("projects", [])
    projects = []

    add_project = inquirer.confirm(
        message="Add a featured project?",
        default=len(default_projects) > 0,
    ).execute()

    idx = 0
    while add_project:
        proj_default = default_projects[idx] if idx < len(default_projects) else {}

        repo = inquirer.text(
            message="Repository (owner/repo):",
            default=proj_default.get("repo", ""),
            validate=EmptyInputValidator("Repository cannot be empty."),
        ).execute()

        arm = inquirer.select(
            message="Associated galaxy arm (index):",
            choices=[
                {"name": "Arm 0", "value": 0},
                {"name": "Arm 1", "value": 1},
                {"name": "Arm 2", "value": 2},
            ],
            default=proj_default.get("arm", 0),
        ).execute()

        description = inquirer.text(
            message="Short description:",
            default=proj_default.get("description", ""),
        ).execute()

        projects.append({"repo": repo, "arm": arm, "description": description})
        idx += 1

        add_project = inquirer.confirm(
            message="Add another project?",
            default=idx < len(default_projects),
        ).execute()

    return projects


def _prompt_theme(theme_defaults: dict) -> dict:
    """Collect custom theme hex colors."""
    theme = {}
    for key, default_value in DEFAULT_THEME.items():
        current = theme_defaults.get(key, default_value)
        value = inquirer.text(
            message=f"Theme {key} (hex):",
            default=current,
            validate=lambda v: bool(HEX_COLOR_RE.match(v)),
            invalid_message="Must be a valid hex color (e.g. #00d4ff).",
        ).execute()
        theme[key] = value
    return theme


def _build_config(essential: dict, arms: list, advanced: dict) -> dict:
    """Assemble the final config dictionary."""
    config = {
        "username": essential["username"],
        "profile": {
            "name": essential["name"],
            "tagline": essential.get("tagline", ""),
        },
        "galaxy_arms": arms,
    }

    # Merge advanced profile fields
    for key in ("bio", "company", "location", "philosophy"):
        if key in advanced:
            config["profile"][key] = advanced[key]

    for key in ("social", "projects", "theme", "stats", "languages"):
        if key in advanced:
            config[key] = advanced[key]

    return config


def _save_config(config: dict) -> str:
    """Serialize config to YAML and write to config.yml. Return the path."""
    path = os.path.normpath(_CONFIG_PATH)

    header = (
        "# Galaxy Profile README Configuration\n"
        "# Generated by: python -m generator.main init\n"
        "#\n"
        "# Regenerate SVGs with:\n"
        "#   python -m generator.main\n"
        "#\n"
        "# Demo mode (no API calls):\n"
        "#   python -m generator.main --demo\n\n"
    )

    with open(path, "w") as f:
        f.write(header)
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    return path


def _offer_generation():
    """Ask if user wants to generate SVGs now."""
    generate_now = inquirer.confirm(
        message="Generate SVGs now?",
        default=True,
    ).execute()

    if generate_now:
        print("\nGenerating SVGs...")
        from generator.main import generate

        generate(argparse.Namespace(demo=False))
