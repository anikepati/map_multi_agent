# Multi-Agent GenAI Application with Model Context Protocol (MCP)
This project demonstrates a sophisticated multi-agent Generative AI application built using LangChain, FastMCP, and OpenAI. It showcases how specialized, LLM-powered agents can collaborate by exposing their capabilities via the Model Context Protocol (MCP), orchestrated by a central Master Agent.

## 🚀 Introduction
In traditional AI applications, LLMs often operate in isolation or rely on tightly integrated tools. The Model Context Protocol (MCP) provides a standardized, open framework for LLMs and AI agents to securely and seamlessly interact with external data sources and tools. This project takes that a step further by demonstrating how MCP enables true Agent-to-Agent (A2A) communication, where individual LLM-powered agents can offer their specialized services to other agents.

## 🧠 Architecture
This application features a modular, decentralized architecture comprising:
Inline-style: 
![alt text](https://github.com/anikepati/mcp_multi_agent/blob/main/mcp_design.png "Design")

Specialized LLM-Powered Agents (MCP Servers):

Math Agent: An independent agent with its own OpenAI LLM "brain" that specializes in solving mathematical problems. It exposes a high-level solve_math_problem tool via a FastMCP server. When invoked, its internal LLM interprets the natural language problem and uses its own internal math functions (_add, _multiply) to find the solution.

Text Agent: Another independent agent with its own OpenAI LLM "brain" focused on text manipulation. It exposes a high-level process_text_request tool via a FastMCP server. Its internal LLM interprets text-related requests and uses internal text functions (_reverse_string, _count_words) to fulfill them.

## Master Orchestrator Agent (LangChain Client):

This is the central control point of the application. It's a LangChain agent powered by an OpenAI LLM.

It acts as an MCP client, connecting to both the Math Agent's and Text Agent's MCP servers.

Its primary role is to interpret user queries and intelligently delegate sub-tasks to the appropriate specialized agent by invoking their high-level MCP tools.

Key Principle: Each specialized agent is truly "agentic" in that it uses its own LLM for internal reasoning to fulfill requests received via MCP, rather than just executing a simple function. This allows for complex, natural language-driven delegation between agents.

## 💡 How It Works
Agent Initialization:

The math_agent_server.py and text_agent_server.py scripts are started as separate processes (or can be deployed independently). Each initializes its own OpenAI LLM and a FastMCP server, exposing a single, natural-language-driven tool.

Orchestrator Connection:

The master_orchestrator_client.py script starts. It uses MultiServerMCPClient to establish connections with both the Math Agent's and Text Agent's MCP servers.

It then loads the high-level tools (solve_math_problem, process_text_request) exposed by these specialized agents.

User Interaction:

When a user provides a query to the Master Orchestrator, its LangChain LLM analyzes the request.

Based on the query's intent (e.g., "calculate...", "reverse...", "count words..."), the Orchestrator's LLM decides which specialized agent's tool to invoke.

Delegation & Internal Reasoning:

The Orchestrator calls the selected specialized agent's MCP tool (e.g., solve_math_problem) with the relevant natural language sub-query.

The specialized agent's MCP server receives this call. Its own internal LLM then takes over, interpreting the sub-query and deciding which of its internal helper functions (e.g., _add, _multiply) to use to generate the result.

Result Return:

The specialized agent returns the processed result back to the Master Orchestrator via MCP.

The Master Orchestrator then presents the final answer to the user.

⚙️ Setup
Clone the repository (or create files):
Create three Python files in the same directory:

math_agent_server.py

text_agent_server.py

master_orchestrator_client.py

Install Dependencies:
Make sure you have Python 3.9+ installed. Then, install the required libraries:

pip install fastmcp langchain langchain-openai langchain-mcp-adapters python-dotenv

Set up OpenAI API Key:
Create a file named .env in the same directory as your Python scripts and add your OpenAI API key:

OPENAI_API_KEY="your_openai_api_key_here"

Important: Replace "your_openai_api_key_here" with your actual OpenAI API key.

▶️ How to Run
To run the multi-agent application, you only need to start the master_orchestrator_client.py script. It will automatically launch the specialized agent servers as subprocesses.

Open your terminal and execute:

python master_orchestrator_client.py

### 💬 Usage
Once the master_orchestrator_client.py is running, you'll see a prompt asking for your input. Try the following types of queries:

#### Mathematical Queries (handled by Math Agent):

Calculate the product of 12 and 5

What is 78 plus 33?

Can you add 10.5 and 20.3?

####  Text Processing Queries (handled by Text Agent):

How many words are in the phrase 'hello world, this is a test'?

Please reverse the sentence 'Python is fun'

Count the words in 'Artificial Intelligence is transforming the world'

The console output will show the delegation process, including messages from the Orchestrator Client and the respective specialized agent servers, demonstrating the agent-to-agent communication and internal LLM reasoning.

To exit the application, simply type quit and press Enter.
