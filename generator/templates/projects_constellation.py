"""SVG template: Featured Systems / Projects Constellation (850x220)."""

from generator.utils import wrap_text, deterministic_random, esc, resolve_arm_colors

WIDTH, HEIGHT = 850, 220


def _build_defs(n, card_width, gap, card_colors, theme):
    """Build all defs (filters, gradients, clip paths, CSS)."""
    defs_parts = []

    # Glow filters per card
    for i in range(n):
        color = card_colors[i]
        defs_parts.append(f'''    <filter id="proj-glow-{i}" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="4" in="SourceGraphic" result="blur"/>
      <feFlood flood-color="{color}" flood-opacity="0.6" result="color"/>
      <feComposite in="color" in2="blur" operator="in" result="glow"/>
      <feMerge>
        <feMergeNode in="glow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>''')

    # Card nebula filter
    defs_parts.append('''    <filter id="card-nebula" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="15"/>
    </filter>''')

    # Card background gradients
    for i in range(n):
        color = card_colors[i]
        defs_parts.append(f'''    <linearGradient id="card-bg-{i}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{theme['star_dust']}" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="{theme['nebula']}" stop-opacity="0.9"/>
    </linearGradient>''')

    # Connection line gradient (between card colors)
    if n >= 2:
        defs_parts.append(f'''    <linearGradient id="conn-grad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="{card_colors[0]}" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="{card_colors[-1]}" stop-opacity="0.4"/>
    </linearGradient>''')

    # Clip paths per card
    for i in range(n):
        card_x = gap + i * (card_width + gap)
        defs_parts.append(f'''    <clipPath id="card-clip-{i}">
      <rect x="{card_x}" y="55" width="{card_width}" height="140" rx="8" ry="8"/>
    </clipPath>''')

    # CSS keyframes
    defs_parts.append('''    <style>
      @keyframes twinkle {
        0%, 100% { opacity: 0.1; }
        50% { opacity: 0.6; }
      }
      @keyframes orbit {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }
      @keyframes card-appear {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
      }
      @keyframes scan-sweep {
        0% { transform: translateY(0); }
        100% { transform: translateY(160px); }
      }
    </style>''')

    return "\n".join(defs_parts)


def _build_starfield(n, width, height, card_colors, theme):
    """Build the 25-star star field (bg + mid-ground stars)."""
    stars = []
    layers = [
        {
            "prefix": "proj-star", "count": 15, "margin": 10,
            "r": (0.3, 0.9), "o": (0.05, 0.25), "d": (5.0, 8.0),
            "o_mult": 3, "o_cap": 0.6,
        },
        {
            "prefix": "proj-mstar", "count": 10, "margin": 15,
            "r": (0.5, 1.2), "o": (0.10, 0.40), "d": (3.0, 6.0),
            "o_mult": 2.5, "o_cap": 0.8,
        },
    ]
    for layer in layers:
        count = layer["count"]
        m = layer["margin"]
        pfx = layer["prefix"]
        sx = deterministic_random(f"{pfx}-x", count, m, width - m)
        sy = deterministic_random(f"{pfx}-y", count, m, height - m)
        sr = deterministic_random(f"{pfx}-r", count, *layer["r"])
        so = deterministic_random(f"{pfx}-o", count, *layer["o"])
        sd = deterministic_random(f"{pfx}-d", count, *layer["d"])
        for i in range(count):
            fill = card_colors[i % n] if i % 4 == 0 else theme["text_dim"]
            stars.append(
                f'  <circle cx="{sx[i]:.1f}" cy="{sy[i]:.1f}" r="{sr[i]:.1f}" '
                f'fill="{fill}" opacity="{so[i]:.2f}">'
                f'<animate attributeName="opacity" values="{so[i]:.2f};{min(so[i] * layer["o_mult"], layer["o_cap"]):.2f};{so[i]:.2f}" '
                f'dur="{sd[i]:.1f}s" repeatCount="indefinite"/>'
                f'</circle>'
            )
    return "\n".join(stars)


