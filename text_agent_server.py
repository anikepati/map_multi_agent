# text_agent_server.py
import asyncio
import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from fastmcp import FastMCP

# Load environment variables
load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY environment variable not set.")

# --- Internal Tools for the Text Agent's LLM ---
@tool
def _reverse_string(text: str) -> str:
    """Reverses a given string."""
    print(f"[TextAgent Internal]: Executing _reverse_string: '{text}'")
    return text[::-1]

@tool
def _count_words(text: str) -> int:
    """Counts the number of words in a given string."""
    print(f"[TextAgent Internal]: Executing _count_words: '{text}'")
    return len(text.split())

# --- Initialize the Text Agent's MCP Server ---
mcp_text_agent = FastMCP("TextAgent")

@mcp_text_agent.tool()
async def process_text_request(request: str) -> str:
    """
    Processes a given text request described in natural language.
    Uses an internal LLM to interpret the request and apply appropriate text tools.
    """
    print(f"[TextAgent Server]: Received natural language text request: '{request}'")

    # Initialize the Text Agent's internal LLM
    text_llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # Define the prompt for the Text Agent's internal LLM
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a specialized text processing assistant. Use the provided tools to fulfill text manipulation requests. If a request cannot be fulfilled with the given tools, state that."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    # Create the Text Agent's internal executor
    internal_tools = [_reverse_string, _count_words]
    internal_agent = create_tool_calling_agent(text_llm, internal_tools, prompt)
    internal_agent_executor = AgentExecutor(agent=internal_agent, tools=internal_tools, verbose=True)

    try:
        # Invoke the internal agent with the natural language request
        result = await internal_agent_executor.ainvoke({"input": request})
        print(f"[TextAgent Server]: Internal agent result: {result['output']}")
        return result["output"]
    except Exception as e:
        print(f"[TextAgent Server]: Error in internal text agent: {e}")
        return f"Text Agent could not process the request: {e}"

async def run_text_agent_server():
    """
    Initializes and runs the Text Agent's MCP server.
    This server exposes the LLM-powered 'process_text_request' tool.
    """
    print("[TextAgent Server]: Starting FastMCP TextAgent Server (LLM-powered Text Agent)...")
    await mcp_text_agent.arun(transport="stdio")
    print("[TextAgent Server]: FastMCP TextAgent Server stopped.")

if __name__ == "__main__":
    asyncio.run(run_text_agent_server())