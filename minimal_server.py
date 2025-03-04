#!/usr/bin/env python
"""
Minimal MCP Server for dbt Semantic Layer that just lists metrics
"""

import json
import os
import time
import requests
from mcp.server.fastmcp import FastMCP

# Create the MCP server
mcp = FastMCP("dbt Minimal")

# Global config to store connection information
CONFIG = {
    "host": os.environ.get("DBT_HOST"),
    "environment_id": os.environ.get("DBT_ENV_ID"),
    "token": os.environ.get("DBT_TOKEN"),
    "is_connected": False
}

# Try to connect automatically if environment variables are set
if CONFIG["host"] and CONFIG["environment_id"] and CONFIG["token"]:
    try:
        url = f"https://{CONFIG['host']}/api/graphql"
        headers = {"Authorization": f"Bearer {CONFIG['token']}"}
        query = f"""{{
          environmentInfo(environmentId: "{CONFIG['environment_id']}") {{
            dialect
          }}
        }}"""
        
        print(f"Executing GraphQL query: {query}")
        
        response = requests.post(
            url, 
            headers=headers,
            json={"query": query}
        )
        
        data = response.json()
        if "errors" not in data:
            CONFIG["is_connected"] = True
            print(f"Successfully connected to {CONFIG['host']} using environment variables")
        else:
            print(f"Connection error: {data['errors']}")
    except Exception as e:
        print(f"Failed to connect using environment variables: {str(e)}")

@mcp.tool()
def connect(host, environment_id, token):
    """
    Connect to the dbt Semantic Layer
    
    Args:
        host: The host (e.g., semantic-layer.cloud.getdbt.com)
        environment_id: The dbt environment ID
        token: The service token
    """
    CONFIG["host"] = host
    CONFIG["environment_id"] = environment_id
    CONFIG["token"] = token
    
    # Test connection
    try:
        url = f"https://{host}/api/graphql"
        headers = {"Authorization": f"Bearer {token}"}
        query = f"""{{
          environmentInfo(environmentId: "{environment_id}") {{
            dialect
          }}
        }}"""
        
        print(f"Executing GraphQL query: {query}")
        
        response = requests.post(
            url, 
            headers=headers,
            json={"query": query}
        )
        
        data = response.json()
        if "errors" in data:
            CONFIG["is_connected"] = False
            return f"Failed to connect: {data['errors']}"
        
        CONFIG["is_connected"] = True
        return f"Successfully connected to {host}"
    except Exception as e:
        CONFIG["is_connected"] = False
        return f"Connection error: {str(e)}"

@mcp.tool()
def list_metrics():
    """
    List all metrics from the dbt Semantic Layer
    """
    if not CONFIG["is_connected"]:
        return "Not connected. Use connect() first."
    
    try:
        url = f"https://{CONFIG['host']}/api/graphql"
        headers = {"Authorization": f"Bearer {CONFIG['token']}"}
        query = f"""{{
          metrics(environmentId: "{CONFIG['environment_id']}") {{
            name
            description
            type
          }}
        }}"""
        
        print(f"Executing GraphQL query: {query}")
        
        response = requests.post(
            url, 
            headers=headers,
            json={"query": query}
        )
        
        data = response.json()
        
        if "errors" in data:
            return f"GraphQL error: {data['errors']}"
        
        return json.dumps(data["data"]["metrics"], indent=2)
    except Exception as e:
        return f"Error listing metrics: {str(e)}"

@mcp.tool()
def get_dimensions(metrics):
    """
    Get available dimensions for specified metrics
    
    Args:
        metrics: List of metric names or a single metric name
    """
    if not CONFIG["is_connected"]:
        return "Not connected. Use connect() first."
    
    try:
        # Ensure metrics is a list
        if isinstance(metrics, str):
            metrics = [metrics]
            
        # Generate metric list string for GraphQL
        metric_list = ", ".join([f"{{name: \"{metric}\"}}" for metric in metrics])
        
        url = f"https://{CONFIG['host']}/api/graphql"
        headers = {"Authorization": f"Bearer {CONFIG['token']}"}
        query = f"""
        {{
          dimensions(
            environmentId: "{CONFIG['environment_id']}"
            metrics: [{metric_list}]
          ) {{
            name
            description
            type
            typeParams {{
              timeGranularity
            }}
            queryableGranularities
          }}
        }}
        """
        
        print(f"Executing GraphQL query: {query}")
        
        response = requests.post(
            url, 
            headers=headers,
            json={"query": query}
        )
        
        data = response.json()
        
        if "errors" in data:
            return f"GraphQL error: {data['errors']}"
        
        return json.dumps(data["data"]["dimensions"], indent=2)
    except Exception as e:
        return f"Error getting dimensions: {str(e)}"

