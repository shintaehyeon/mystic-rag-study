"""Generate a privacy-safe GitHub activity dashboard from aggregate JSON data."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta
from html import escape
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = ROOT / "daily_usage.json"
DEFAULT_OUTPUT_PATH = ROOT / "dashboard.svg"

REQUIRED_SNAPSHOT_FIELDS = {
    "captured_at",
    "lifetime_tokens",
    "peak_task_tokens",
    "longest_task_minutes",
    "current_streak_days",
    "longest_streak_days",
    "total_tasks",
}
DAILY_INTEGER_FIELDS = ("tokens", "tasks", "commits", "tests_passed")


def load_data(path: Path) -> dict[str, Any]:
    """Load and validate dashboard data from JSON."""
    with path.open(encoding="utf-8") as file:
        data = json.load(file)
    validate_data(data)
    return data


def validate_data(data: dict[str, Any]) -> None:
    """Reject malformed, duplicate, or negative activity values."""
    if not isinstance(data.get("profile"), dict):
        raise ValueError("profile must be an object")
    snapshot = data.get("snapshot")
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be an object")
    missing = REQUIRED_SNAPSHOT_FIELDS - snapshot.keys()
    if missing:
        raise ValueError(f"snapshot is missing fields: {sorted(missing)}")

    parse_date(snapshot["captured_at"])
    for field in REQUIRED_SNAPSHOT_FIELDS - {"captured_at"}:
        require_nonnegative_integer(snapshot[field], f"snapshot.{field}")

    daily = data.get("daily")
    if not isinstance(daily, list):
        raise ValueError("daily must be a list")

    seen_dates: set[str] = set()
    for index, entry in enumerate(daily):
        if not isinstance(entry, dict):
            raise ValueError(f"daily[{index}] must be an object")
        day = entry.get("date")
        parse_date(day)
        if day in seen_dates:
            raise ValueError(f"duplicate daily date: {day}")
        seen_dates.add(day)
        for field in DAILY_INTEGER_FIELDS:
            value = entry.get(field)
            if value is not None:
                require_nonnegative_integer(value, f"daily[{index}].{field}")


def parse_date(value: Any) -> date:
    """Parse an ISO date and raise a readable validation error."""
    if not isinstance(value, str):
        raise ValueError(f"date must be an ISO string, got {value!r}")
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as error:
        raise ValueError(f"invalid ISO date: {value}") from error


def require_nonnegative_integer(value: Any, label: str) -> None:
    """Require a real non-negative integer, excluding booleans."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a non-negative integer")


