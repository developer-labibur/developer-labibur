"""SVG template: Mission Telemetry stats card (850x180)."""

from generator.utils import METRIC_ICONS, METRIC_LABELS, METRIC_COLORS, format_number

WIDTH, HEIGHT = 850, 180


def render(stats: dict, metrics: list, theme: dict) -> str:
    """Render the stats card SVG.

    Args:
        stats: dict with keys like commits, stars, prs, issues, repos
        metrics: list of metric keys to display
        theme: color palette dict
    """
    cell_width = WIDTH / len(metrics)

    # Build metric cells
    cells = []
    dividers = []
    for i, key in enumerate(metrics):
        cx = cell_width * i + cell_width / 2
        icon_color = theme.get(METRIC_COLORS.get(key, "synapse_cyan"), "#00d4ff")
        value = format_number(stats.get(key, 0))
        label = METRIC_LABELS.get(key, key.title())
        icon_path = METRIC_ICONS.get(key, "")
        delay = f"{i * 0.3}s"

        cells.append(f'''    <g class="metric-cell" transform="translate({cx}, 95)">
      <g transform="translate(-8, -30) scale(1)">
        <svg viewBox="0 0 16 16" width="16" height="16" fill="{icon_color}" class="metric-icon" style="animation-delay: {delay}">
          {icon_path}
        </svg>
      </g>
      <text x="0" y="2" text-anchor="middle" fill="{icon_color}" font-size="28" font-weight="bold" font-family="sans-serif" opacity="0.35" filter="url(#num-glow)">{value}</text>
      <text x="0" y="2" text-anchor="middle" fill="{theme['text_bright']}" font-size="28" font-weight="bold" font-family="sans-serif">{value}</text>
      <text x="0" y="20" text-anchor="middle" fill="{theme['text_faint']}" font-size="11" font-family="monospace" letter-spacing="1">{label}</text>
    </g>''')

        # Vertical divider between cells (not after last)
        if i < len(metrics) - 1:
            dx = cell_width * (i + 1)
            dividers.append(
                f'    <line x1="{dx}" y1="55" x2="{dx}" y2="155" '
                f'stroke="{theme["star_dust"]}" stroke-width="1" opacity="0.5"/>'
            )

    cells_str = "\n".join(cells)
    dividers_str = "\n".join(dividers)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>
    <style>
      .metric-icon {{
        animation: count-glow 4s ease-in-out infinite;
      }}
      @keyframes count-glow {{
        0%, 100% {{ fill-opacity: 0.7; }}
        50% {{ fill-opacity: 1; }}
      }}
    </style>
    <filter id="num-glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="3"/>
    </filter>
  </defs>

  <!-- Card background -->
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="12" ry="12"
        fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="1"/>

  <!-- Section title -->
  <text x="30" y="38" fill="{theme['text_faint']}" font-size="11" font-family="monospace" letter-spacing="3">MISSION TELEMETRY</text>

  <!-- Dividers -->
{dividers_str}

  <!-- Metric cells -->
{cells_str}
</svg>'''
