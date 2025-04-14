import streamlit as st
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient, SSEConnection
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(page_title="MCP Agent Demo", page_icon="🤖", layout="centered")


# Model for agent
@st.cache_resource
def get_model(name: str = "gpt-4o-mini"):
    return ChatOpenAI(model=name)


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


async def chat(query: str, history=[]):

    all_server_config = get_mcp_server_config()

    # main server config
    main_server_config = {
        "math": all_server_config["math"],
        "weather": all_server_config["weather"],
    }

    # model selector config
    model_selector_config = {
        "which_llm": all_server_config["which_llm"],
    }

    best_model_to_do_a_task = "gpt-4o-mini"
    async with MultiServerMCPClient(model_selector_config) as client:
        model = get_model("gpt-4o-mini")
        agent = create_react_agent(
            model,
            client.get_tools(),
            prompt="Help me select which model to use",
        )
        # TODO: for better model selection, maintain the a separate history for model selection agent
        response = await agent.ainvoke({"messages": query})

        # TODO: parse the response to get the best model to do a task, now hard code to use gpt-4o-mini
        best_model_to_do_a_task = "gpt-4o-mini"

    async with MultiServerMCPClient(main_server_config) as client:
        model = get_model(best_model_to_do_a_task)
        agent = create_react_agent(
            model,
            client.get_tools(),
            prompt="You are a helpful assistant, your name is Mia. You have to response in Vietnamese even when users are talking in English",
        )

        messages = history + [HumanMessage(content=query)]
        response = await agent.ainvoke({"messages": messages})

    return response


# Helper function to extract the last AI message from the response
def extract_assistant_response(response):
    # If we have direct access to the messages key
    if "messages" in response:
        messages = response["messages"]
        # Find the last AI message
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                return msg.content

    # If response itself is an AIMessage
    if isinstance(response, AIMessage):
        return response.content

    # If response is the entire agent output, try to find output or response keys
    if isinstance(response, dict):
        # Debug: Print response keys to console
        st.sidebar.write("Response keys:", list(response.keys()))

        # Try different possible keys
        if "output" in response:
            return response["output"]
        if "response" in response:
            return response["response"]
        if "result" in response:
            return response["result"]

        # Look at all string values in response dict
        for key, value in response.items():
            if (
                isinstance(value, str) and len(value) > 10
            ):  # Assume a reasonably long string might be the response
                return value

    # If nothing found, return the entire response as string
    return str(response)


# App title
st.title("MCP Agent Demo")
st.subheader("Chat with Mia - The Assistant in Vietnamese")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Server status indicators
st.sidebar.title("Server Status")
col1, col2, col3 = st.sidebar.columns(3)

# Check if servers are running (simplified status check)
try:
    server_config = get_mcp_server_config()
    math_status = "✅"
    weather_status = "✅"
    which_llm_status = "✅"
except Exception:
    math_status = "❌"
    weather_status = "❌"
    which_llm_status = "❌"

col1.metric("Math Server", math_status)
col2.metric("Weather Server", weather_status)
col3.metric("LLM Server", which_llm_status)

st.sidebar.warning(
    "Make sure all MCP servers are running:\n```\npython math_mcp_server.py\npython weather_mcp_server.py\npython which_llm_to_use_mcp_server.py\n```"
)

# Add a debug toggle
if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False

st.sidebar.checkbox("Debug Mode", key="debug_mode")

# Chat input
query = st.chat_input("Ask something...")

if query:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": query})

    # Display user message
    with st.chat_message("user"):
        st.write(query)

    # Display assistant response with a spinner
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Convert session messages to langchain format
            history = []
            for msg in st.session_state.messages[:-1]:  # Exclude the current query
                if msg["role"] == "user":
                    history.append(HumanMessage(content=msg["content"]))
                else:
                    history.append(AIMessage(content=msg["content"]))

            # Get response
            response = asyncio.run(chat(query, history))

            # Show raw response in debug mode
            if st.session_state.debug_mode:
                st.write("Raw response:")
                st.write(response)

            # Extract the assistant's message
            assistant_response = extract_assistant_response(response)

            # Display response
            st.write(assistant_response)

    # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_response}
    )

# Clear chat button
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.experimental_rerun()

# Instructions
st.sidebar.markdown("### Example Questions")
st.sidebar.markdown("- What is the weather in Hanoi, Vietnam?")
st.sidebar.markdown("- Can you solve 45 + 67 * 3?")
st.sidebar.markdown("- Which LLM should I use for code generation?")
