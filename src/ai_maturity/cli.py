"""AI Maturity Framework CLI."""
from __future__ import annotations

import json
from pathlib import Path

import click


@click.group()
def cli():
    """AI Maturity Framework — assess and track AI adoption maturity across your team."""
    pass


@cli.command()
@click.argument('logs_path', type=click.Path(exists=True))
@click.option('--team-name', default="unknown", help='Team name')
@click.option('--user-name', default="unknown", help='User name')
@click.option('--output-dir', type=click.Path(), default=None,
              help='Output directory for assessment-input JSONL (default: data/input/)')
def upload(logs_path, team_name, user_name, output_dir):
    """
    Extract and classify Claude Code session logs for assessment.

    LOGS_PATH: Path to directory containing session .jsonl files

    Example:
        ai-maturity upload ~/.claude/projects/myapp --team-name myteam --user-name alice
    """
    from datetime import date
    from pathlib import Path
    from ai_maturity.pipeline import process_session, write_output

    logs = Path(logs_path)
    out = Path(output_dir) if output_dir else Path("data/input")

    session_files = sorted(logs.glob("*.jsonl"))
    if not session_files:
        click.echo(f"No .jsonl files found in {logs_path}")
        return

    total_records = 0
    for session_file in session_files:
        results = process_session(session_file, team=team_name, user=user_name)
        if not results:
            continue
        today = date.today().isoformat()
        out_name = f"{team_name}_{user_name}_{today}_{session_file.stem[:8]}.jsonl"
        write_output(results, out / out_name)
        total_records += len(results)
        click.echo(f"  {session_file.name}: {len(results)} records extracted")

    click.echo(f"\nDone. {total_records} records from {len(session_files)} sessions -> {out}/")


@cli.command()
@click.option('--scored-dir', type=click.Path(exists=True), default='data/output/',
              help='Directory containing scored JSONL from assess (default: data/output/)')
@click.option('--input-dir', type=click.Path(exists=True), default='data/input/',
              help='Directory containing input JSONL from upload (default: data/input/)')
@click.option('--output-dir', type=click.Path(), default='reports/',
              help='Output directory for report files (default: reports/)')
@click.option('--team-name', default=None, help='Filter by team name')
@click.option('--user-name', default=None, help='Filter by user name')
@click.option('--model', default='sonnet', help='Claude model for narrative writing')
def report(scored_dir, input_dir, output_dir, team_name, user_name, model):
    """
    Generate an AI maturity report from scored assessment data.

    Example:
        ai-maturity report --scored-dir data/output/ --input-dir data/input/
        ai-maturity report --team-name myteam --user-name alice
    """
    from ai_maturity.report import generate_report

    scored = Path(scored_dir)
    inp = Path(input_dir)
    out = Path(output_dir)

    # Find scored JSONL files, optionally filtered by team/user
    scored_files = sorted(scored.glob("*_scored.jsonl"))
    if team_name:
        scored_files = [f for f in scored_files if team_name in f.name]
    if user_name:
        scored_files = [f for f in scored_files if user_name in f.name]

    if not scored_files:
        click.echo(f"No scored JSONL files found in {scored}")
        return

    # Find input JSONL files
    input_files = sorted(inp.glob("*.jsonl"))

    out.mkdir(parents=True, exist_ok=True)

    for scored_file in scored_files:
        # Find matching input file by stem substring matching
        stem = scored_file.stem.replace("_scored", "")
        matching_input = None
        for inf in input_files:
            if stem in inf.stem or inf.stem in stem:
                matching_input = inf
                break

        if matching_input is None and input_files:
            click.echo(f"  Warning: no exact input match for {scored_file.name}, using {input_files[0].name}")
            matching_input = input_files[0]

        if matching_input is None:
            click.echo(f"  Warning: no input files available for {scored_file.name}, skipping")
            continue

        md_content = generate_report(scored_file, matching_input, model=model)
        out_path = out / f"{stem}_report.md"
        out_path.write_text(md_content)
        click.echo(f"Report written to {out_path}")


@cli.command()
@click.option('--input-dir', type=click.Path(), default='data/input/',
              help='Directory containing assessment-input JSONL from upload (default: data/input/)')
@click.option('--output-dir', type=click.Path(), default='data/output/',
              help='Scored output directory (default: data/output/)')
@click.option('--team-name', default=None, help='Filter input files by team name')
@click.option('--user-name', default=None, help='Filter input files by user name')
@click.option('--model', default='sonnet', help='Claude model to use (default: sonnet)')
@click.option('--save-context', is_flag=True, default=False,
              help='Write a .context.txt file showing grading details')
def assess(input_dir, output_dir, team_name, user_name, model, save_context):
    """
    Run a prompt-quality AI maturity assessment for a developer.

    Scores all 12 maturity sub-dimensions by analyzing actual developer prompts
    via Claude. Produces scored JSONL output with dimension-by-dimension
    analysis.

    Example:
        ai-maturity assess --input-dir data/input/ --output-dir data/output/
        ai-maturity assess --team-name myteam --user-name alice --save-context
    """
    from ai_maturity.grader import grade_session
    from ai_maturity.pipeline import write_output
    from ai_maturity.scorer import compute_scores

    inp = Path(input_dir)
    out = Path(output_dir)
    ground_truth_path = Path(__file__).parent.parent.parent / "docs" / "MATURITY_ASSESSMENT_GROUND_TRUTH.md"

    # Find input JSONL files, optionally filtered by team/user
    input_files = sorted(inp.glob("*.jsonl"))
    if team_name:
        input_files = [f for f in input_files if team_name in f.name]
    if user_name:
        input_files = [f for f in input_files if user_name in f.name]

    if not input_files:
        click.echo(f"No input JSONL files found in {inp}")
        return

    all_results: list[dict] = []

    for input_file in input_files:
        click.echo(f"Grading: {input_file.name}")
        results = grade_session(input_file, ground_truth_path, model=model)
        all_results.extend(results)

        # Write scored output
        out_name = input_file.stem + "_scored.jsonl"
        write_output(results, out / out_name)
        click.echo(f"  -> {out / out_name} ({len(results)} sub-dimensions)")

    # Compute aggregate scores
    scores = compute_scores(all_results)

    # Print summary
    click.echo(f"\n{'=' * 50}")
    click.echo(f"Overall Score: {scores['overall_score']}  ({scores['maturity_label']})")
    click.echo(f"{'=' * 50}")
    for dim, info in scores["dimensions"].items():
        click.echo(f"  {dim}: {info['average']}")
        for sd, lvl in info["sub_dimensions"].items():
            click.echo(f"    {sd}: L{lvl}")

    # Optionally write context file
    if save_context:
        context_path = out / "assess.context.txt"
        _write_context(all_results, context_path)
        click.echo(f"\nContext written to {context_path}")


@cli.command(name="list-uploads")
@click.option('--team-name', default=None)
@click.option('--user-name', default=None)
def list_uploads(team_name, user_name):
    """List all uploaded log sets."""
    raise NotImplementedError


@cli.command(name="list-reports")
@click.option('--team-name', default=None)
@click.option('--user-name', default=None)
def list_reports(team_name, user_name):
    """List all generated reports."""
    raise NotImplementedError


@cli.command(name="open-report")
@click.option('--team-name', default=None)
@click.option('--user-name', default=None)
@click.option('--id', 'report_id', default=None, type=int, help='Report ID from list-reports')
def open_report(team_name, user_name, report_id):
    """Open the most recent report in the system viewer."""
    raise NotImplementedError


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


if __name__ == '__main__':
    cli()
