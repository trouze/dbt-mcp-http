# Contributing

With [task](https://taskfile.dev/) installed, simply run `task` to see the list of available commands. For comments, questions, or requests open a GitHub issue.

## Setup

1. Clone the repository:
```shell
git clone https://github.com/dbt-labs/dbt-mcp.git
cd dbt-mcp
```

2. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)

3. [Install Task](https://taskfile.dev/installation/)

4. Run `task install`

5. Configure environment variables:
```shell
cp .env.example .env
```
Then edit `.env` with your specific environment variables (see the `Configuration` section of the `README.md`).

## Debugging

If you encounter any problems. You can try running `task run` to see errors in your terminal.

## Release

To release a new version:

1. Increment `version` in `pyproject.toml` by following semantic versioning best practices.
2. Run `uv sync`.
3. Open a PR with these changes.
4. Once the PR is merged, run the `Publish to PyPi` GitHub action [here](https://github.com/dbt-labs/dbt-mcp/actions/workflows/release.yml). Anyone on the dbt Labs AI team can approve this workflow.