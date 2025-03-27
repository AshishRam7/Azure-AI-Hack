import asyncio
import inspect
import types
from mcp.client import ClientSession, StdioServerParameters
from pydantic_ai import Agent, Tool

# --- Simulated Helpers for Demonstration ---

# A simple helper that converts a tool's schema (a dict of parameter names to types)
# into a list of inspect.Parameter objects.
def convert_schema_to_params(schema: dict):
    parameters = []
    for param_name, param_type in schema.items():
        param = inspect.Parameter(
            name=param_name,
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=param_type
        )
        parameters.append(param)
    return parameters

# Simulated TextContent class (in your actual code this would come from the MCP SDK)
class TextContent:
    def __init__(self, text: str):
        self.text = text

# --- Core Functions for Converting MCP Tools ---

def create_function_from_schema(session: ClientSession, name: str, schema: dict) -> types.FunctionType:
    # Convert the MCP tool's JSON schema into a list of parameters.
    parameters = convert_schema_to_params(schema)
    sig = inspect.Signature(parameters=parameters)
    
    # Define an async function that, when called, sends the arguments to the MCP server.
    async def function_body(ctx, **kwargs) -> str:
        # Call the MCP tool using the session.
        result = await session.call_tool(name, arguments=kwargs)
        # Here, we assume the result has a 'content' attribute that's a list,
        # and that the first element is an instance of TextContent.
        if result.content and isinstance(result.content[0], TextContent):
            return result.content[0].text
        else:
            raise ValueError("Expected TextContent, got ", type(result.content[0]) if result.content else None)
    
    # Create a dynamic function with the proper signature.
    dynamic_function = types.FunctionType(
        function_body.__code__,
        function_body.__globals__,
        name=name,
        argdefs=function_body.__defaults__,
        closure=function_body.__closure__,
    )
    dynamic_function.__signature__ = sig
    dynamic_function.__annotations__ = {param.name: param.annotation for param in parameters}
    return dynamic_function

def pydantic_tool_from_mcp_tool(session: ClientSession, tool: dict) -> Tool:
    """
    Convert an MCP tool definition (provided as a dict with keys 'name', 'description', and 'inputSchema')
    into a PydanticAI Tool.
    """
    tool_function = create_function_from_schema(session, tool['name'], tool.get('inputSchema', {}))
    return Tool(
        name=tool['name'],
        description=tool['description'],
        function=tool_function,
        takes_ctx=True  # Indicates that the tool function accepts context if needed.
    )

# --- Main Integration Example ---

async def main():
    # Configure the MCP server parameters.
    # (Adjust 'command' and 'args' to match your MCP server implementation.)
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )
    
    # Connect to the MCP server.
    async with ClientSession(server_params) as session:
        # Retrieve a list of available tools from the MCP server.
        tools_result = await session.list_tools()
        # Assume that tools_result.tools is a list of tool definitions (each a dict).
        mcp_tools = tools_result.tools
        
        # Convert each MCP tool into a PydanticAI tool.
        ai_tools = [pydantic_tool_from_mcp_tool(session, tool) for tool in mcp_tools]
        
        # Create a PydanticAI agent and register the MCP-derived tools.
        agent = Agent(
            model="openai:gpt-4",
            system_prompt="You are an AI assistant that can call MCP tools to help answer queries.",
            tools=ai_tools
        )
        
        # Example conversation: Ask the agent to list recent emails.
        user_input = "List the recent emails in my inbox."
        result = await agent.run(user_input)
        print("Agent response:", result.data)

if __name__ == "__main__":
    asyncio.run(main())
