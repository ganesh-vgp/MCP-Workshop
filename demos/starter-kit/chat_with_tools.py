#!/usr/bin/env python3
"""
Interactive Chat with Local LLM + MCP Tools
This is the main demo interface where everyone chats with AI using their custom tools.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Any

try:
    import ollama
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.markdown import Markdown
    from rich.live import Live
    from rich.spinner import Spinner
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False
    print("⚠️  Dependencies not installed. Run: pip install -r requirements.txt")

console = Console()

class MCPToolChat:
    """Chat interface that connects Ollama to MCP tools"""
    
    def __init__(self, model_name="llama3.2:3b"):
        self.model_name = model_name
        self.client = None
        self.conversation = []
        self.tools = {}
        self.setup_tools()
    
    def setup_tools(self):
        """Define the tools that will be available to the AI"""
        self.tools = {
            "calculator": {
                "add": self.tool_add,
                "subtract": self.tool_subtract,
                "multiply": self.tool_multiply,
                "divide": self.tool_divide,
            },
            "file_ops": {
                "read_file": self.tool_read_file,
                "write_file": self.tool_write_file,
                "list_files": self.tool_list_files,
            }
        }
    
    async def initialize(self):
        """Initialize the Ollama client and verify connection"""
        try:
            self.client = ollama.Client()
            
            # Test connection
            models = self.client.list()
            if not models or not models.get('models'):
                raise Exception("No models available in Ollama")
            
            # Check if our preferred model exists
            available_models = [m['model'] for m in models['models']]
            if self.model_name not in available_models:
                # Use first available model
                self.model_name = available_models[0]
                console.print(f"ℹ️  Using model: {self.model_name}", style="yellow")
            
            return True
            
        except Exception as e:
            console.print(f"❌ Failed to initialize Ollama: {e}", style="red")
            return False
    
    def create_system_prompt(self):
        """Create system prompt that teaches the AI about available tools"""
        return """You are an AI assistant with access to powerful tools. You can:

CALCULATOR TOOLS:
- add(a, b) - Add two numbers
- subtract(a, b) - Subtract b from a  
- multiply(a, b) - Multiply two numbers
- divide(a, b) - Divide a by b

FILE TOOLS:
- read_file(filename) - Read contents of a file
- write_file(filename, content) - Write content to a file
- list_files() - List all available files

When you need to use a tool, format it exactly like this:
TOOL_CALL: tool_name(param1=value1, param2=value2)

Examples:
- To calculate: TOOL_CALL: add(a=5, b=3)
- To read a file: TOOL_CALL: read_file(filename="hello.txt")
- To write a file: TOOL_CALL: write_file(filename="result.txt", content="The answer is 42")

