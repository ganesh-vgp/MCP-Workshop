# MCP Demo - Local LLM Integration

Build an MCP server and connect it to a locally running LLM! This hands-on session will have you creating tools that an AI can use instantly.

## What You'll Build

A complete MCP server with:
- **Calculator tools** - Basic arithmetic operations that AI can use
- **File tools** - Let AI read, write, and manage files  
- **Local LLM client** - Connect to Ollama or any local model
- **Real conversations** - Chat with AI using your custom tools

## Setup Instructions

### 1. Install Dependencies:
```bash
# Core MCP and AI libraries
pip install -r requirements.txt

# Install Ollama (for local LLM)
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.ai/install.sh | sh
# Windows: Download from ollama.ai
```

### 2. Setup Local LLM:
```bash
# Pull a lightweight model (2GB)
ollama pull llama3.2:3b

# Or a more capable model (4GB)
ollama pull llama3.2:7b

# Start Ollama server
ollama serve
```

### 3. Test Your Setup:
```bash
# Test LLM is working
python test_llm.py

# Test MCP server
python server.py

# Full integration test
python chat_with_tools.py
```

## Session Structure

### Part 1: MCP Server Basics
- Build MCP server with calculator tools
- Test tools work correctly

### Part 2: File Operations
- Add file read/write capabilities
- Create file resources for AI access

### Part 3: LLM Integration
- Connect to local Ollama model
- Chat with AI using your custom tools
- See AI use calculator and file operations live!

### Part 4: Advanced Experiments
- Try complex multi-step tasks
- Let AI analyze files and do calculations
- Add your own custom tools

## What Makes This Special

🤖 **Real AI Integration** - Not just API testing, but actual conversations  
🏠 **Fully Local** - No external services, all runs on your machine  
⚡ **Immediate Feedback** - See your tools working with AI instantly  
🔧 **Hands-on Learning** - Build, test, iterate, and experiment

## Files Overview

- `server.py` - Your MCP server implementation (TO COMPLETE)
- `chat_with_tools.py` - Interactive chat with AI using your tools
- `test_llm.py` - Test local LLM connection
- `requirements.txt` - All Python dependencies
- `demo_files/` - Sample files for AI to work with

## Live Demo Flow

1. **Start your MCP server** → `python server.py`
2. **Launch chat interface** → `python chat_with_tools.py`  
3. **Ask AI to do math** → "Calculate 15 * 7 + 23"
4. **Ask AI to read files** → "What's in hello.txt?"
5. **Complex tasks** → "Read numbers.txt, sum them up, and save result to sum.txt"

## Getting Help

- Raise your hand if you get stuck
- Check the comments in `server.py` for guidance
- Try `python test_llm.py` if LLM isn't working
- Look at terminal output for error messages

## Troubleshooting

**Ollama not found?**  
- Install: `brew install ollama` (macOS) or visit ollama.ai
- Start: `ollama serve`

**Model download slow?**  
- Use smaller model: `ollama pull llama3.2:1b`
- Or use any model you already have

**MCP errors?**  
- Check `requirements.txt` installed correctly
- Try demo mode: `python server.py --demo`

Let's build something amazing! 🚀
