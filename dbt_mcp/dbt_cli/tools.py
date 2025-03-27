import subprocess
from dbt_mcp.config.config import Config
from mcp.server.fastmcp import FastMCP

def register_dbt_cli_tools(dbt_mcp: FastMCP, config: Config) -> None:

    def _run_dbt_command(command: list[str]) -> str:
        result = subprocess.run(
            args=[config.dbt_command, *command],
            cwd=config.project_dir,
            capture_output=True,
            text=True,
        )
        # Cloud CLI reports errors to stderr, Core CLI reports errors to stdout
        if config.dbt_executable_type == "cloud" and  result.returncode != 0:
            return result.stderr
        else:
            return result.stdout

    @dbt_mcp.tool()
    def build() -> str:
        """
        Build the project
        """
        return _run_dbt_command(["build"])

    @dbt_mcp.tool()
    def compile() -> str:
        """
        Compile the project
        """
        return _run_dbt_command(["compile"])

    @dbt_mcp.tool()
    def docs() -> str:
        """
        Generate the docs for the project
        """
        return _run_dbt_command(["docs", "generate"])

    @dbt_mcp.tool(name="list")
    def ls() -> str:
        """
        List the resources in the project
        """
        return _run_dbt_command(["list"])

    @dbt_mcp.tool()
    def parse() -> str:
        """
        Parse the project
        """
        return _run_dbt_command(["parse"])

    @dbt_mcp.tool()
    def run() -> str:
        """
        Run the project
        """
        return _run_dbt_command(["run"])

    @dbt_mcp.tool()
    def test() -> str:
        """
        Test the project
        """
        return _run_dbt_command(["test"])
