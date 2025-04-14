import asyncio
from mcp.server.fastmcp import FastMCP

# math_server.py
mcp = FastMCP("which_llm")


@mcp.tool()
def get_llm_model_name(model_name: str) -> int:
    """Get name of the LLM model, one of:
    - gpt-3.5-turbo: when asked about math
    - gpt-4o-mini: when asked about weather
    """
    return model_name


if __name__ == "__main__":
    # mcp.run(transport="sse")
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8002
    asyncio.run(mcp.run_sse_async())
