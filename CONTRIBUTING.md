# Contributing

With [task](https://taskfile.dev/) installed, simply run `task` to see the list of available commands. For comments, questions, or requests open a GitHub issue.

## Release

To release a new version:

1. Increment `version` in `pyproject.toml` by following semantic versioning best practices.
2. Run `uv sync`.
3. Open a PR with these changes.
4. Once the PR is merged, run the `Publish to PyPi` GitHub action [here](https://github.com/dbt-labs/dbt-mcp/actions/workflows/release.yml). Anyone on the dbt Labs AI team can approve this workflow.