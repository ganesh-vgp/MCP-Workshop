#!/usr/bin/env python3
"""
Test Local LLM Connection
Verifies that Ollama is running and a model is available for the MCP demo.
"""

import asyncio
import json
import sys
from pathlib import Path

try:
    import ollama
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False
    print("⚠️  Dependencies not installed. Run: pip install -r requirements.txt")

console = Console()

async def test_ollama_connection():
    """Test if Ollama is running and accessible"""
    console.print("\n🔌 Testing Ollama Connection...", style="blue bold")
    
    try:
        # Check if Ollama is running
        client = ollama.Client()
        models = client.list()
        
        if not models or not models.get('models'):
            console.print("❌ No models found in Ollama", style="red")
            console.print("💡 Install a model: ollama pull llama3.2:3b", style="yellow")
            return False
        
        console.print("✅ Ollama is running", style="green")
        
        # List available models
        console.print("\n📋 Available Models:", style="blue")
        for model in models['models']:
            name = model['model']
            size = model.get('size', 0) // (1024*1024*1024)  # Convert to GB
            console.print(f"  • {name} ({size}GB)", style="cyan")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Ollama connection failed: {e}", style="red")
        console.print("💡 Make sure Ollama is installed and running:", style="yellow")
        console.print("   1. Install: brew install ollama", style="yellow")
        console.print("   2. Start: ollama serve", style="yellow")
        console.print("   3. Pull model: ollama pull llama3.2:3b", style="yellow")
        return False

async def test_model_response():
    """Test if the model can respond to a simple query"""
    console.print("\n🧠 Testing Model Response...", style="blue bold")
    
    try:
        client = ollama.Client()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Asking model a test question...", total=None)
            
            response = client.chat(
                model='llama3.2:3b',  # Default model for demo
                messages=[{
                    'role': 'user',
                    'content': 'Hello! Please respond with just "Hello from Ollama!" to confirm you are working.'
                }]
            )
            
            progress.stop()
        
        model_response = response['message']['content'].strip()
        console.print(f"✅ Model Response: {model_response}", style="green")
        
        # Test if model understands tool concepts
        console.print("\n🔧 Testing Tool Understanding...", style="blue")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Testing tool concept understanding...", total=None)
            
            tool_test = client.chat(
                model='llama3.2:3b',
                messages=[{
                    'role': 'user', 
                    'content': 'I will give you access to a calculator tool. When I ask you to calculate 5+3, you should use the tool. Do you understand? Just say "I understand tools."'
                }]
            )
            
            progress.stop()
        
        tool_response = tool_test['message']['content'].strip()
        console.print(f"✅ Tool Understanding: {tool_response}", style="green")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Model test failed: {e}", style="red")
        
        # Try fallback models
        fallback_models = ['llama3.2:1b', 'llama3.1:8b', 'phi3:mini']
        console.print("\n🔄 Trying fallback models...", style="yellow")
        
        for model in fallback_models:
            try:
                client.chat(
                    model=model,
                    messages=[{'role': 'user', 'content': 'Hello'}]
                )
                console.print(f"✅ {model} is working!", style="green")
                return True
            except:
                console.print(f"❌ {model} not available", style="red")
        
        return False

def check_demo_files():
    """Verify demo files exist for the session"""
    console.print("\n📁 Checking Demo Files...", style="blue bold")
    
    demo_dir = Path("demo_files")
    if not demo_dir.exists():
        console.print("❌ demo_files directory missing", style="red")
        return False
    
    expected_files = ["hello.txt", "numbers.txt", "readme.md"]
    missing_files = []
    
    for file in expected_files:
        file_path = demo_dir / file
        if file_path.exists():
            console.print(f"  ✅ {file}", style="green")
        else:
            console.print(f"  ❌ {file} missing", style="red")
            missing_files.append(file)
    
    if missing_files:
        console.print(f"💡 Creating missing files...", style="yellow")
        demo_dir.mkdir(exist_ok=True)
        
        # Create missing files
        if "hello.txt" in missing_files:
            (demo_dir / "hello.txt").write_text("Hello, World! This is a test file for the MCP demo.")
        
        if "numbers.txt" in missing_files:
            (demo_dir / "numbers.txt").write_text("1\n2\n3\n4\n5\n6\n7\n8\n9\n10")
        
        if "readme.md" in missing_files:
            (demo_dir / "readme.md").write_text("# Demo Files\n\nTest files for MCP demo session.")
        
        console.print("✅ Demo files created", style="green")
    
    return True

async def main():
    """Run all tests to verify setup is ready"""
    console.print(Panel.fit(
        "🧪 MCP Demo - Local LLM Setup Test",
        title="Setup Verification",
        border_style="blue"
    ))
    
    if not DEPS_AVAILABLE:
        return
    
    # Run tests
    tests = [
        ("Ollama Connection", test_ollama_connection()),
        ("Model Response", test_model_response()),
        ("Demo Files", check_demo_files()),
    ]
    
    results = []
    for test_name, test_coro in tests:
        if asyncio.iscoroutine(test_coro):
            result = await test_coro
        else:
            result = test_coro
        results.append((test_name, result))
    
    # Summary
    console.print("\n" + "="*50, style="blue")
    console.print("📊 Setup Summary:", style="blue bold")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        style = "green" if passed else "red"
        console.print(f"  {status} {test_name}", style=style)
        if not passed:
            all_passed = False
    
    console.print("\n" + "="*50, style="blue")
    
    if all_passed:
        console.print(Panel.fit(
            "🎉 All tests passed! Ready for MCP demo session.\n\n" +
            "Next steps:\n" +
            "1. python server.py (start your MCP server)\n" +
            "2. python chat_with_tools.py (chat with AI using tools)",
            title="✅ Setup Complete",
            border_style="green"
        ))
    else:
        console.print(Panel.fit(
            "⚠️  Some tests failed. Check the errors above.\n\n" +
            "Common fixes:\n" +
            "• ollama serve (start Ollama)\n" +
            "• ollama pull llama3.2:3b (install model)\n" +
            "• pip install -r requirements.txt (install deps)",
            title="❌ Setup Issues",
            border_style="red"
        ))

if __name__ == "__main__":
    if DEPS_AVAILABLE:
        asyncio.run(main())
    else:
        print("Install requirements first: pip install -r requirements.txt")
        sys.exit(1)
