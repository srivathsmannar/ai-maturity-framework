"""AI Maturity Framework CLI."""
from __future__ import annotations

from pathlib import Path

import click

from ai_maturity.store import Store


def _get_store(db: str | None) -> Store:
    if db:
        return Store(Path(db))
    return Store()


@click.group()
def cli():
    """AI Maturity Framework — assess and track AI adoption maturity."""
    pass


@cli.command()
@click.argument("logs_path", type=click.Path(exists=True))
@click.option("--name", required=True, help="Developer name")
@click.option("--email", required=True, help="Developer email (unique identifier)")
@click.option("--team", required=True, help="Team name")
@click.option("--db", default=None, hidden=True)
def submit(logs_path, name, email, team, db):
    """Submit Claude Code session logs for a developer.

    LOGS_PATH: Directory containing session .jsonl files

    Example:
        ai-maturity submit ~/.claude/projects/myapp/ --name alice --email alice@company.com --team platform
    """
    from ai_maturity.pipeline import process_session

    store = _get_store(db)
    logs = Path(logs_path)

    session_files = sorted(logs.glob("*.jsonl"))
    if not session_files:
        click.echo(f"No .jsonl files found in {logs_path}")
        return

    existing = store.get_developer(email)
    if existing:
        click.echo(f"  Note: replacing previous submission for {existing['name']} ({email})")

    all_records = []
    for session_file in session_files:
        results = process_session(session_file, team=team, user=name)
        if results:
            all_records.extend(results)
            click.echo(f"  {session_file.name}: {len(results)} records")

    store.save_developer(email, name, team)
    store.save_records(email, all_records)
    click.echo(f"\nSubmitted {len(all_records)} records for {name} <{email}> ({team})")


@cli.command()
@click.option("--email", required=True, help="Developer email")
@click.option("--model", default="sonnet", help="Claude model for grading")
@click.option("--db", default=None, hidden=True)
def assess(email, model, db):
    """Grade a developer's AI maturity across 12 sub-dimensions.

    Example:
        ai-maturity assess --email alice@company.com
    """
    from ai_maturity.grader import grade_session
    from ai_maturity.scorer import compute_scores

    store = _get_store(db)

    dev = store.get_developer(email)
    if dev is None:
        click.echo(f"Developer '{email}' not found. Run 'submit' first.")
        return

    existing_scores = store.get_scores(email)
    if existing_scores:
        click.echo(f"  Note: replacing previous assessment for {dev['name']}")

    records = store.get_records(email)
    click.echo(f"Grading {dev['name']} ({dev['team']}) — {len(records)} records, model={model}...")

    gt_path = Path(__file__).parent.parent.parent / "docs" / "MATURITY_ASSESSMENT_GROUND_TRUTH.md"
    tmp_input = store.write_records_jsonl(email)
    try:
        results = grade_session(tmp_input, gt_path, model=model)
    finally:
        tmp_input.unlink(missing_ok=True)

    store.save_scores(email, results)

    scores = compute_scores(results)
    click.echo(f"\n{'=' * 50}")
    click.echo(f"Overall Score: {scores['overall_score']}  ({scores['maturity_label']})")
    click.echo(f"{'=' * 50}")
    for dim, info in scores["dimensions"].items():
        click.echo(f"  {dim}: {info['average']}")
        for sd, lvl in info["sub_dimensions"].items():
            click.echo(f"    {sd}: L{lvl}")


@cli.command()
@click.option("--email", required=True, help="Developer email")
@click.option("--format", "output_format", type=click.Choice(["md", "html", "both"]),
              default="both", help="Output format (default: both)")
@click.option("--model", default="sonnet", help="Claude model for narratives")
@click.option("--output-dir", default=None, help="Custom output directory")
@click.option("--db", default=None, hidden=True)
def report(email, output_format, model, output_dir, db):
    """Generate an AI maturity assessment report.

    Example:
        ai-maturity report --email alice@company.com
        ai-maturity report --email alice@company.com --format html
    """
    from ai_maturity.report import generate_report

    store = _get_store(db)

    dev = store.get_developer(email)
    if dev is None:
        click.echo(f"Developer '{email}' not found.")
        return

    scores = store.get_scores(email)
    if not scores:
        click.echo(f"No scores for '{email}'. Run 'assess' first.")
        return

    out = Path(output_dir) if output_dir else store.reports_dir()
    out.mkdir(parents=True, exist_ok=True)

    click.echo(f"Generating report for {dev['name']} ({dev['team']})...")
    tmp_scored = store.write_scores_jsonl(email)
    tmp_input = store.write_records_jsonl(email)
    try:
        md_content = generate_report(tmp_scored, tmp_input, model=model)
    finally:
        tmp_scored.unlink(missing_ok=True)
        tmp_input.unlink(missing_ok=True)

    stem = email.split("@")[0]

    if output_format in ("md", "both"):
        md_path = out / f"{stem}_report.md"
        md_path.write_text(md_content)
        click.echo(f"  Markdown: {md_path}")

    if output_format in ("html", "both"):
        from ai_maturity.html_report import md_to_html
        md_path = out / f"{stem}_report.md"
        if not md_path.exists():
            md_path.write_text(md_content)
        html_path = out / f"{stem}_report.html"
        md_to_html(md_path, html_path)
        click.echo(f"  HTML: {html_path}")


@cli.command(name="list")
@click.option("--db", default=None, hidden=True)
def list_developers(db):
    """List all submitted developers and their assessment status."""
    store = _get_store(db)
    devs = store.list_developers()

    if not devs:
        click.echo("No developers submitted yet.")
        return

    click.echo(f"{'Name':<16} {'Email':<30} {'Team':<12} {'Submitted':<12} {'Assessed'}")
    click.echo("-" * 80)
    for d in devs:
        submitted = d["submitted_at"][:10]
        assessed = "Yes" if d["has_scores"] else "No"
        click.echo(f"{d['name']:<16} {d['email']:<30} {d['team']:<12} {submitted:<12} {assessed}")


if __name__ == "__main__":
    cli()
