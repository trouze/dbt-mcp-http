import subprocess

from mcp.server.fastmcp import FastMCP

from dbt_mcp.config.config import Config
from dbt_mcp.prompts.prompts import get_prompt


def register_dbt_cli_tools(dbt_mcp: FastMCP, config: Config) -> None:
    def _run_dbt_command(command: list[str]) -> str:
        process = subprocess.Popen(
            args=[config.dbt_command, *command],
            cwd=config.project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        output, _ = process.communicate()
        return output

    @dbt_mcp.tool(description=get_prompt("dbt_cli/build"))
    def build() -> str:
        return _run_dbt_command(["build"])

    @dbt_mcp.tool(description=get_prompt("dbt_cli/compile"))
    def compile() -> str:
        return _run_dbt_command(["compile"])

    @dbt_mcp.tool(description=get_prompt("dbt_cli/docs"))
    def docs() -> str:
        return _run_dbt_command(["docs", "generate"])

    @dbt_mcp.tool(name="list", description=get_prompt("dbt_cli/list"))
    def ls() -> str:
        return _run_dbt_command(["list"])

    @dbt_mcp.tool(description=get_prompt("dbt_cli/parse"))
    def parse() -> str:
        return _run_dbt_command(["parse"])

    @dbt_mcp.tool(description=get_prompt("dbt_cli/run"))
    def run() -> str:
        return _run_dbt_command(["run"])

    @dbt_mcp.tool(description=get_prompt("dbt_cli/test"))
    def test() -> str:
        return _run_dbt_command(["test"])

    @dbt_mcp.tool(description=get_prompt("dbt_cli/show"))
    def show(sql_query: str, limit: int | None = None) -> str:
        args = ["show", "--inline", sql_query, "--favor-state"]
        if limit:
            args.extend(["--limit", str(limit)])
        args.extend(["--output", "json"])
        return _run_dbt_command(args)
