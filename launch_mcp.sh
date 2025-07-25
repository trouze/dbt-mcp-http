#!/bin/bash
set -e

# Load environment variables from .env
export $(grep -v '^#' /Users/tylerrouze/demo/mcp/dbt-mcp/.env | xargs)

# Start the dbt-mcp server
/Users/tylerrouze/.local/bin/uvx dbt-mcp