def format_compact(value: int, approximate: bool = False) -> str:
    """Format large values for compact dashboard labels."""
    prefix = "≈" if approximate else ""
    if value >= 1_000_000_000:
        return f"{prefix}{value / 1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"{prefix}{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{prefix}{value / 1_000:.1f}K"
    return f"{prefix}{value:,}"


def format_duration(minutes: int) -> str:
    """Format minutes as a short hours-and-minutes label."""
    hours, remainder = divmod(minutes, 60)
    return f"{hours}h {remainder}m"


def record_daily_entry(
    data: dict[str, Any],
    day: str,
    tokens: int,
    tasks: int | None,
    commits: int | None,
    tests_passed: int | None,
    note: str | None,
) -> None:
    """Insert or update one exact daily aggregate without storing prompt content."""
    parse_date(day)
    values = {
        "tokens": tokens,
        "tasks": tasks,
        "commits": commits,
        "tests_passed": tests_passed,
    }
    for field, value in values.items():
        if value is not None:
            require_nonnegative_integer(value, field)

    entry = {"date": day, **values}
    if note:
        entry["note"] = note
    daily = data["daily"]
    for index, existing in enumerate(daily):
        if existing["date"] == day:
            daily[index] = entry
            break
    else:
        daily.append(entry)
    daily.sort(key=lambda item: item["date"])
    validate_data(data)


def heatmap_window(data: dict[str, Any]) -> tuple[date, date]:
    """Return a Sunday-to-Saturday window covering the latest snapshot."""
    candidates = [parse_date(data["snapshot"]["captured_at"])]
    candidates.extend(parse_date(item["date"]) for item in data["daily"])
    latest = max(candidates)
    days_until_saturday = (5 - latest.weekday()) % 7
    end = latest + timedelta(days=days_until_saturday)
    return end - timedelta(days=363), end


def intensity(tokens: int | None, maximum: int) -> int:
    """Map a token count to GitHub-style levels 0 through 4."""
    if tokens is None or tokens == 0 or maximum <= 0:
        return 0
    ratio = tokens / maximum
    if ratio <= 0.25:
        return 1
    if ratio <= 0.5:
        return 2
    if ratio <= 0.75:
        return 3
    return 4


def render_svg(data: dict[str, Any]) -> str:
    """Render an accessible, self-contained SVG for a GitHub README."""
    validate_data(data)
    snapshot = data["snapshot"]
    daily_by_date = {item["date"]: item for item in data["daily"]}
    known_tokens = [
        item["tokens"] for item in data["daily"] if item.get("tokens") is not None
    ]
    maximum = max(known_tokens, default=0)
    start, end = heatmap_window(data)

    width, height = 1120, 430
    grid_x, grid_y = 78, 250
    cell, gap = 14, 4
    pitch = cell + gap
    colors = ["#21262d", "#0e4429", "#006d32", "#26a641", "#39d353"]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">AI-Assisted Engineering Activity</title>',
        '<desc id="desc">Aggregate Codex token profile metrics and a 52-week daily token activity heatmap. Prompt content is never included.</desc>',
        "<style>",
        "text{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;fill:#e6edf3}",
        ".muted{fill:#8b949e}.label{font-size:13px}.value{font-size:29px;font-weight:600}",
        ".heading{font-size:22px;font-weight:600}.small{font-size:11px}",
        ".panel{fill:#161b22;stroke:#30363d}.grid{stroke:#30363d;stroke-width:1}",
        "</style>",
        f'<rect width="{width}" height="{height}" rx="16" fill="#0d1117"/>',
        '<text x="40" y="43" class="heading">AI-Assisted Engineering Activity</text>',
        f'<text x="1080" y="42" text-anchor="end" class="muted label">Snapshot {escape(snapshot["captured_at"])}</text>',
    ]

    metrics = [
        (
            "Lifetime tokens",
            format_compact(
                snapshot["lifetime_tokens"],
                snapshot.get("lifetime_tokens_approximate", False),
            ),
        ),
        ("Peak task", format_compact(snapshot["peak_task_tokens"])),
        ("Longest task", format_duration(snapshot["longest_task_minutes"])),
        ("Current streak", f'{snapshot["current_streak_days"]} days'),
        ("Total tasks", f'{snapshot["total_tasks"]:,}'),
    ]
    panel_width = 198
    for index, (label, value) in enumerate(metrics):
        x = 40 + index * 210
        parts.extend(
            [
                f'<rect x="{x}" y="65" width="{panel_width}" height="112" rx="10" class="panel"/>',
                f'<text x="{x + 18}" y="97" class="muted label">{escape(label)}</text>',
                f'<text x="{x + 18}" y="137" class="value">{escape(value)}</text>',
            ]
        )

    parts.extend(
        [
            '<text x="40" y="218" class="label">Daily token activity</text>',
            '<text x="1080" y="218" text-anchor="end" class="muted small">Exact aggregates only · no prompts or conversation content</text>',
        ]
    )

    month_positions: list[tuple[int, str]] = []
    previous_month = None
    current = start
    while current <= end:
        week = (current - start).days // 7
        weekday = (current.weekday() + 1) % 7
        entry = daily_by_date.get(current.isoformat())
        tokens = entry.get("tokens") if entry else None
        level = intensity(tokens, maximum)
        x = grid_x + week * pitch
        y = grid_y + weekday * pitch
        readable = "not recorded" if tokens is None else f"{tokens:,} tokens"
        parts.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" fill="{colors[level]}" class="grid"><title>{current.isoformat()}: {readable}</title></rect>'
        )
        if current.day <= 7 and current.month != previous_month:
            month_positions.append((x, current.strftime("%b")))
            previous_month = current.month
        current += timedelta(days=1)

    for x, label in month_positions:
        parts.append(f'<text x="{x}" y="240" class="muted small">{label}</text>')
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        y = grid_y + row * pitch + 11
        parts.append(f'<text x="40" y="{y}" class="muted small">{label}</text>')

    legend_x, legend_y = 900, 398
    parts.append(f'<text x="{legend_x - 46}" y="{legend_y + 11}" class="muted small">Less</text>')
    for level, color in enumerate(colors):
        x = legend_x + level * pitch
        parts.append(
            f'<rect x="{x}" y="{legend_y}" width="{cell}" height="{cell}" rx="3" fill="{color}" class="grid"/>'
        )
    parts.append(f'<text x="{legend_x + 5 * pitch + 4}" y="{legend_y + 11}" class="muted small">More</text>')

    known_days = len(known_tokens)
    status = (
        f"{known_days} exact day{'s' if known_days != 1 else ''} recorded"
        if known_days
        else "Daily tracking ready · first exact token value not recorded yet"
    )
    parts.extend(
        [
            f'<text x="40" y="409" class="muted small">{escape(status)}</text>',
            f'<text x="1080" y="409" text-anchor="end" class="muted small">Longest streak: {snapshot["longest_streak_days"]} days</text>',
            "</svg>",
        ]
    )
    return "\n".join(parts) + "\n"


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Write stable, reviewable JSON with a trailing newline."""
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--date", help="ISO date to insert or update")
    parser.add_argument("--tokens", type=int, help="Exact tokens used on --date")
    parser.add_argument("--tasks", type=int)
    parser.add_argument("--commits", type=int)
    parser.add_argument("--tests-passed", type=int)
    parser.add_argument("--note")
    return parser


def main() -> None:
    """Optionally record one day, then regenerate the dashboard."""
    args = build_parser().parse_args()
    data = load_data(args.data)
    if args.date or args.tokens is not None:
        if not args.date or args.tokens is None:
            raise SystemExit("--date and --tokens must be provided together")
        record_daily_entry(
            data,
            args.date,
            args.tokens,
            args.tasks,
            args.commits,
            args.tests_passed,
            args.note,
        )
        write_json(args.data, data)

    args.output.write_text(render_svg(data), encoding="utf-8")
    print(f"Generated {args.output}")


if __name__ == "__main__":
    main()
