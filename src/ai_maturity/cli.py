"""AI Maturity Framework CLI."""
from __future__ import annotations

import json
from pathlib import Path

import click

from ai_maturity.store import Store


def _get_store(db: str | None) -> Store:
    """Create a Store with an optional custom db path."""
    if db:
        return Store(Path(db))
    return Store()


@click.group()
def cli():
    """AI Maturity Framework -- assess and track AI adoption maturity across your team."""
    pass


@cli.command()
@click.argument("logs_path", type=click.Path(exists=True))
@click.option("--name", required=True, help="Developer name")
@click.option("--team", required=True, help="Team name")
@click.option("--db", default=None, hidden=True, help="Override database path")
def submit(logs_path: str, name: str, team: str, db: str | None) -> None:
    """Extract session logs and save to store.

    LOGS_PATH: Directory containing .jsonl session files.
    """
    from ai_maturity.pipeline import process_session

    logs = Path(logs_path)
    session_files = sorted(logs.glob("*.jsonl"))
    if not session_files:
        click.echo(f"No .jsonl files found in {logs_path}")
        return

    all_records: list[dict] = []
    for session_file in session_files:
        results = process_session(session_file, team=team, user=name)
        if results:
            all_records.extend(results)
            click.echo(f"  {session_file.name}: {len(results)} records")

    store = _get_store(db)
    store.save_developer(name, team)
    store.save_records(name, all_records)

    click.echo(f"\nSubmitted {len(all_records)} records for {name} (team: {team})")


@cli.command()
@click.argument("name")
@click.option("--model", default="sonnet", help="Claude model for grading")
@click.option("--db", default=None, hidden=True, help="Override database path")
def assess(name: str, model: str, db: str | None) -> None:
    """Grade a developer's sessions and save scores.

    NAME: Developer name (must have been submitted first).
    """
    from ai_maturity.grader import grade_session
    from ai_maturity.scorer import compute_scores

    store = _get_store(db)

    dev = store.get_developer(name)
    if dev is None:
        click.echo(f"Developer '{name}' not found. Run submit first.")
        return

    ground_truth_path = (
        Path(__file__).parent.parent.parent / "docs" / "MATURITY_ASSESSMENT_GROUND_TRUTH.md"
    )

    tmp_input = store.write_records_jsonl(name)
    try:
        results = grade_session(tmp_input, ground_truth_path, model=model)
    finally:
        tmp_input.unlink(missing_ok=True)

    store.save_scores(name, results)

    scores = compute_scores(results)
    click.echo(f"\n{'=' * 50}")
    click.echo(f"Overall Score: {scores['overall_score']}  ({scores['maturity_label']})")
    click.echo(f"{'=' * 50}")
    for dim, info in scores["dimensions"].items():
        click.echo(f"  {dim}: {info['average']}")
        for sd, lvl in info["sub_dimensions"].items():
            click.echo(f"    {sd}: L{lvl}")


@cli.command()
@click.argument("name")
@click.option("--model", default="sonnet", help="Claude model for narrative writing")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["md", "html", "both"]),
    default="both",
    help="Output format (default: both)",
)
@click.option("--output-dir", type=click.Path(), default=None, help="Override output directory")
@click.option("--db", default=None, hidden=True, help="Override database path")
def report(name: str, model: str, output_format: str, output_dir: str | None, db: str | None) -> None:
    """Generate an AI maturity report from scored data.

    NAME: Developer name (must have been assessed first).
    """
    from ai_maturity.report import generate_report

    store = _get_store(db)

    dev = store.get_developer(name)
    if dev is None:
        click.echo(f"Developer '{name}' not found.")
        return

    scores = store.get_scores(name)
    if not scores:
        click.echo(f"No scores found for '{name}'. Run assess first.")
        return

    out = Path(output_dir) if output_dir else store.reports_dir()
    out.mkdir(parents=True, exist_ok=True)

    tmp_scored = store.write_scores_jsonl(name)
    tmp_input = store.write_records_jsonl(name)
    try:
        md_content = generate_report(tmp_scored, tmp_input, model=model)
    finally:
        tmp_scored.unlink(missing_ok=True)
        tmp_input.unlink(missing_ok=True)

    if output_format in ("md", "both"):
        md_path = out / f"{name}_report.md"
        md_path.write_text(md_content)
        click.echo(f"  Markdown: {md_path}")

    if output_format in ("html", "both"):
        from ai_maturity.html_report import md_to_html

        md_path = out / f"{name}_report.md"
        if not md_path.exists():
            md_path.write_text(md_content)
        html_path = out / f"{name}_report.html"
        md_to_html(md_path, html_path)
        click.echo(f"  HTML: {html_path}")


@cli.command(name="list")
@click.option("--db", default=None, hidden=True, help="Override database path")
def list_developers(db: str | None) -> None:
    """Show all developers in the store."""
    store = _get_store(db)
    devs = store.list_developers()

    if not devs:
        click.echo("No developers found.")
        return

    click.echo(f"{'Name':<20} {'Team':<15} {'Submitted':<25} {'Scored'}")
    click.echo("-" * 70)
    for d in devs:
        submitted = d["submitted_at"][:19] if d["submitted_at"] else ""
        scored = "yes" if d["has_scores"] else "no"
        click.echo(f"{d['name']:<20} {d['team']:<15} {submitted:<25} {scored}")


def _write_context(results: list[dict], path: Path) -> None:
    """Write a human-readable context file with per-sub-dimension grading details."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("AI Maturity Assessment Context")
    lines.append("=" * 40)
    lines.append("")
    for r in results:
        lines.append(f"Sub-dimension: {r['sub_dimension']}")
        lines.append(f"  Dimension:   {r['dimension']}")
        lines.append(f"  Level:       L{r['level']} ({r.get('level_label', '')})")
        lines.append(f"  Confidence:  {r.get('confidence', 'N/A')}")
        lines.append(f"  Reasoning:   {r.get('reasoning', '')}")
        evidence = r.get("evidence", [])
        if evidence:
            lines.append(f"  Evidence:    {'; '.join(str(e) for e in evidence)}")
        signals = r.get("matched_signals", [])
        if signals:
            lines.append(f"  Signals:     {'; '.join(str(s) for s in signals)}")
        lines.append(f"  Records:     {r.get('record_count', 0)}")
        lines.append("")
    with open(path, "w") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    cli()
