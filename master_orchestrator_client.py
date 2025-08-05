# master_orchestrator_client.py
import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain.schema import HumanMessage, AIMessage

# Load environment variables
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable not set.")

async def run_master_orchestrator_agent():
    """
    Initializes the Master Orchestrator Agent, connects to specialized agent servers,
    loads their LLM-powered tools, and orchestrates interactions.
    """
    print("[Orchestrator Client]: Initializing Master Orchestrator LangChain Client...")

    # Initialize the OpenAI Chat Model for the Orchestrator
    orchestrator_llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # Initialize the MultiServerMCPClient to connect to both specialized agent servers
    mcp_client = MultiServerMCPClient(
        server_configs=[
            {
                "name": "MathAgent",
                "transport": "stdio",
                "command": ["python", "math_agent_server.py"] # Command to start MathAgent server
            },
            {
                "name": "TextAgent",
                "transport": "stdio",
                "command": ["python", "text_agent_server.py"] # Command to start TextAgent server
            }
        ]
    )

    # Establish connections and load tools from all configured specialized agent servers
    print("[Orchestrator Client]: Connecting to specialized agent servers and loading tools...")
    await mcp_client.ainitialize()
    tools = await mcp_client.aload_tools()

    if not tools:
        print("[Orchestrator Client]: No tools loaded from specialized agent servers. Exiting.")
        return

    print(f"[Orchestrator Client]: Loaded tools from all specialized agents: {[tool.name for tool in tools]}")

    # Create the Master Orchestrator LangChain ReAct agent with all loaded tools
    # The orchestrator's LLM will decide which specialized agent's LLM-powered tool to use
    master_agent = create_react_agent(orchestrator_llm, tools)

    print("\n[Orchestrator Client]: Master Orchestrator Agent ready! Type your query or 'quit' to exit.")
    print("Try queries like: 'Calculate the product of 12 and 5', 'How many words are in 'hello world'?', 'Can you add 78 and 33?', 'Please reverse the phrase 'Python is fun''")

    while True:
        user_query = input("\nUser: ").strip()
        if user_query.lower() == "quit":
            print("[Orchestrator Client]: Exiting Master Orchestrator Agent. Goodbye!")
            break

        print(f"[Orchestrator Client]: Orchestrator processing: '{user_query}'...")
        try:
            result = await master_agent.ainvoke({"messages": [HumanMessage(content=user_query)]})

            if "output" in result:
                print(f"[Orchestrator Client]: Orchestrator Response: {result['output']}")
            elif "messages" in result and result["messages"]:
                last_message = result["messages"][-1]
                if isinstance(last_message, AIMessage):
                    print(f"[Orchestrator Client]: Orchestrator Response: {last_message.content}")
                else:
                    print(f"[Orchestrator Client]: Orchestrator Response: {last_message.content}")
            else:
                print("[Orchestrator Client]: Orchestrator Response: No discernible output.")

        except Exception as e:
            print(f"[Orchestrator Client]: An error occurred: {e}")

    # Ensure all MCP client connections are properly shut down
    await mcp_client.ashutdown()

if __name__ == "__main__":
    asyncio.run(run_master_orchestrator_agent())