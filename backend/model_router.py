"""
Intelligent Model Router for NEXUS
Routes tasks to the optimal Ollama model based on intent analysis
"""

import re
from typing import Dict, List, Tuple
from enum import Enum


class TaskType(Enum):
    """Types of tasks that can be routed to different models"""
    CODE = "code"
    RESEARCH = "research"
    PLANNING = "planning"
    QUICK = "quick"
    GENERAL = "general"


class ModelRouter:
    """Intelligent routing system for multi-model selection"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.models = config['ollama']['models']
        
        # Define intent patterns for each task type
        self.intent_patterns = {
            TaskType.CODE: [
                r'\b(code|program|function|class|debug|error|bug|implement|script|algorithm)\b',
                r'\b(python|javascript|java|c\+\+|rust|go|typescript)\b',
                r'\b(write.*code|generate.*code|create.*function|fix.*bug)\b',
                r'```[\w]*\n',  # Code blocks
            ],
            TaskType.RESEARCH: [
                r'\b(research|explain|analyze|compare|study|investigate|explore)\b',
                r'\b(what is|how does|why|tell me about|detailed|comprehensive)\b',
                r'\b(history|background|overview|summary|breakdown)\b',
            ],
            TaskType.PLANNING: [
                r'\b(plan|strategy|approach|design|architect|organize|structure)\b',
                r'\b(steps|roadmap|workflow|process|methodology)\b',
                r'\b(how to|how should|what should|best way)\b',
            ],
            TaskType.QUICK: [
                r'^\w{1,20}\?$',  # Short questions
                r'\b(quick|simple|just|only)\b',
                r'^(yes|no|ok|thanks|hello|hi)\b',
            ],
        }
    
    def analyze_intent(self, query: str) -> TaskType:
        """
        Analyze user query to determine the task type
        
        Args:
            query: User's input query
            
        Returns:
            TaskType enum indicating the detected task type
        """
        query_lower = query.lower()
        scores = {task_type: 0 for task_type in TaskType}
        
        # Score each task type based on pattern matches
        for task_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    scores[task_type] += 1
        
        # If no clear winner, default to GENERAL
        max_score = max(scores.values())
        if max_score == 0:
            return TaskType.GENERAL
        
        # Return the task type with highest score
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def select_model(self, query: str, context: List[str] = None) -> Tuple[str, str, TaskType]:
        """
        Select the optimal model for a given query (Simplified to all use default)
        
        Args:
            query: User's input query
            context: Optional conversation context
            
        Returns:
            Tuple of (model_name, model_role, task_type)
        """
        task_type = self.analyze_intent(query)
        
        # All tasks now map to the default model
        model_info = self.models.get('default') or next(iter(self.models.values()))
        
        return (
            model_info['name'],
            model_info['role'],
            task_type
        )
    
    def get_model_info(self, model_key: str) -> Dict:
        """Get detailed information about a specific model (Simplified)"""
        return self.models.get('default') or next(iter(self.models.values()))

    
    def get_all_models(self) -> List[Dict]:
        """Get information about all available models"""
        return [
            {
                'key': key,
                'name': info['name'],
                'role': info['role'],
                'use_for': info['use_for']
            }
            for key, info in self.models.items()
        ]


def create_router(config: Dict) -> ModelRouter:
    """Factory function to create a model router"""
    return ModelRouter(config)