Always use TOOL_CALL: exactly as shown. Be helpful and use tools when appropriate!"""

    def parse_tool_calls(self, text: str) -> List[Dict]:
        """Extract tool calls from AI response"""
        tool_calls = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('TOOL_CALL:'):
                try:
                    # Extract tool call: TOOL_CALL: add(a=5, b=3)
                    call_part = line.replace('TOOL_CALL:', '').strip()
                    
                    # Parse function name and params
                    if '(' in call_part and ')' in call_part:
                        func_name = call_part.split('(')[0].strip()
                        params_str = call_part.split('(')[1].split(')')[0]
                        
                        # Parse parameters
                        params = {}
                        if params_str.strip():
                            for param in params_str.split(','):
                                param = param.strip()
                                if '=' in param:
                                    key, value = param.split('=', 1)
                                    key = key.strip()
                                    value = value.strip().strip('"\'')
                                    
                                    # Try to convert to number if possible
                                    try:
                                        if '.' in value:
                                            params[key] = float(value)
                                        else:
                                            params[key] = int(value)
                                    except ValueError:
                                        params[key] = value
                        
                        tool_calls.append({
                            'function': func_name,
                            'parameters': params
                        })
                        
                except Exception as e:
                    console.print(f"⚠️  Failed to parse tool call: {line}", style="yellow")
        
        return tool_calls

    async def execute_tool(self, func_name: str, params: Dict) -> str:
        """Execute a tool function and return the result"""
        try:
            # Find the tool
            tool_func = None
            for category, tools in self.tools.items():
                if func_name in tools:
                    tool_func = tools[func_name]
                    break
            
            if not tool_func:
                return f"❌ Unknown tool: {func_name}"
            
            # Execute the tool
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(**params)
            else:
                result = tool_func(**params)
            
            return f"✅ {func_name} result: {result}"
            
        except Exception as e:
            return f"❌ Tool {func_name} failed: {str(e)}"

    # Tool implementations
    def tool_add(self, a: float, b: float) -> float:
        return a + b
    
    def tool_subtract(self, a: float, b: float) -> float:
        return a - b
    
    def tool_multiply(self, a: float, b: float) -> float:
        return a * b
    
    def tool_divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Division by zero")
        return a / b
    
    def tool_read_file(self, filename: str) -> str:
        file_path = Path("demo_files") / filename
        if not file_path.exists():
            raise FileNotFoundError(f"File {filename} not found")
        return file_path.read_text()
    
    def tool_write_file(self, filename: str, content: str) -> str:
        file_path = Path("demo_files") / filename
        file_path.parent.mkdir(exist_ok=True)
        file_path.write_text(content)
        return f"Wrote {len(content)} characters to {filename}"
    
    def tool_list_files(self) -> str:
        demo_dir = Path("demo_files")
        if not demo_dir.exists():
            return "No demo_files directory found"
        
        files = [f.name for f in demo_dir.glob("*") if f.is_file()]
        if not files:
            return "No files found"
        
        return "Files: " + ", ".join(files)

    async def chat_turn(self, user_input: str) -> str:
        """Process one turn of conversation with tool support"""
        
        # Add user message to conversation
        self.conversation.append({
            'role': 'user',
            'content': user_input
        })
        
        # Get AI response
        messages = [
            {'role': 'system', 'content': self.create_system_prompt()}
        ] + self.conversation
        
        try:
            with console.status("[bold blue]🤔 AI is thinking...", spinner="dots"):
                response = self.client.chat(
                    model=self.model_name,
                    messages=messages
                )
            
            ai_response = response['message']['content']
            
            # Check for tool calls
            tool_calls = self.parse_tool_calls(ai_response)
            
            if tool_calls:
                console.print("🔧 AI wants to use tools:", style="blue")
                
                # Execute each tool call
                tool_results = []
                for call in tool_calls:
                    func_name = call['function']
                    params = call['parameters']
                    
                    console.print(f"  → {func_name}({params})", style="cyan")
                    
                    result = await self.execute_tool(func_name, params)
                    tool_results.append(result)
                    console.print(f"    {result}", style="green")
                
                # Add tool results to conversation and get final response
                tool_summary = "\n".join(tool_results)
                follow_up_message = f"Tool execution results:\n{tool_summary}\n\nPlease provide a natural response to the user based on these results."
                
                self.conversation.append({
                    'role': 'assistant',
                    'content': ai_response
                })
                self.conversation.append({
                    'role': 'user', 
                    'content': follow_up_message
                })
                
                # Get final response
                with console.status("[bold blue]🤔 AI is processing results...", spinner="dots"):
                    final_response = self.client.chat(
                        model=self.model_name,
                        messages=[
                            {'role': 'system', 'content': self.create_system_prompt()}
                        ] + self.conversation
                    )
                
                final_ai_response = final_response['message']['content']
                self.conversation.append({
                    'role': 'assistant',
                    'content': final_ai_response
                })
                
                return final_ai_response
            
            else:
                # No tools needed, just return the response
                self.conversation.append({
                    'role': 'assistant',
                    'content': ai_response
                })
                return ai_response
                
        except Exception as e:
            error_msg = f"❌ Error during chat: {str(e)}"
            console.print(error_msg, style="red")
            return error_msg

async def main():
    """Main chat loop"""
    if not DEPS_AVAILABLE:
        console.print("❌ Please install dependencies: pip install -r requirements.txt", style="red")
        return
    
    console.print(Panel.fit(
        "🤖 MCP Demo - Chat with AI + Tools\n\n" +
        "Your AI assistant has access to:\n" +
        "• Calculator (add, subtract, multiply, divide)\n" +
        "• File operations (read, write, list)\n" +
        "• Demo files in demo_files/ directory\n\n" +
        "Try asking: 'Calculate 15 * 7 + 23' or 'What's in hello.txt?'",
        title="🚀 Interactive AI Chat",
        border_style="blue"
    ))
    
    # Initialize chat system
    chat = MCPToolChat()
    
    if not await chat.initialize():
        console.print("❌ Failed to initialize. Check that Ollama is running!", style="red")
        console.print("💡 Run: ollama serve", style="yellow")
        return
    
    console.print(f"✅ Connected to {chat.model_name}", style="green")
    console.print("💬 Start chatting! (type 'quit' to exit)\n", style="blue")
    
    # Example prompts
    examples = [
        "Calculate 25 * 4 + 100",
        "Read hello.txt and tell me what it says",
        "List all files, then read numbers.txt and sum the numbers",
        "Write a file called 'greeting.txt' with 'Hello from AI!'",
        "What's 123 + 456? Then save the result to math_result.txt"
    ]
    
    console.print("💡 Try these examples:", style="yellow")
    for i, example in enumerate(examples, 1):
        console.print(f"  {i}. {example}", style="cyan")
    console.print()
    
    # Main chat loop
    while True:
        try:
            user_input = Prompt.ask("[bold blue]You")
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                console.print("👋 Goodbye!", style="green")
                break
            
            if not user_input.strip():
                continue
            
            # Get AI response
            ai_response = await chat.chat_turn(user_input)
            
            # Display response
            console.print(Panel(
                Markdown(ai_response),
                title="🤖 AI Assistant",
                border_style="green"
            ))
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n👋 Chat ended. Goodbye!", style="green")
            break
        except Exception as e:
            console.print(f"❌ Error: {e}", style="red")

if __name__ == "__main__":
    if DEPS_AVAILABLE:
        asyncio.run(main())
    else:
        print("Install requirements first: pip install -r requirements.txt")
