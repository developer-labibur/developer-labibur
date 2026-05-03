"""SVG template: Galaxy Header — the signature spiral galaxy banner (850x280)."""

import math
from generator.utils import spiral_points, deterministic_random, esc, resolve_arm_colors

# ── Module-level constants ──
WIDTH, HEIGHT = 850, 280
CENTER_X, CENTER_Y = 425, 155
MAX_RADIUS = 220
SPIRAL_TURNS = 0.85
NUM_POINTS = 30
X_SCALE, Y_SCALE = 1.5, 0.38
START_ANGLES = [25, 150, 265]


def _build_glow_filters(galaxy_arms, arm_colors):
    """Build the star glow filters, one per arm."""
    glow_filters = []
    for i, arm in enumerate(galaxy_arms):
        color = arm_colors[i]
        glow_filters.append(
            f'    <filter id="star-glow-{i}" x="-100%" y="-100%" width="300%" height="300%">\n'
            f'      <feGaussianBlur stdDeviation="3" result="blur"/>\n'
            f'      <feFlood flood-color="{color}" flood-opacity="0.5" result="color"/>\n'
            f'      <feComposite in="color" in2="blur" operator="in" result="glow"/>\n'
            f'      <feMerge>\n'
            f'        <feMergeNode in="glow"/>\n'
            f'        <feMergeNode in="SourceGraphic"/>\n'
            f'      </feMerge>\n'
            f'    </filter>'
        )
    return "\n".join(glow_filters)


def _build_starfield(username, width, height, theme):
    """Build all 3 star depth layers (bg, mid, fg)."""
    star_layers = [
        {
            "count": 40, "label": "bg",
            "r_min": 0.3, "r_max": 0.8,
            "o_min": 0.08, "o_max": 0.3,
            "dur_min": 5.0, "dur_max": 9.0,
        },
        {
            "count": 20, "label": "mid",
            "r_min": 0.6, "r_max": 1.2,
            "o_min": 0.15, "o_max": 0.5,
            "dur_min": 3.5, "dur_max": 7.0,
        },
        {
            "count": 10, "label": "fg",
            "r_min": 1.0, "r_max": 1.8,
            "o_min": 0.4, "o_max": 0.7,
            "dur_min": 2.0, "dur_max": 4.5,
        },
    ]

    stars = []
    for layer in star_layers:
        n = layer["count"]
        lbl = layer["label"]
        sx = deterministic_random(f"{username}_sx_{lbl}", n, 10, width - 10)
        sy = deterministic_random(f"{username}_sy_{lbl}", n, 10, height - 10)
        sr = deterministic_random(f"{username}_sr_{lbl}", n, layer["r_min"], layer["r_max"])
        so = deterministic_random(f"{username}_so_{lbl}", n, layer["o_min"], layer["o_max"])
        sd = deterministic_random(f"{username}_sd_{lbl}", n, layer["dur_min"], layer["dur_max"])

        accent_colors = {
            0: theme.get("synapse_cyan", "#00d4ff"),
            4: theme.get("dendrite_violet", "#a78bfa"),
            8: theme.get("axon_amber", "#ffb020"),
        }
        for i in range(n):
            fill = accent_colors.get(i % 12, "#ffffff")

            delay = f"{sd[i] * 0.3:.1f}s"
            stars.append(
                f'    <circle cx="{sx[i]:.1f}" cy="{sy[i]:.1f}" r="{sr[i]:.2f}" '
                f'fill="{fill}" opacity="{so[i]:.2f}" class="star-{lbl}" '
                f'style="animation-delay: {delay}"/>'
            )
    return "\n".join(stars)


def _build_nebulae(cx, cy, theme):
    """Return the outer_nebula and inner_nebula SVG strings."""
    outer_nebula = (
        f'    <circle cx="{cx - 180}" cy="{cy - 30}" r="120" fill="{theme["dendrite_violet"]}" opacity="0.015" filter="url(#nebula-outer)"/>\n'
        f'    <circle cx="{cx + 200}" cy="{cy + 20}" r="100" fill="{theme["axon_amber"]}" opacity="0.012" filter="url(#nebula-outer)"/>\n'
        f'    <circle cx="{cx}" cy="{cy + 40}" r="140" fill="{theme["synapse_cyan"]}" opacity="0.01" filter="url(#nebula-outer)"/>'
    )

    inner_nebula = (
        f'    <circle cx="{cx}" cy="{cy}" r="70" fill="{theme["synapse_cyan"]}" opacity="0.04" filter="url(#nebula-inner)"/>\n'
        f'    <circle cx="{cx - 60}" cy="{cy - 20}" r="50" fill="{theme["dendrite_violet"]}" opacity="0.035" filter="url(#nebula-inner)"/>\n'
        f'    <circle cx="{cx + 70}" cy="{cy + 15}" r="45" fill="{theme["axon_amber"]}" opacity="0.03" filter="url(#nebula-inner)"/>'
    )

    return outer_nebula, inner_nebula


