import asyncio
from mcp.server.fastmcp import FastMCP

# math_server.py
mcp = FastMCP("Math")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def sub(a: int, b: int) -> int:
    """Substract two numbers"""
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b


if __name__ == "__main__":
    # mcp.run(transport="sse")
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8000
    asyncio.run(mcp.run_sse_async())
