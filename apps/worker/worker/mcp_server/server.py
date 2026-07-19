import os
import json
import sys
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
import psycopg2
from dotenv import load_dotenv

# Load env variables from the apps/worker/.env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

mcp = FastMCP("doc-intel-tools")

@mcp.tool()
def web_search(query: str, max_results: int = 3) -> str:
    """Search the public web for current information. Returns JSON list of
    {title, url, content} results."""
    try:
        api_key = os.environ.get("TAVILY_API_KEY")
        if not api_key:
            return json.dumps([{"title": "Error", "url": "", "content": "TAVILY_API_KEY not found in environment."}])
        client = TavilyClient(api_key=api_key)
        resp = client.search(query=query, max_results=max_results)
        results = [
            {"title": r["title"], "url": r["url"], "content": r["content"][:800]}
            for r in resp.get("results", [])
        ]
        return json.dumps(results)
    except Exception as e:
        print(f"Error in web_search tool: {e}", file=sys.stderr)
        return json.dumps([{"title": "Error", "url": "", "content": f"Search failed: {str(e)}"}])

@mcp.tool()
def get_job_status(job_id: str) -> str:
    """Look up the ingestion status of a document job by its job id.
    Returns JSON {status, filename, error}."""
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    with conn, conn.cursor() as cur:
        cur.execute("SELECT status, filename, error FROM jobs WHERE id = %s", (job_id,))
        row = cur.fetchone()
    conn.close()
    if not row:
        return json.dumps({"error": "job not found"})
    return json.dumps({"status": row[0], "filename": row[1], "error": row[2]})

if __name__ == "__main__":
    mcp.run()          # default: stdio transport