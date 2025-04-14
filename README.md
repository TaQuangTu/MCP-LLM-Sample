# MCP with Langchain Sample Setup

## Start MCP servers

There are 3 sample MCP servers created in folder `mcp_servers`, each has 1 or 2 functions. Start and listen for requests on 3 different ports: 8000, 8001, and 8002.

```bash
cd mcp_servers
nohup python math_mcp_server.py > math.log 2>&1 &
nohup python weather_mcp_server.py > weather.log 2>&1 &
nohup python which_llm_to_use_mcp_server.py > which_llm.log 2>&1 &
```

## Start MCP client

MCP client works as an interface bridging users and MCP servers.

```bash
export OPENAI_API_KEY=sk-svcacct-Tn_rKHd............................your_key_please
streamlit run my_chat_bot_app.py
```

The streamlit command will start a web UI listening on port 8501. You can play with the bot from there.
