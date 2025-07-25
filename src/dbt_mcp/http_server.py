#!/usr/bin/env python3
"""
HTTP server entry point for dbt-mcp.
This serves the MCP server over HTTP instead of stdio.
"""
import asyncio
import logging
import os
import subprocess
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dbt_mcp.config.config import load_config
from dbt_mcp.mcp.server import create_dbt_mcp

logger = logging.getLogger(__name__)


# Global variable to store the MCP server instance
dbt_mcp_server = None

# Add this after your imports and before initialize_mcp_server

async def refresh_dbt_project_internal():
    """Internal function to refresh the dbt project (no HTTP response)"""
    dbt_project_dir = os.getenv("DBT_PROJECT_DIR", "/app/dbt-project")
    repo_branch = os.getenv("DBT_REPO_BRANCH", "main")
    github_token = os.getenv("GITHUB_TOKEN")
    repo_url = os.getenv("DBT_REPO_URL")
    
    # If we have a GitHub token, configure git to use it
    if github_token:
        subprocess.run([
            "git", "config", "--global", "credential.helper", 
            f"!f() {{ echo \"username=token\"; echo \"password={github_token}\"; }}; f"
        ], check=True, capture_output=True)
    
    try:
        if os.path.exists(dbt_project_dir):
            logger.info(f"Updating existing dbt project at {dbt_project_dir}")
            
            subprocess.run(
                ["git", "fetch", "origin"], 
                cwd=dbt_project_dir, 
                check=True, 
                capture_output=True,
                text=True
            )
            subprocess.run(
                ["git", "reset", "--hard", f"origin/{repo_branch}"], 
                cwd=dbt_project_dir, 
                check=True, 
                capture_output=True,
                text=True
            )
            subprocess.run(
                ["git", "pull", "origin", repo_branch], 
                cwd=dbt_project_dir, 
                check=True, 
                capture_output=True,
                text=True
            )
        else:
            if not repo_url:
                raise Exception("DBT_REPO_URL environment variable not set")
            
            logger.info(f"Cloning dbt project from {repo_url}")
            
            # Use token in URL if provided
            if github_token and "github.com" in repo_url:
                if repo_url.startswith("https://github.com/"):
                    auth_url = repo_url.replace("https://github.com/", f"https://{github_token}@github.com/")
                else:
                    auth_url = repo_url
            else:
                auth_url = repo_url
            
            subprocess.run(
                ["git", "clone", "-b", repo_branch, auth_url, dbt_project_dir],
                check=True,
                capture_output=True,
                text=True
            )
            
        logger.info("dbt project refreshed successfully")
        
    finally:
        # Clean up git credentials for security
        if github_token:
            try:
                subprocess.run([
                    "git", "config", "--global", "--unset", "credential.helper"
                ], capture_output=True)
            except:
                pass

async def initialize_mcp_server():
    """Initialize the dbt MCP server"""
    global dbt_mcp_server
    if dbt_mcp_server is None:
        config = load_config()
        # Create MCP server without FastAPI lifespan since it's not an HTTP server
        from dbt_mcp.mcp.server import DbtMCP
        from dbt_mcp.tracking.tracking import UsageTracker
        from dbt_mcp.dbt_cli.tools import register_dbt_cli_tools
        from dbt_mcp.discovery.tools import register_discovery_tools
        from dbt_mcp.remote.tools import register_remote_tools
        from dbt_mcp.semantic_layer.tools import register_sl_tools
        
        # Create the MCP server directly without lifespan
        dbt_mcp_server = DbtMCP(
            config=config,
            usage_tracker=UsageTracker(),
            name="dbt",
        )

        # Register tools based on configuration
        if config.semantic_layer_config:
            logger.info("Registering semantic layer tools")
            register_sl_tools(dbt_mcp_server, config.semantic_layer_config, config.disable_tools)

        if config.discovery_config:
            logger.info("Registering discovery tools")
            register_discovery_tools(dbt_mcp_server, config.discovery_config, config.disable_tools)

        if config.dbt_cli_config:
            logger.info("Registering dbt cli tools")
            register_dbt_cli_tools(dbt_mcp_server, config.dbt_cli_config, [])

        if config.remote_config:
            logger.info("Registering remote tools")
            await register_remote_tools(dbt_mcp_server, config.remote_config, config.disable_tools)
        
        logger.info("dbt MCP server created and ready")

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting dbt-mcp HTTP server")
    
    # Clone/refresh the dbt project on startup
    logger.info("Refreshing dbt project on startup...")
    try:
        await refresh_dbt_project_internal()
        logger.info("dbt project refreshed successfully on startup")
    except Exception as e:
        logger.error(f"Failed to refresh dbt project on startup: {e}")
        # Don't fail startup, but log the error
    
    # Initialize the MCP server during startup
    await initialize_mcp_server()
    
    try:
        yield
    finally:
        logger.info("Shutting down dbt-mcp HTTP server")

def create_http_app() -> FastAPI:
    """Create the FastAPI application with the dbt-mcp server."""
    
    # Create FastAPI app
    app = FastAPI(
        title="dbt MCP Server",
        description="HTTP API for dbt MCP Server",
        version="1.0.0",
        lifespan=app_lifespan
    )
    
    # Add CORS middleware for cross-origin requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure this more restrictively in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "ok", "service": "dbt-mcp"}
    
    # MCP tools list endpoint
    @app.get("/tools/list")
    async def list_tools():
        global dbt_mcp_server
        if not dbt_mcp_server:
            # Try to initialize if not already done
            await initialize_mcp_server()
        
        if not dbt_mcp_server:
            return {"error": "Server not initialized"}
            
        tools = await dbt_mcp_server.list_tools()
        return {"tools": [tool.model_dump() for tool in tools]}
    
    # MCP tool call endpoint
    @app.post("/tools/call")
    async def call_tool(request: dict):
        global dbt_mcp_server
        if not dbt_mcp_server:
            # Try to initialize if not already done
            await initialize_mcp_server()
        
        if not dbt_mcp_server:
            return {"error": "Server not initialized"}
        
        tool_name = request.get("params", {}).get("name")
        arguments = request.get("params", {}).get("arguments", {})
        
        if not tool_name:
            return {"error": "Tool name is required"}
        
        try:
            result = await dbt_mcp_server.call_tool(tool_name, arguments)
            return {
                "result": {
                    "content": [
                        item.model_dump() if hasattr(item, 'model_dump') else item
                        for item in result
                    ]
                }
            }
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {
                "error": {
                    "code": -1,
                    "message": str(e)
                }
            }

    return app


def main():
    """Main entry point for HTTP server."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    logger.info(f"Starting dbt-mcp HTTP server on {host}:{port}")
    
    # Create and run the app
    app = create_http_app()
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )

app = create_http_app()

if __name__ == "__main__":
    main()
