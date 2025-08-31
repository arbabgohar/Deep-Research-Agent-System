"""
Planning Agent - Breaks down complex research questions into manageable tasks
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from llm_client import LLMClient
from utils import setup_logging

@dataclass
class ResearchTask:
    """Represents a single research task"""
    id: str
    title: str
    description: str
    keywords: List[str]
    priority: str  # "high", "medium", "low"
    estimated_sources: int
    dependencies: List[str] = None

class PlanningAgent:
    """
    Agent responsible for breaking down complex research questions into 
    manageable research tasks and creating a research plan.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = setup_logging("planning_agent")
        self.llm_client = LLMClient(config)
        
        self.system_prompt = """You are an expert research planner. Your job is to break down complex research questions into specific, manageable research tasks.

For each research question, you should:
1. Identify the main components and sub-questions
2. Create specific research tasks for each component
3. Prioritize tasks based on importance
4. Suggest relevant keywords for each task
5. Estimate how many sources each task might need

Return your response as a structured list of research tasks with clear titles, descriptions, and priorities."""

    async def create_research_plan(self, question: str) -> List[Dict[str, Any]]:
        """
        Create a comprehensive research plan for the given question.
        
        Args:
            question: The research question to plan for
            
        Returns:
            List of research tasks with details
        """
        self.logger.info(f"Creating research plan for: {question}")
        
        # Analyze the question complexity
        complexity = await self._analyze_question_complexity(question)
        self.logger.info(f"Question complexity: {complexity}")
        
        # Generate research tasks
        tasks = await self._generate_research_tasks(question, complexity)
        
        # Optimize the plan
        optimized_tasks = await self._optimize_research_plan(tasks, complexity)
        
        self.logger.info(f"Created research plan with {len(optimized_tasks)} tasks")
        return optimized_tasks
    
    async def _analyze_question_complexity(self, question: str) -> Dict[str, Any]:
        """Analyze the complexity of the research question"""
        
        analysis_prompt = f"""
        Analyze the complexity of this research question: "{question}"
        
        Consider:
        1. Number of topics/concepts involved
        2. Whether it requires comparison/analysis
        3. Time period considerations
        4. Need for multiple perspectives
        5. Data requirements
        
        Return a JSON object with:
        - complexity_level: "simple", "moderate", "complex", "expert"
        - topics_count: number of main topics
        - requires_comparison: boolean
        - requires_temporal_analysis: boolean
        - requires_multiple_perspectives: boolean
        - estimated_tasks: number of research tasks needed
        """
        
        response = await self.llm_client.get_completion(analysis_prompt)
        return self._parse_complexity_analysis(response)
    
    async def _generate_research_tasks(self, question: str, complexity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific research tasks based on the question and complexity"""
        
        task_generation_prompt = f"""
        Research Question: "{question}"
        Complexity Analysis: {complexity}
        
        Create a detailed research plan with specific tasks. For each task, provide:
        - id: unique identifier
        - title: clear, specific title
        - description: what this task will research
        - keywords: relevant search terms
        - priority: "high", "medium", or "low"
        - estimated_sources: number of sources needed
        - dependencies: any tasks this depends on (if any)
        
        Return as a JSON array of task objects.
        """
        
        response = await self.llm_client.get_completion(task_generation_prompt)
        return self._parse_research_tasks(response)
    
    async def _optimize_research_plan(self, tasks: List[Dict[str, Any]], complexity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Optimize the research plan for efficiency and completeness"""
        
        optimization_prompt = f"""
        Research Tasks: {tasks}
        Complexity: {complexity}
        
        Optimize this research plan by:
        1. Ensuring all aspects of the question are covered
        2. Balancing task priorities appropriately
        3. Identifying any missing critical tasks
        4. Suggesting parallel execution opportunities
        5. Estimating total research time
        
        Return the optimized task list as JSON.
        """
        
        response = await self.llm_client.get_completion(optimization_prompt)
        return self._parse_research_tasks(response)
    
    def _parse_complexity_analysis(self, response: str) -> Dict[str, Any]:
        """Parse the complexity analysis response"""
        try:
            # Simple JSON parsing - in production, use proper JSON parsing
            import json
            return json.loads(response)
        except:
            # Fallback parsing
            return {
                "complexity_level": "moderate",
                "topics_count": 2,
                "requires_comparison": "compare" in response.lower(),
                "requires_temporal_analysis": "2020" in response or "2024" in response,
                "requires_multiple_perspectives": "perspective" in response.lower(),
                "estimated_tasks": 3
            }
    
    def _parse_research_tasks(self, response: str) -> List[Dict[str, Any]]:
        """Parse the research tasks response"""
        try:
            import json
            return json.loads(response)
        except:
            # Fallback: create basic tasks
            return [
                {
                    "id": "task_1",
                    "title": "Basic Research",
                    "description": "Initial research on the main topic",
                    "keywords": ["research", "topic"],
                    "priority": "high",
                    "estimated_sources": 5,
                    "dependencies": []
                }
            ]
    
    async def validate_research_plan(self, plan: List[Dict[str, Any]], question: str) -> Dict[str, Any]:
        """
        Validate that the research plan adequately covers the question.
        
        Args:
            plan: The research plan to validate
            question: The original research question
            
        Returns:
            Validation results with suggestions for improvement
        """
        
        validation_prompt = f"""
        Research Question: "{question}"
        Research Plan: {plan}
        
        Validate this research plan by checking:
        1. Does it cover all aspects of the question?
        2. Are there any gaps or missing topics?
        3. Is the priority distribution appropriate?
        4. Are there any redundant tasks?
        5. Can any tasks be combined or split?
        
        Return validation results as JSON with:
        - is_complete: boolean
        - missing_topics: list of missing topics
        - suggestions: list of improvement suggestions
        - confidence_score: 0-100
        """
        
        response = await self.llm_client.get_completion(validation_prompt)
        return self._parse_validation_results(response)
    
    def _parse_validation_results(self, response: str) -> Dict[str, Any]:
        """Parse validation results"""
        try:
            import json
            return json.loads(response)
        except:
            return {
                "is_complete": True,
                "missing_topics": [],
                "suggestions": [],
                "confidence_score": 80
            }

# Example usage
async def test_planning_agent():
    """Test the planning agent with sample questions"""
    
    config = {
        "llm_provider": "openai",
        "model": "gpt-4",
        "temperature": 0.3
    }
    
    planning_agent = PlanningAgent(config)
    
    test_questions = [
        "What are the benefits of electric cars?",
        "Compare the environmental impact of electric vs hybrid vs gas cars",
        "How has artificial intelligence changed healthcare from 2020 to 2024?"
    ]
    
    for question in test_questions:
        print(f"\nPlanning research for: {question}")
        plan = await planning_agent.create_research_plan(question)
        
        print(f"Created {len(plan)} research tasks:")
        for task in plan:
            print(f"  - {task.get('title', 'Unknown')} (Priority: {task.get('priority', 'Unknown')})")

if __name__ == "__main__":
    asyncio.run(test_planning_agent())