def _build_grid_overlay(width, height, theme):
    """Build the horizontal and vertical dashed grid lines."""
    grid_lines = []
    # Horizontal dashed lines every ~40px
    for y in range(40, height, 40):
        grid_lines.append(
            f'  <line x1="12" y1="{y}" x2="{width - 12}" y2="{y}" '
            f'stroke="{theme["text_faint"]}" stroke-width="0.5" '
            f'stroke-dasharray="4,8" opacity="0.12"/>'
        )
    # Vertical dashed lines every ~80px
    for x in range(80, width, 80):
        grid_lines.append(
            f'  <line x1="{x}" y1="12" x2="{x}" y2="{height - 12}" '
            f'stroke="{theme["text_faint"]}" stroke-width="0.5" '
            f'stroke-dasharray="4,8" opacity="0.08"/>'
        )
    return "\n".join(grid_lines)


def _build_connections(n, card_width, gap):
    """Build connection lines between cards."""
    conn_lines = []
    if n >= 2:
        for i in range(n - 1):
            x1 = gap + i * (card_width + gap) + card_width / 2
            x2 = gap + (i + 1) * (card_width + gap) + card_width / 2
            conn_lines.append(
                f'  <line x1="{x1:.1f}" y1="85" x2="{x2:.1f}" y2="85" '
                f'stroke="url(#conn-grad)" stroke-width="1" '
                f'stroke-dasharray="6,4" opacity="0.5"/>'
            )
    return "\n".join(conn_lines)


def _build_title_area(n, width, height, theme):
    """Build the corner brackets, title, status dot, and status text."""
    title_parts = []
    # Corner brackets (4 L-shaped pairs)
    bk = theme["text_faint"]
    bl = 16  # bracket arm length
    title_parts.append(
        f'  <g opacity="0.4">'
        # Top-left
        f'\n    <polyline points="5,{bl + 5} 5,5 {bl + 5},5" fill="none" stroke="{bk}" stroke-width="1.5"/>'
        # Top-right
        f'\n    <polyline points="{width - bl - 5},5 {width - 5},5 {width - 5},{bl + 5}" fill="none" stroke="{bk}" stroke-width="1.5"/>'
        # Bottom-left
        f'\n    <polyline points="5,{height - bl - 5} 5,{height - 5} {bl + 5},{height - 5}" fill="none" stroke="{bk}" stroke-width="1.5"/>'
        # Bottom-right
        f'\n    <polyline points="{width - bl - 5},{height - 5} {width - 5},{height - 5} {width - 5},{height - bl - 5}" fill="none" stroke="{bk}" stroke-width="1.5"/>'
        f'\n  </g>'
    )
    # Section title
    title_parts.append(
        f'  <text x="30" y="38" fill="{theme["text_faint"]}" font-size="11" '
        f'font-family="monospace" letter-spacing="3">FEATURED SYSTEMS</text>'
    )
    # Pulsing status dot
    cyan = theme.get("synapse_cyan", "#00d4ff")
    title_parts.append(
        f'  <circle cx="218" cy="34" r="3" fill="{cyan}" opacity="0.8">'
        f'<animate attributeName="opacity" values="0.4;1;0.4" dur="2s" repeatCount="indefinite"/>'
        f'</circle>'
    )
    # Right-aligned status text
    title_parts.append(
        f'  <text x="{width - 30}" y="38" fill="{theme["text_faint"]}" font-size="10" '
        f'font-family="monospace" text-anchor="end" opacity="0.5">SYS {n}/{n} ONLINE</text>'
    )
    return "\n".join(title_parts)