def _build_shooting_stars():
    """Build the shooting star lines."""
    shoot_stars = []
    shoot_data = [
        (120, 30, 200, 80, 6),
        (650, 20, 180, 70, 8),
        (400, 250, 160, 60, 7),
    ]
    for idx, (sx_pos, sy_pos, tx, ty, dur) in enumerate(shoot_data):
        shoot_stars.append(
            f'    <line x1="{sx_pos}" y1="{sy_pos}" x2="{sx_pos + 20}" y2="{sy_pos + 5}" '
            f'stroke="url(#shoot-grad)" stroke-width="1.2" stroke-linecap="round" '
            f'class="shooting-star" style="animation-delay: {idx * 2.5}s; '
            f'--shoot-tx: {tx}px; --shoot-ty: {ty}px; animation-duration: {dur}s"/>'
        )
    return "\n".join(shoot_stars)


def _points_to_path(points):
    """Build a quadratic Bezier SVG path string from a list of (x, y) points."""
    d = f"M {points[0][0]:.1f} {points[0][1]:.1f}"
    for j in range(1, len(points)):
        px, py = points[j - 1]
        x, y = points[j]
        cpx = (px + x) / 2
        cpy = (py + y) / 2
        d += f" Q {px:.1f} {py:.1f} {cpx:.1f} {cpy:.1f}"
    d += f" L {points[-1][0]:.1f} {points[-1][1]:.1f}"
    return d


def _build_spiral_arms(galaxy_arms, arm_colors, all_arm_points):
    """Build arm paths (segmented fade) and arm particles."""
    arm_paths = []
    arm_particles = []
    segment_count = 4
    opacity_steps = [0.50, 0.40, 0.30, 0.20]
    width_steps = [2.0, 1.7, 1.4, 1.1]

    for arm_idx, arm in enumerate(galaxy_arms):
        color = arm_colors[arm_idx]
        points = all_arm_points[arm_idx]

        if len(points) < 2:
            continue

        # Build full path string for animateMotion
        full_path_d = _points_to_path(points)

        # Split into segments (Step 4)
        pts_per_seg = len(points) // segment_count
        for seg in range(segment_count):
            start_i = seg * pts_per_seg
            end_i = min(start_i + pts_per_seg + 1, len(points))
            seg_pts = points[start_i:end_i]

            if len(seg_pts) < 2:
                continue

            seg_d = _points_to_path(seg_pts)

            op = opacity_steps[seg]
            sw = width_steps[seg]
            arm_paths.append(
                f'    <path d="{seg_d}" fill="none" stroke="{color}" '
                f'stroke-width="{sw:.1f}" opacity="{op:.2f}" stroke-linecap="round">'
                f'\n      <animate attributeName="opacity" values="{op - 0.1:.2f};{op + 0.1:.2f};{op - 0.1:.2f}" '
                f'dur="8s" begin="{arm_idx}s" repeatCount="indefinite"/>'
                f'\n    </path>'
            )

        # Arm particles — 2 per arm (Step 7)
        for p_idx in range(2):
            delay = arm_idx * 4 + p_idx * 6
            arm_particles.append(
                f'    <circle r="1.5" fill="{color}" opacity="0.6">\n'
                f'      <animateMotion dur="12s" begin="{delay}s" repeatCount="indefinite" '
                f'path="{full_path_d}"/>\n'
                f'      <animate attributeName="opacity" values="0;0.7;0.3;0" dur="12s" '
                f'begin="{delay}s" repeatCount="indefinite"/>\n'
                f'    </circle>'
            )

    return "\n".join(arm_paths), "\n".join(arm_particles)


