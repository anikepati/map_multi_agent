# math_agent_server.py
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

# --- Internal Tools for the Math Agent's LLM ---
@tool
def _add(a: float, b: float) -> float:
    """Adds two numbers."""
    print(f"[MathAgent Internal]: Executing _add: {a} + {b}")
    return a + b

@tool
def _multiply(a: float, b: float) -> float:
    """Multiplies two numbers."""
    print(f"[MathAgent Internal]: Executing _multiply: {a} * {b}")
    return a * b

# --- Initialize the Math Agent's MCP Server ---
mcp_math_agent = FastMCP("MathAgent")

@mcp_math_agent.tool()
async def solve_math_problem(problem: str) -> str:
    """
    Solves a given mathematical problem described in natural language.
    Uses an internal LLM to interpret the problem and apply appropriate math tools.
    """
    print(f"[MathAgent Server]: Received natural language math problem: '{problem}'")

    # Initialize the Math Agent's internal LLM
    math_llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # Define the prompt for the Math Agent's internal LLM
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a specialized mathematical assistant. Use the provided tools to solve math problems. If a problem cannot be solved with the given tools, state that."),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    # Create the Math Agent's internal executor
    internal_tools = [_add, _multiply]
    internal_agent = create_tool_calling_agent(math_llm, internal_tools, prompt)
    internal_agent_executor = AgentExecutor(agent=internal_agent, tools=internal_tools, verbose=True)

    try:
        # Invoke the internal agent with the natural language problem
        result = await internal_agent_executor.ainvoke({"input": problem})
        print(f"[MathAgent Server]: Internal agent result: {result['output']}")
        return result["output"]
    except Exception as e:
        print(f"[MathAgent Server]: Error in internal math agent: {e}")
        return f"Math Agent could not solve the problem: {e}"

async def run_math_agent_server():
    """
    Initializes and runs the Math Agent's MCP server.
    This server exposes the LLM-powered 'solve_math_problem' tool.
    """
    print("[MathAgent Server]: Starting FastMCP MathAgent Server (LLM-powered Math Agent)...")
    await mcp_math_agent.arun(transport="stdio")
    print("[MathAgent Server]: FastMCP MathAgent Server stopped.")

if __name__ == "__main__":
    asyncio.run(run_math_agent_server())