def _build_project_card(i, proj, arm, color, card_width, card_x, theme):
    """Build a single project card."""
    card_cx = card_x + card_width / 2
    repo_name = proj["repo"].split("/")[-1] if "/" in proj["repo"] else proj["repo"]
    desc = proj.get("description", "")
    # Wrap description to fit card width (approx chars)
    max_chars = int(card_width / 7.5)
    desc_lines = wrap_text(desc, max_chars)

    delay = f"{i * 0.3}s"

    card_parts = []
    card_parts.append(f'  <g opacity="0" style="animation: card-appear 0.6s ease {delay} forwards">')

    # Card container
    card_parts.append(
        f'    <rect x="{card_x}" y="55" width="{card_width}" height="140" rx="8" ry="8" '
        f'fill="url(#card-bg-{i})" stroke="{theme["star_dust"]}" stroke-width="1"/>'
    )

    # Nebula wisps (clipped inside card)
    card_parts.append(f'    <g clip-path="url(#card-clip-{i})">')
    card_parts.append(
        f'      <circle cx="{card_x + card_width * 0.3}" cy="90" r="50" '
        f'fill="{color}" opacity="0.025" filter="url(#card-nebula)"/>'
    )
    card_parts.append(
        f'      <circle cx="{card_x + card_width * 0.7}" cy="150" r="40" '
        f'fill="{color}" opacity="0.03" filter="url(#card-nebula)"/>'
    )
    # Scan line inside card
    card_parts.append(
        f'      <rect x="{card_x}" y="55" width="{card_width}" height="2" '
        f'fill="{color}" opacity="0.1">'
        f'<animateTransform attributeName="transform" type="translate" '
        f'from="0 0" to="0 140" dur="6s" repeatCount="indefinite"/>'
        f'</rect>'
    )
    card_parts.append('    </g>')

    # Star indicator — orbital ring + glow + core + center
    # Orbital ring (rotating dashed circle)
    card_parts.append(
        f'    <circle cx="{card_cx}" cy="85" r="14" fill="none" '
        f'stroke="{color}" stroke-width="0.8" stroke-dasharray="4,3" opacity="0.5">'
        f'<animateTransform attributeName="transform" type="rotate" '
        f'from="0 {card_cx} 85" to="360 {card_cx} 85" dur="12s" repeatCount="indefinite"/>'
        f'</circle>'
    )
    # Glow halo
    card_parts.append(
        f'    <circle cx="{card_cx}" cy="85" r="8" fill="{color}" '
        f'opacity="0.15" filter="url(#proj-glow-{i})"/>'
    )
    # Pulsing core
    card_parts.append(
        f'    <circle cx="{card_cx}" cy="85" r="5" fill="{color}" opacity="0.7">'
        f'<animate attributeName="opacity" values="0.5;0.9;0.5" dur="3s" '
        f'begin="{delay}" repeatCount="indefinite"/>'
        f'<animate attributeName="r" values="4.5;5.5;4.5" dur="3s" '
        f'begin="{delay}" repeatCount="indefinite"/>'
        f'</circle>'
    )
    # White center dot
    card_parts.append(
        f'    <circle cx="{card_cx}" cy="85" r="2" fill="#ffffff" opacity="0.9"/>'
    )

    # Project name (centered)
    card_parts.append(
        f'    <text x="{card_cx}" y="111" fill="{theme["text_bright"]}" '
        f'font-size="14" font-weight="bold" font-family="sans-serif" '
        f'text-anchor="middle">{esc(repo_name)}</text>'
    )

    # Description lines (centered)
    for j, line in enumerate(desc_lines[:2]):
        y_pos = 129 + j * 15
        card_parts.append(
            f'    <text x="{card_cx}" y="{y_pos}" fill="{theme["text_dim"]}" '
            f'font-size="11" font-family="sans-serif" '
            f'text-anchor="middle">{esc(line)}</text>'
        )

    # Category tag (pill shape)
    tag_text = arm["name"]
    tag_width = len(tag_text) * 7 + 16
    tag_x = card_cx - tag_width / 2
    card_parts.append(
        f'    <rect x="{tag_x}" y="163" width="{tag_width}" height="18" rx="9" ry="9" '
        f'fill="{color}" opacity="0.12"/>'
    )
    card_parts.append(
        f'    <text x="{card_cx}" y="175" fill="{color}" '
        f'font-size="9" font-family="monospace" text-anchor="middle" '
        f'opacity="0.85">{esc(tag_text)}</text>'
    )

    card_parts.append('  </g>')
    return "\n".join(card_parts)


