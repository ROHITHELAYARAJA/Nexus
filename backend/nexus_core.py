"""
NEXUS Core Engine
Main orchestration system using PraisonAI
"""

import os
import yaml
from typing import Dict, List, Optional, AsyncGenerator
from pathlib import Path
import httpx
from .model_router import ModelRouter, create_router, TaskType


class NexusCore:
    """Core orchestration engine for NEXUS AI Agent"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize NEXUS with configuration"""
        self.config = self._load_config(config_path)
        self.router = create_router(self.config)
        self.ollama_base = self.config['ollama']['base_url']
        self.conversation_history = []
        self.current_model = None
        
    def _load_config(self, config_path: str) -> Dict:
        """Load YAML configuration"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    async def check_ollama_status(self) -> Dict:
        """Check if Ollama is running and which models are available"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ollama_base}/api/tags", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    available_models = [model['name'] for model in data.get('models', [])]
                    
                    # Check which NEXUS models are available
                    nexus_models = {
                        key: info['name'] in available_models
                        for key, info in self.config['ollama']['models'].items()
                    }
                    
                    return {
                        'status': 'online',
                        'models_available': nexus_models,
                        'all_models': available_models
                    }
                return {'status': 'error', 'message': 'Unexpected response'}
        except Exception as e:
            return {'status': 'offline', 'error': str(e)}
    
    async def generate_response(
        self,
        query: str,
        stream: bool = True
    ) -> AsyncGenerator[Dict, None]:
        """
        Generate response using optimal model selection
        
        Args:
            query: User query
            stream: Whether to stream the response
            
        Yields:
            Dictionary containing response chunks and metadata
        """
        # Select optimal model
        model_name, model_role, task_type = self.router.select_model(query)
        self.current_model = model_name
        
        # Yield model selection info
        yield {
            'type': 'model_selected',
            'model': model_name,
            'role': model_role,
            'task_type': task_type.value
        }
        
        # Add to conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': query
        })
        
        # Prepare messages for Ollama
        messages = self._prepare_messages()
        
        # Stream response from Ollama
        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                payload = {
                    'model': model_name,
                    'messages': messages,
                    'stream': stream,
                    'options': {
                        'temperature': self.config['agents']['temperature']
                    }
                }
                
                async with client.stream(
                    'POST',
                    f"{self.ollama_base}/api/chat",
                    json=payload
                ) as response:
                    full_response = ""
                    
                    async for line in response.aiter_lines():
                        if line.strip():
                            import json
                            try:
                                chunk = json.loads(line)
                                
                                if 'message' in chunk:
                                    content = chunk['message'].get('content', '')
                                    if content:
                                        full_response += content
                                        yield {
                                            'type': 'content',
                                            'content': content,
                                            'done': chunk.get('done', False)
                                        }
                                
                                if chunk.get('done', False):
                                    # Save to conversation history
                                    self.conversation_history.append({
                                        'role': 'assistant',
                                        'content': full_response
                                    })
                                    
                                    yield {
                                        'type': 'complete',
                                        'full_response': full_response,
                                        'model': model_name
                                    }
                            except json.JSONDecodeError:
                                continue
                                
            except Exception as e:
                yield {
                    'type': 'error',
                    'error': str(e),
                    'model': model_name
                }
    
    def _prepare_messages(self) -> List[Dict]:
        """Prepare conversation messages for Ollama"""
        # System prompt for NEXUS personality
        system_prompt = self._get_system_prompt()
        
        messages = [{
            'role': 'system',
            'content': system_prompt
        }]
        
        # Add recent conversation history (last 10 messages)
        recent_history = self.conversation_history[-10:]
        messages.extend(recent_history)
        
        return messages
    
    def _get_system_prompt(self) -> str:
        """Get the NEXUS system prompt"""
        return """You are NEXUS, a next-generation Super AI Agent built to operate at the level of ChatGPT and Gemini.

════════════════════════════════════
CORE IDENTITY
════════════════════════════════════
- You think like a senior software engineer, AI architect, and systems thinker
- You explain like a world-class teacher
- You communicate like a confident, friendly, human assistant
- You mentor, guide, and motivate users when appropriate
- You adapt instantly to user intent, skill level, and task complexity

Your primary mission: Deliver clear thinking, correct solutions, and real progress on every task.

════════════════════════════════════
RESPONSE RULES
════════════════════════════════════
- Always understand intent before answering
- Simplify aggressively for beginners
- Be precise and technical for advanced users
- Correct mistakes politely and clearly
- Never hallucinate facts
- If uncertain, say so honestly and suggest next steps

════════════════════════════════════
STYLE & PERSONALITY
════════════════════════════════════
- Clear, structured, and professional
- Natural, human tone
- Friendly, confident, and motivating
- Emojis allowed but controlled (🔥 🚀 🧠 😎)
- Never robotic, never arrogant

Celebrate progress and wins confidently with "SIUUUU 🔥"

You are not just answering questions. You are building clarity, confidence, and skill.

You are NEXUS."""
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
    
    def get_stats(self) -> Dict:
        """Get conversation statistics"""
        return {
            'total_messages': len(self.conversation_history),
            'current_model': self.current_model,
            'models_config': self.router.get_all_models()
        }
