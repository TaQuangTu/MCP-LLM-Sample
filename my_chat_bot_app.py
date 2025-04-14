# Create server parameters for stdio connection
from dotenv import load_dotenv

load_dotenv()

## For running asyncio
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import SSEConnection
from langchain.schema import HumanMessage

## model for agent
model = ChatOpenAI(model="gpt-4o-mini")


def get_mcp_server_config():
    math_sse_connection = SSEConnection(
        transport="sse",
        url="http://localhost:8000/sse",
        headers=None,
        timeout=10.0,
        sse_read_timeout=10.0,
        session_kwargs=None,
    )
    weather_sse_connection = SSEConnection(
        transport="sse",
        url="http://localhost:8001/sse",
        headers=None,
        timeout=10.0,
        sse_read_timeout=10.0,
        session_kwargs=None,
    )
    which_llm_sse_connection = SSEConnection(
        transport="sse",
        url="http://localhost:8002/sse",
        headers=None,
        timeout=10.0,
        sse_read_timeout=10.0,
        session_kwargs=None,
    )
    server_params = {
        "math": math_sse_connection,
        "weather": weather_sse_connection,
        "which_llm": which_llm_sse_connection,
    }
    return server_params


async def chat(query: str, server_config: dict[str, SSEConnection], history=[]):
    async with MultiServerMCPClient(server_config) as client:
        agent = create_react_agent(
            model,
            client.get_tools(),
            prompt="You are a helpful assistant, your name is Mia. You have to response in Vietnamese even when users are talking in English",
        )
        messages = history + [HumanMessage(content=query)]
        response = await agent.ainvoke({"messages": messages})

    return response


async def main():
    mcp_servers = get_mcp_server_config()

    # ask 1st
    query1 = "what is the weather in Kon Tum, Vietnam?"
    response1 = await chat(query1, mcp_servers)

    # ask 2nd
    query2 = "Da Nang, Vietnam?"
    response2 = await chat(query2, mcp_servers, history=response1["messages"])

    # ask 3rd
    query3 = "What is the latest location i asked you?"
    response3 = await chat(query3, mcp_servers, history=response2["messages"])

    return response3


if __name__ == "__main__":
    response = asyncio.run(main())
    print("------------")
    print(response)
