import asyncio
import json
import os
import sys

from dotenv import load_dotenv
from openai import AsyncOpenAI

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables (e.g. OPENAI_API_KEY)
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("OPENAI_API_KEY not found in environment.")
    sys.exit(1)

# Instantiate the asynchronous OpenAI client
openai_client = AsyncOpenAI(api_key=openai_api_key)


def build_system_prompt(functions):
    """
    Build a system prompt listing available tools.
    """
    prompt = (
        "You are a helpful assistant with access to external tools. "
        "When necessary, you should call a function to get real-time data. "
        "Respond naturally while incorporating tool results as needed."
    )
    if functions:
        tool_list = "\n".join([f"- {f['name']}: {f['description']}" for f in functions])
        prompt += "\n\nAvailable tools:\n" + tool_list
    return prompt


class MCPClient:
    """
    MCPClient implements async context management so that all cancellation scopes
    (used internally by stdio_client and ClientSession) are entered and exited within the same task.
    """
    def __init__(self, server_script_path: str):
        self.server_script_path = server_script_path
        self.session = None
        self.stdio = None
        self.write = None
        self._stdio_cm = None  # To hold the stdio_client context

    async def __aenter__(self):
        # Determine the command based on file extension
        if self.server_script_path.endswith('.py'):
            command = "python"
        elif self.server_script_path.endswith('.js'):
            command = "node"
        else:
            raise ValueError("Server script must be a .py or .js file")

        server_params = StdioServerParameters(
            command=command,
            args=[self.server_script_path],
            env=None
        )
        # Enter the stdio_client context in the current task
        self._stdio_cm = stdio_client(server_params)
        self.stdio, self.write = await self._stdio_cm.__aenter__()

        # Create and enter the MCP session context
        session = ClientSession(self.stdio, self.write)
        self.session = await session.__aenter__()
        await self.session.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Exit the MCP session context
        if self.session is not None:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
        # Exit the stdio_client context
        if self._stdio_cm is not None:
            await self._stdio_cm.__aexit__(exc_type, exc_val, exc_tb)

    async def list_tools(self):
        """
        List available tools from the MCP server.
        """
        response = await self.session.list_tools()
        return response.tools

    async def call_tool(self, tool_name: str, tool_args: dict):
        """
        Call the specified tool on the MCP server.
        """
        response = await self.session.call_tool(tool_name, tool_args)
        # Assumes the response content is a list with a 'text' field in its first element.
        return response.content[0].text


async def chat_loop(mcp_client: MCPClient):
    """
    Runs an interactive chat loop with the user.
    """
    # Retrieve available tools from the MCP server
    mcp_tools = await mcp_client.list_tools()

    # Convert MCP tools into a list of function definitions for OpenAI
    functions = []
    for tool in mcp_tools:
        functions.append({
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema  # Must be a valid JSON schema
        })

    # Build the initial system prompt using the available tools
    system_message = {"role": "system", "content": build_system_prompt(functions)}
    messages = [system_message]

    print("Chat session started. Type 'quit' to exit.")

    while True:
        try:
            user_input = input("\nUser: ").strip()
            if user_input.lower() in ["quit", "exit"]:
                break

            messages.append({"role": "user", "content": user_input})

            # Request a completion from GPT with function calling enabled
            response = await openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                functions=functions,
                function_call="auto",
                max_tokens=5000,
                temperature=0.5,
            )

            # Access the message object (ChatCompletionMessage) using attributes
            message = response.choices[0].message

            if message.function_call is not None:
                function_name = message.function_call.name
                arguments = message.function_call.arguments
                try:
                    parsed_args = json.loads(arguments) if arguments else {}
                except json.JSONDecodeError:
                    parsed_args = {}

                print(f"\nAssistant is calling function: {function_name} with arguments: {parsed_args}")

                tool_result = await mcp_client.call_tool(function_name, parsed_args)
                print(f"Tool result: {tool_result}")

                # Append the function call and its result to the conversation
                messages.append({
                    "role": message.role,
                    "content": message.content,
                    "function_call": {
                        "name": function_name,
                        "arguments": arguments
                    }
                })
                messages.append({
                    "role": "function",
                    "name": function_name,
                    "content": tool_result
                })

                # Request a follow-up completion with the tool result included
                followup_response = await openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    max_tokens=5000,
                    temperature=0.5,
                )
                final_reply = followup_response.choices[0].message
                final_content = final_reply.content.strip() if final_reply.content else ""
                print(f"\nAssistant: {final_content}")
                messages.append({
                    "role": final_reply.role,
                    "content": final_reply.content
                })
            else:
                # If no function call, simply output the assistant's reply
                content = message.content.strip() if message.content else ""
                print(f"\nAssistant: {content}")
                messages.append({
                    "role": message.role,
                    "content": message.content
                })
        except Exception as e:
            print(f"Error: {str(e)}")


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    async with MCPClient(sys.argv[1]) as client:
        print("Connected to MCP server!")
        await chat_loop(client)


if __name__ == "__main__":
    asyncio.run(main())