def _build_tech_labels(galaxy_arms, arm_colors, all_arm_points, cx, cy):
    """Build tech dots, leader lines, and labels with radial placement."""
    arm_dots = []
    outer_start = 8  # Only use outer 65% of spiral (indices 8-27 of 30)

    for arm_idx, arm in enumerate(galaxy_arms):
        color = arm_colors[arm_idx]
        points = all_arm_points[arm_idx]
        items = arm.get("items", [])

        if not items:
            continue

        # Distribute items across outer portion of spiral
        available = len(points) - outer_start - 2  # leave last 2 points free
        spacing = max(1, available // max(len(items), 1))

        for i, item in enumerate(items):
            pt_idx = min(outer_start + i * spacing, len(points) - 1)
            px, py = points[pt_idx]

            # Radial direction from core (Step 3)
            dx = px - cx
            dy = py - cy
            dist = math.sqrt(dx * dx + dy * dy) or 1
            nx = dx / dist
            ny = dy / dist

            # Label position: 18px outward from dot
            label_x = px + nx * 18
            label_y = py + ny * 18

            # Dynamic text-anchor based on position
            if dx > 20:
                anchor = "start"
            elif dx < -20:
                anchor = "end"
            else:
                anchor = "middle"

            # Dot with opacity pulse animation (Step 7)
            arm_dots.append(
                f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="2.5" fill="{color}" opacity="0.85">\n'
                f'      <animate attributeName="opacity" values="0.85;1;0.85" dur="5s" begin="{i * 0.7}s" repeatCount="indefinite"/>\n'
                f'    </circle>'
            )

            # Leader line — dashed, subtle (Step 3)
            arm_dots.append(
                f'    <line x1="{px:.1f}" y1="{py:.1f}" x2="{label_x:.1f}" y2="{label_y:.1f}" '
                f'stroke="{color}" stroke-width="0.5" opacity="0.25" stroke-dasharray="2 2"/>'
            )

            # Label glow (blurred duplicate behind — Step 9)
            arm_dots.append(
                f'    <text x="{label_x:.1f}" y="{label_y + 3:.1f}" text-anchor="{anchor}" '
                f'fill="{color}" font-size="9" font-family="monospace" opacity="0.2" '
                f'filter="url(#label-glow)">{esc(item)}</text>'
            )

            # Main label (Step 9)
            arm_dots.append(
                f'    <text x="{label_x:.1f}" y="{label_y + 3:.1f}" text-anchor="{anchor}" '
                f'fill="{color}" font-size="9" font-family="monospace" opacity="0.85">{esc(item)}</text>'
            )

    return "\n".join(arm_dots)


def _build_project_stars(projects, galaxy_arms, arm_colors, all_arm_points):
    """Build project star circles."""
    project_stars = []
    for proj in projects[:3]:
        arm_idx = proj.get("arm", 0) % len(galaxy_arms)
        arm = galaxy_arms[arm_idx]
        color = arm_colors[arm_idx]
        points = all_arm_points[arm_idx]

        pt_idx = min(len(points) - 3, 24)
        px, py = points[pt_idx]
        delay = f"{arm_idx * 0.8}s"

        project_stars.append(
            f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{color}" filter="url(#star-glow-{arm_idx})">\n'
            f'      <animate attributeName="opacity" values="0.6;1;0.6" dur="4s" begin="{delay}" repeatCount="indefinite"/>\n'
            f'    </circle>'
        )

    return "\n".join(project_stars)


def _build_orbital_rings(cx, cy, theme):
    """Build the orbital ring ellipses."""
    return (
        f'    <ellipse cx="{cx}" cy="{cy}" rx="55" ry="18" fill="none" '
        f'stroke="{theme["synapse_cyan"]}" stroke-width="0.6" opacity="0.15" '
        f'stroke-dasharray="4 6">\n'
        f'      <animateTransform attributeName="transform" type="rotate" '
        f'from="0 {cx} {cy}" to="360 {cx} {cy}" dur="20s" repeatCount="indefinite"/>\n'
        f'    </ellipse>\n'
        f'    <ellipse cx="{cx}" cy="{cy}" rx="75" ry="24" fill="none" '
        f'stroke="{theme["dendrite_violet"]}" stroke-width="0.5" opacity="0.1" '
        f'stroke-dasharray="3 8">\n'
        f'      <animateTransform attributeName="transform" type="rotate" '
        f'from="360 {cx} {cy}" to="0 {cx} {cy}" dur="30s" repeatCount="indefinite"/>\n'
        f'    </ellipse>'
    )


def _build_galaxy_core(cx, cy, theme, initial):
    """Build the core layers (haze, glow, rings, solid core, initial)."""
    return (
        f'    <!-- Outer haze -->\n'
        f'    <circle cx="{cx}" cy="{cy}" r="40" fill="url(#core-haze-gradient)" opacity="0.4"/>\n'
        f'    <!-- Inner glow -->\n'
        f'    <circle cx="{cx}" cy="{cy}" r="24" fill="url(#core-inner-gradient)" opacity="0.6"/>\n'
        f'    <!-- Outer ring -->\n'
        f'    <ellipse cx="{cx}" cy="{cy}" rx="20" ry="18" fill="none" '
        f'stroke="{theme["synapse_cyan"]}" stroke-width="1.2" opacity="0.55" '
        f'stroke-dasharray="5 3" class="core-ring"/>\n'
        f'    <!-- Inner ring -->\n'
        f'    <circle cx="{cx}" cy="{cy}" r="14" fill="none" '
        f'stroke="{theme["dendrite_violet"]}" stroke-width="0.8" opacity="0.4" class="core-ring-inner"/>\n'
        f'    <!-- Solid core -->\n'
        f'    <circle cx="{cx}" cy="{cy}" r="11" fill="{theme["nebula"]}" '
        f'stroke="{theme["star_dust"]}" stroke-width="0.5"/>\n'
        f'    <!-- Bright center dot -->\n'
        f'    <circle cx="{cx}" cy="{cy}" r="3" fill="{theme["synapse_cyan"]}" '
        f'filter="url(#core-bright-glow)" opacity="0.9"/>\n'
        f'    <!-- Initial -->\n'
        f'    <text x="{cx}" y="{cy + 5}" text-anchor="middle" fill="{theme["synapse_cyan"]}" '
        f'font-size="14" font-weight="bold" font-family="monospace">{initial}</text>'
    )


def render(
    config: dict,
    theme: dict,
    galaxy_arms: list,
    projects: list,
) -> str:
    """Render the galaxy header SVG.

    Args:
        config: full profile config dict
        theme: color palette dict
        galaxy_arms: list of arm configs
        projects: list of project dicts
    """
    username = config.get("username", "user")
    profile = config.get("profile", {})
    name = profile.get("name", username)
    tagline = profile.get("tagline", "")
    philosophy = profile.get("philosophy", "")
    initial = name[0].upper() if name else "?"

    arm_colors = resolve_arm_colors(galaxy_arms, theme)

    # ── Spiral geometry (Step 2) ──
    # Generate arm points for all arms
    all_arm_points = [
        spiral_points(
            CENTER_X, CENTER_Y, START_ANGLES[arm_idx % len(START_ANGLES)],
            NUM_POINTS, MAX_RADIUS, SPIRAL_TURNS, X_SCALE, Y_SCALE
        )
        for arm_idx in range(len(galaxy_arms))
    ]

    # ── Defs: filters, gradients, animations ──

    # Glow filters for project stars
    glow_filters_str = _build_glow_filters(galaxy_arms, arm_colors)

    # Label glow filter (Step 9)
    label_glow_filter = (
        '    <filter id="label-glow" x="-20%" y="-20%" width="140%" height="140%">\n'
        '      <feGaussianBlur stdDeviation="2" result="blur"/>\n'
        '    </filter>'
    )

    # Core glow filter
    core_glow_filter = (
        '    <filter id="core-bright-glow" x="-100%" y="-100%" width="300%" height="300%">\n'
        '      <feGaussianBlur stdDeviation="4"/>\n'
        '    </filter>'
    )

    # ── Build all layers via helper functions ──
    stars_str = _build_starfield(username, WIDTH, HEIGHT, theme)
    outer_nebula, inner_nebula = _build_nebulae(CENTER_X, CENTER_Y, theme)
    shoot_stars_str = _build_shooting_stars()
    arm_paths_str, arm_particles_str = _build_spiral_arms(galaxy_arms, arm_colors, all_arm_points)
    arm_dots_str = _build_tech_labels(galaxy_arms, arm_colors, all_arm_points, CENTER_X, CENTER_Y)
    project_stars_str = _build_project_stars(projects, galaxy_arms, arm_colors, all_arm_points)
    orbital_rings = _build_orbital_rings(CENTER_X, CENTER_Y, theme)
    core = _build_galaxy_core(CENTER_X, CENTER_Y, theme, initial)

    # ── Assemble SVG ──
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>
    <style>
      .star-bg {{
        animation: twinkle-slow 7s ease-in-out infinite;
      }}
      .star-mid {{
        animation: twinkle-mid 5s ease-in-out infinite;
      }}
      .star-fg {{
        animation: twinkle-fast 3s ease-in-out infinite;
      }}
      @keyframes twinkle-slow {{
        0%, 100% {{ opacity: 0.08; }}
        50% {{ opacity: 0.3; }}
      }}
      @keyframes twinkle-mid {{
        0%, 100% {{ opacity: 0.15; }}
        50% {{ opacity: 0.5; }}
      }}
      @keyframes twinkle-fast {{
        0%, 100% {{ opacity: 0.4; }}
        50% {{ opacity: 0.8; }}
      }}
      .core-ring {{
        animation: pulse-core 3s ease-in-out infinite;
      }}
      .core-ring-inner {{
        animation: pulse-core 3s ease-in-out infinite 1.5s;
      }}
      @keyframes pulse-core {{
        0%, 100% {{ stroke-opacity: 0.3; transform: scale(1); transform-origin: {CENTER_X}px {CENTER_Y}px; }}
        50% {{ stroke-opacity: 0.8; transform: scale(1.06); transform-origin: {CENTER_X}px {CENTER_Y}px; }}
      }}
      .shooting-star {{
        opacity: 0;
        animation: shoot linear infinite;
      }}
      @keyframes shoot {{
        0% {{ opacity: 0; transform: translate(0, 0); }}
        5% {{ opacity: 0.9; }}
        15% {{ opacity: 0.6; transform: translate(var(--shoot-tx), var(--shoot-ty)); }}
        20% {{ opacity: 0; transform: translate(var(--shoot-tx), var(--shoot-ty)); }}
        100% {{ opacity: 0; }}
      }}
    </style>

    <filter id="nebula-outer">
      <feGaussianBlur stdDeviation="60"/>
    </filter>
    <filter id="nebula-inner">
      <feGaussianBlur stdDeviation="30"/>
    </filter>

{label_glow_filter}
{core_glow_filter}

    <radialGradient id="core-haze-gradient" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{theme['synapse_cyan']}" stop-opacity="0.5"/>
      <stop offset="50%" stop-color="{theme['dendrite_violet']}" stop-opacity="0.2"/>
      <stop offset="100%" stop-color="{theme['synapse_cyan']}" stop-opacity="0"/>
    </radialGradient>

    <radialGradient id="core-inner-gradient" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.6"/>
      <stop offset="40%" stop-color="{theme['synapse_cyan']}" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="{theme['synapse_cyan']}" stop-opacity="0"/>
    </radialGradient>

    <linearGradient id="shoot-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>

{glow_filters_str}
  </defs>

  <!-- 1. Background -->
  <rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" rx="12" ry="12" fill="{theme['void']}"/>

  <!-- 2. Outer nebula -->
{outer_nebula}

  <!-- 3. Star field (3 layers) -->
{stars_str}

  <!-- 4. Inner nebula -->
{inner_nebula}

  <!-- 5. Shooting stars -->
{shoot_stars_str}

  <!-- 6. Spiral arm paths (segmented fade) -->
{arm_paths_str}

  <!-- 7. Arm particles -->
{arm_particles_str}

  <!-- 8. Tech dots + leader lines + labels -->
{arm_dots_str}

  <!-- 9. Project stars -->
{project_stars_str}

  <!-- 10. Orbital rings -->
{orbital_rings}

  <!-- 11. Galaxy core -->
{core}

  <!-- 12. Profile text -->
  <text x="{CENTER_X}" y="26" text-anchor="middle" fill="{theme['text_bright']}" font-size="20" font-weight="bold" font-family="sans-serif">{esc(name)}</text>
  <text x="{CENTER_X}" y="44" text-anchor="middle" fill="{theme['text_dim']}" font-size="12" font-family="sans-serif">{esc(tagline)}</text>
  <text x="{CENTER_X}" y="{HEIGHT - 12}" text-anchor="middle" fill="{theme['text_faint']}" font-size="11" font-family="monospace" font-style="italic">{esc(philosophy)}</text>
</svg>'''