@mcp.tool()
def get_granularities(metrics):
    """
    Get available time granularities for the specified metrics
    
    Args:
        metrics: List of metric names or a single metric name
    """
    if not CONFIG["is_connected"]:
        return "Not connected. Use connect() first."
    
    try:
        # Ensure metrics is a list
        if isinstance(metrics, str):
            metrics = [metrics]
            
        # Generate metric list string for GraphQL
        metric_list = ", ".join([f"{{name: \"{metric}\"}}" for metric in metrics])
        
        url = f"https://{CONFIG['host']}/api/graphql"
        headers = {"Authorization": f"Bearer {CONFIG['token']}"}
        query = f"""
        {{
          queryableGranularities(
            environmentId: "{CONFIG['environment_id']}"
            metrics: [{metric_list}]
          )
        }}
        """
        
        print(f"Executing GraphQL query: {query}")
        
        response = requests.post(
            url, 
            headers=headers,
            json={"query": query}
        )
        
        data = response.json()
        
        if "errors" in data:
            return f"GraphQL error: {data['errors']}"
        
        return json.dumps(data["data"]["queryableGranularities"], indent=2)
    except Exception as e:
        return f"Error getting granularities: {str(e)}"

@mcp.tool()
def query_metrics(metrics, group_by=None, time_grain=None, limit=None):
    """
    Query metrics with optional grouping and filtering
    
    Args:
        metrics: List of metric names or a single metric name
        group_by: Optional list of dimensions to group by or a single dimension
        time_grain: Optional time grain (DAY, WEEK, MONTH, QUARTER, YEAR)
        limit: Optional limit for number of results
    """
    if not CONFIG["is_connected"]:
        return "Not connected. Use connect() first."
    
    try:
        # Ensure metrics is a list
        if isinstance(metrics, str):
            metrics = [metrics]
            
        # Ensure group_by is a list if provided
        if group_by and isinstance(group_by, str):
            group_by = [group_by]
        
        # Generate metric list string for GraphQL
        metric_list = ", ".join([f"{{name: \"{metric}\"}}" for metric in metrics])
        
        # Build group_by section if needed
        group_by_section = ""
        if group_by:
            groups = []
            for dim in group_by:
                if dim == "metric_time" and time_grain:
                    groups.append(f'{{name: "{dim}", grain: {time_grain}}}')
                else:
                    groups.append(f'{{name: "{dim}"}}')
            group_by_section = f"groupBy: [{', '.join(groups)}]"
        
        # Build limit section if needed
        limit_section = f"limit: {limit}" if limit else ""
        
        # Build create query mutation with direct string construction
        mutation = f"""
        mutation {{
          createQuery(
            environmentId: "{CONFIG['environment_id']}"
            metrics: [{metric_list}]
            {group_by_section}
            {limit_section}
          ) {{
            queryId
          }}
        }}
        """
        
        url = f"https://{CONFIG['host']}/api/graphql"
        headers = {"Authorization": f"Bearer {CONFIG['token']}"}
        
        print(f"Executing GraphQL mutation: {mutation}")
        
        # Execute create query mutation
        response = requests.post(
            url,
            headers=headers,
            json={"query": mutation}
        )
        response.raise_for_status()
        create_data = response.json()
        
        if "errors" in create_data:
            return f"GraphQL error: {create_data['errors']}"
        
        # Get query ID
        query_id = create_data["data"]["createQuery"]["queryId"]
        
        # Poll for results
        max_attempts = 30
        attempts = 0
        query_result = None
        
        while attempts < max_attempts:
            attempts += 1
            
            # Query for results
            result_query = f"""
            {{
              query(environmentId: "{CONFIG['environment_id']}", queryId: "{query_id}") {{
                status
                error
                jsonResult(encoded: false)
              }}
            }}
            """
            
            print(f"Polling with query: {result_query}")
            
            response = requests.post(
                url,
                headers=headers,
                json={"query": result_query}
            )
            response.raise_for_status()
            result_data = response.json()
            
            if "errors" in result_data:
                return f"GraphQL error: {result_data['errors']}"
            
            query_result = result_data["data"]["query"]
            
            # Check status
            if query_result["status"] == "FAILED":
                return f"Query failed: {query_result['error']}"
            elif query_result["status"] == "SUCCESSFUL":
                break
            
            # Wait before polling again
            time.sleep(1)
        
        if attempts >= max_attempts:
            return "Query timed out. Please try again or simplify your query."
        
        # Parse and return results
        if query_result["jsonResult"]:
            # Return the raw JSON result
            return query_result["jsonResult"]
        else:
            return "No results returned."
    except Exception as e:
        return f"Error querying metrics: {str(e)}"

if __name__ == "__main__":
    mcp.run()
