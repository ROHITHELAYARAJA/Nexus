"""
NEXUS CLI Chatbot
Simple command-line interface to chat with Ollama models
"""

import httpx
import asyncio
import json
import yaml
from pathlib import Path


class NexusChatbot:
    def __init__(self):
        self.ollama_base = "http://localhost:11434"
        self.conversation_history = []
        self.config = self.load_config()
        self.current_model = None
        
    def load_config(self):
        """Load configuration or use defaults"""
        config_path = Path("config.yaml")
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {
            'ollama': {
                'models': {
                    'default': {'name': 'deepseek-v3.1:671b-cloud', 'role': 'Core Intelligence Brain'}
                }
            }
        }
    
    async def check_available_models(self):
        """Check which models are available"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ollama_base}/api/tags", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    return [model['name'] for model in data.get('models', [])]
        except:
            return []
        return []
    
    def get_system_prompt(self):
        """NEXUS personality"""
        return """You are NEXUS, a next-generation Super AI Agent built to operate at the level of ChatGPT and Gemini.

You think like a senior software engineer, AI architect, and systems thinker.
You explain like a world-class teacher.
You communicate like a confident, friendly, human assistant.

Your mission: Deliver clear thinking, correct solutions, and real progress on every task.

Be clear, structured, and professional with a natural, human tone.
Celebrate wins with "SIUUUU 🔥" when appropriate!"""
    
    async def chat(self, user_message: str):
        """Send message and get streaming response"""
        
        # Add user message to history
        self.conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        
        # Prepare messages with system prompt
        messages = [
            {'role': 'system', 'content': self.get_system_prompt()}
        ] + self.conversation_history[-10:]  # Keep last 10 messages
        
        # Stream response
        full_response = ""
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                payload = {
                    'model': self.current_model,
                    'messages': messages,
                    'stream': True
                }
                
                async with client.stream(
                    'POST',
                    f"{self.ollama_base}/api/chat",
                    json=payload
                ) as response:
                    
                    print(f"\n🤖 NEXUS ({self.current_model}):", end=" ", flush=True)
                    
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                chunk = json.loads(line)
                                if 'message' in chunk:
                                    content = chunk['message'].get('content', '')
                                    if content:
                                        print(content, end="", flush=True)
                                        full_response += content
                            except json.JSONDecodeError:
                                continue
                    
                    print("\n")  # New line after response
                    
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            return
        
        # Save assistant response to history
        self.conversation_history.append({
            'role': 'assistant',
            'content': full_response
        })
    
    async def select_model(self, available_models):
        """Skip model selection if only one model is preferred or available"""
        # If we have a default model in config and it's available, just use it
        default_model = self.config['ollama']['models'].get('default', {}).get('name')
        if default_model in available_models:
            return default_model
            
        print("\n🧠 Available Neural Cores:\n")
        
        # Map available models
        model_options = []
        for i, model_name in enumerate(available_models, 1):
            # Find role from config
            role = "AI Model"
            for key, info in self.config['ollama']['models'].items():
                if info.get('name') == model_name:
                    role = info.get('role', key.title())
                    break
            
            print(f"{i}. {model_name} - {role}")
            model_options.append(model_name)
        
        if len(model_options) == 1:
            return model_options[0]

        while True:
            try:
                choice = input("\nSelect model (number): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(model_options):
                    return model_options[idx]
                print("Invalid choice. Try again.")
            except (ValueError, KeyboardInterrupt):
                print("\nExiting...")
                return None
    
    async def run(self):
        """Main chat loop"""
        print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ███╗   ██╗███████╗██╗  ██╗██╗   ██╗███████╗            ║
║   ████╗  ██║██╔════╝╚██╗██╔╝██║   ██║██╔════╝            ║
║   ██╔██╗ ██║█████╗   ╚███╔╝ ██║   ██║███████╗            ║
║   ██║╚██╗██║██╔══╝   ██╔██╗ ██║   ██║╚════██║            ║
║   ██║ ╚████║███████╗██╔╝ ██╗╚██████╔╝███████║            ║
║   ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝            ║
║                                                           ║
║         Next-generation CLI Chatbot                       ║
║              Powered by Ollama                            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
        """)
        
        # Check available models
        print("🔍 Checking Ollama connection...")
        available_models = await self.check_available_models()
        
        if not available_models:
            print("❌ No Ollama models found. Make sure Ollama is running and models are pulled.")
            print("\nTo pull models:")
            print("  ollama pull llama3.1:8b")
            print("  ollama pull gemma:7b")
            print("  ollama pull mistral:7b")
            print("  ollama pull qwen2.5:7b")
            return
        
        # Select model
        self.current_model = await self.select_model(available_models)
        if not self.current_model:
            return
        
        print(f"\n✅ Connected to {self.current_model}")
        print("\nType your message and press Enter. Type 'quit' or 'exit' to stop.\n")
        print("─" * 60)
        
        # Chat loop
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 SIUUUU! See you next time! 🔥\n")
                    break
                
                if user_input.lower() == 'reset':
                    self.conversation_history = []
                    print("\n🔄 Conversation reset!\n")
                    continue
                
                # Get response
                await self.chat(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 SIUUUU! See you next time! 🔥\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


async def main():
    chatbot = NexusChatbot()
    await chatbot.run()


if __name__ == "__main__":
    asyncio.run(main())