def _build_scan_line(width, theme):
    """Build the global scan line."""
    cyan = theme.get("synapse_cyan", "#00d4ff")
    return (
        f'  <rect x="12" y="50" width="{width - 24}" height="1.5" '
        f'fill="{cyan}" opacity="0.08">'
        f'<animateTransform attributeName="transform" type="translate" '
        f'from="0 0" to="0 160" dur="6s" repeatCount="indefinite"/>'
        f'</rect>'
    )


def render(projects: list, galaxy_arms: list, theme: dict) -> str:
    """Render the projects constellation SVG.

    Args:
        projects: list of project dicts with repo, arm, description
        galaxy_arms: list of arm configs for color mapping
        theme: color palette dict
    """
    all_arm_colors = resolve_arm_colors(galaxy_arms, theme)

    n = min(len(projects), 3)

    if n == 0:
        # No projects — render an empty card
        return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" ry="12"
        fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="1"/>
  <text x="{WIDTH / 2}" y="{HEIGHT / 2}" fill="{theme['text_faint']}" font-size="12"
        font-family="monospace" text-anchor="middle" dominant-baseline="middle">No featured projects configured</text>
</svg>'''

    # Adaptive card sizing
    if n == 2:
        card_width = 340
    else:
        card_width = 240
    total_cards_width = card_width * n
    gap = (WIDTH - total_cards_width) / (n + 1)

    # Resolve arm indices and colors per card
    card_arms = []
    card_colors = []
    for i in range(n):
        proj = projects[i]
        arm_idx = proj.get("arm", 0)
        arm_idx = arm_idx if arm_idx < len(galaxy_arms) else 0
        card_arms.append(arm_idx)
        card_colors.append(all_arm_colors[arm_idx])

    # ── Layer 0: Defs ──
    defs_str = _build_defs(n, card_width, gap, card_colors, theme)

    # ── Layer 1: Background rect ──
    bg = (
        f'  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" '
        f'rx="12" ry="12" fill="{theme["nebula"]}" '
        f'stroke="{theme["star_dust"]}" stroke-width="1"/>'
    )

    # ── Layer 2: Star field (25 particles) ──
    stars_str = _build_starfield(n, WIDTH, HEIGHT, card_colors, theme)

    # ── Layer 3: Faint grid overlay ──
    grid_str = _build_grid_overlay(WIDTH, HEIGHT, theme)

    # ── Layer 4: Connection lines between cards ──
    conn_str = _build_connections(n, card_width, gap)

    # ── Layer 5: Title area ──
    title_str = _build_title_area(n, WIDTH, HEIGHT, theme)

    # ── Layer 6: Project cards ──
    cards = []
    for i in range(n):
        proj = projects[i]
        arm = galaxy_arms[card_arms[i]]
        color = card_colors[i]
        card_x = gap + i * (card_width + gap)

        cards.append(_build_project_card(i, proj, arm, color, card_width, card_x, theme))

    cards_str = "\n".join(cards)

    # ── Layer 7: Global scan line ──
    scan_line = _build_scan_line(WIDTH, theme)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>
{defs_str}
  </defs>

  <!-- Background -->
{bg}

  <!-- Star field -->
{stars_str}

  <!-- Grid overlay -->
{grid_str}

  <!-- Connection lines -->
{conn_str}

  <!-- Title area -->
{title_str}

  <!-- Project cards -->
{cards_str}

  <!-- Global scan line -->
{scan_line}
</svg>'''
