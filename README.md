# 🚀 NEXUS - Next-Generation Super AI Agent

> **Orbital Command** - Your personal multi-model AI agent powered by Ollama

![Version](https://img.shields.io/badge/version-1.0.0-purple)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- 🧠 **Intelligent Model Routing** - Automatically selects the best model for each task
- 🤖 **4 Specialized Models** - Planner, Researcher, Executor, and Coder
- ⚡ **Real-time Streaming** - See responses as they're generated
- 🎨 **Premium UI** - Orbital Command interface with glassmorphism design
- 📊 **System Metrics** - Monitor CPU and memory usage in real-time
- 💬 **Conversation Memory** - Maintains context across messages

## 🧠 Neural Cores (Models)

NEXUS uses intelligent routing to select the optimal model:

| Model | Role | Use Cases |
|-------|------|-----------|
| **Llama3.1:8b** | Core/Planner Brain | Planning, reasoning, orchestration, general tasks |
| **Gemma:7b** | Research/Clarity Brain | Research, explanations, analysis, long context |
| **Mistral:7b** | Fast Execution Brain | Quick responses, simple tasks, chat |
| **Qwen2.5:7b** | Coding Specialist Brain | Code generation, debugging, technical tasks |

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running ([Download here](https://ollama.ai))

### Installation

**1. Clone or download this repository**

**2. Pull required Ollama models:**

```bash
ollama pull llama3.1:8b
ollama pull gemma:7b
ollama pull mistral:7b
ollama pull qwen2.5:7b
```

**3. Install Python dependencies:**

```bash
pip install -r requirements.txt
```

### Running NEXUS

**Start the server:**

```bash
python api.py
```

**Access the UI:**

Open your browser to: **http://localhost:8080/app**

## 📚 API Documentation

Once running, visit **http://localhost:8080/docs** for interactive API documentation.

### Key Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check and Ollama status
- `GET /models` - Available models and their status
- `POST /chat` - Send a message (supports streaming)
- `GET /metrics` - System performance metrics
- `POST /reset` - Reset conversation history

## 🎨 UI Features

### Orbital Command Interface

- **Neural Core Panel** - View all available models and their specializations
- **Live Model Indicator** - See which model is currently active
- **System Metrics Dashboard** - Monitor real-time system performance
- **Markdown Support** - Rich text formatting in responses
- **Code Syntax Highlighting** - Beautiful code blocks
- **Responsive Design** - Works on all screen sizes

### Keyboard Shortcuts

- `Enter` - Send message
- `Shift + Enter` - New line in input

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
nexus:
  name: "NEXUS"
  version: "1.0.0"

ollama:
  base_url: "http://localhost:11434"
  timeout: 120

agents:
  temperature: 0.7
  enable_memory: true
  enable_planning: true

ui:
  theme: "orbital_dark"
  streaming: true
  show_metrics: true
```

## 🔧 Architecture

```
NEXUS/
├── api.py                 # FastAPI backend server
├── config.yaml           # Configuration file
├── requirements.txt      # Python dependencies
├── backend/
│   ├── nexus_core.py     # Core orchestration engine
│   ├── model_router.py   # Intelligent model routing
│   └── tools/
│       └── system_tools.py   # System metrics
└── frontend/
    ├── index.html        # Main UI
    ├── css/
    │   └── orbital.css   # Premium styling
    └── js/
        └── nexus-ui.js   # Frontend logic
```

## 🤝 How It Works

1. **User sends a message** via the web UI
2. **Model Router analyzes intent** using pattern matching
3. **Optimal model is selected** based on task type
4. **Request streams to Ollama** for processing
5. **Response streams back** to the UI in real-time
6. **Conversation is saved** for context

## 🎯 Example Queries

Try these to see different models in action:

- **Planning**: "Create a plan to build a todo app"
- **Code**: "Write a Python function to reverse a string"
- **Research**: "Explain quantum computing in detail"
- **Quick**: "What's the capital of France?"

## 🐛 Troubleshooting

### Ollama not connecting

- Ensure Ollama is running: `ollama serve`
- Check if models are installed: `ollama list`

### Models showing as offline

- Pull the required models (see Quick Start)
- Restart Ollama service

### Port 8080 already in use

Edit `api.py` and change the port in `uvicorn.run()`

## 📊 Performance

- **Response Time**: 1-3 seconds (depends on model)
- **Memory Usage**: ~8-12GB RAM (all models loaded)
- **CPU Usage**: Varies by model complexity

## 🔮 Roadmap

- [ ] Tool integration (file operations, web search)
- [ ] Multi-agent collaboration
- [ ] Long-term memory system
- [ ] Voice input/output
- [ ] Custom model fine-tuning

## 📝 License

MIT License - Feel free to use, modify, and distribute.

## 🙏 Credits

Built with:
- [Ollama](https://ollama.ai) - Local LLM runtime
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [Marked.js](https://marked.js.org/) - Markdown rendering
- [Highlight.js](https://highlightjs.org/) - Code syntax highlighting

---

**NEXUS** - Building clarity, confidence, and skill. 🔥

SIUUUU! 🚀
# Nexus
