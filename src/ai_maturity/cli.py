"""AI Maturity Framework CLI."""
import click


@click.group()
def cli():
    """AI Maturity Framework — assess and track AI adoption maturity across your team."""
    pass


@cli.command()
@click.argument('logs_path', type=click.Path(exists=True))
@click.option('--team-name', default=None, help='Team name')
@click.option('--user-name', default=None, help='User name')
def upload(logs_path, team_name, user_name):
    """
    Upload Claude Code session logs for analysis.

    LOGS_PATH: Path to logs directory or .zip file

    Example:
        ai-maturity upload ~/.claude/projects/myapp --team-name myteam --user-name alice
    """
    raise NotImplementedError


@cli.command()
@click.option('--team-name', default=None, help='Team name')
@click.option('--user-name', default=None, help='User name')
@click.option('--report-type', type=click.Choice(['individual', 'team']), default='individual')
@click.option('--output-dir', type=click.Path(), default=None)
def report(team_name, user_name, report_type, output_dir):
    """
    Generate an AI maturity report from uploaded logs.

    Example:
        ai-maturity report --team-name myteam --user-name alice
        ai-maturity report --team-name myteam --report-type team
    """
    raise NotImplementedError


@cli.command()
@click.option('--team-name', default=None, help='Team name')
@click.option('--user-name', default=None, help='User name')
@click.option('--logs-path', 'logs_path_override', type=click.Path(exists=True), default=None,
              help='Direct path to logs directory (skips DB lookup)')
@click.option('--output-dir', type=click.Path(), default=None)
@click.option('--save-context', is_flag=True, default=False,
              help='Write a .context.txt file showing what the scorer sends to Claude')
def assess(team_name, user_name, logs_path_override, output_dir, save_context):
    """
    Run a prompt-quality AI maturity assessment for a developer.

    Scores all 12 maturity sub-dimensions by analyzing actual developer prompts
    via Claude. Produces a clean Markdown report with dimension-by-dimension
    analysis and exemplar prompts.

    Example:
        ai-maturity assess --team-name myteam --user-name alice
        ai-maturity assess --logs-path ~/.claude/projects/myapp --user-name alice --save-context
    """
    raise NotImplementedError


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


if __name__ == '__main__':
    cli()
