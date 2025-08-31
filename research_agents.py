"""
Research Team - Multiple specialized agents working together
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import time

from llm_client import LLMClient
from search_client import SearchClient
from utils import setup_logging

@dataclass
class ResearchResult:
    """Represents a single research result"""
    task_id: str
    title: str
    content: str
    sources: List[Dict[str, Any]]
    confidence: float
    agent_id: str
    timestamp: float

@dataclass
class SourceInfo:
    """Information about a source"""
    url: str
    title: str
    snippet: str
    domain: str
    quality_score: float
    reliability: str  # "high", "medium", "low"

class FactFinderAgent:
    """Agent specialized in finding factual information"""
    
    def __init__(self, config: Dict[str, Any], agent_id: str = "fact_finder"):
        self.config = config
        self.agent_id = agent_id
        self.logger = setup_logging(f"agent_{agent_id}")
        self.llm_client = LLMClient(config)
        self.search_client = SearchClient(config)
        
        self.system_prompt = """You are a fact-finding specialist. Your job is to:
1. Search for accurate, factual information
2. Focus on verifiable data and statistics
3. Look for authoritative sources
4. Extract key facts and figures
5. Provide clear, concise summaries

Always cite your sources and indicate confidence levels."""

    async def research_task(self, task: Dict[str, Any]) -> ResearchResult:
        """Research a specific task and return findings"""
        
        self.logger.info(f"Researching task: {task.get('title', 'Unknown')}")
        
        # Search for information
        search_query = " ".join(task.get('keywords', []))
        search_results = await self.search_client.search(search_query, max_results=10)
        
        # Analyze and extract facts
        facts = await self._extract_facts(search_results, task)
        
        # Calculate confidence
        confidence = await self._calculate_confidence(facts, search_results)
        
        return ResearchResult(
            task_id=task.get('id', 'unknown'),
            title=task.get('title', 'Unknown Task'),
            content=facts,
            sources=search_results,
            confidence=confidence,
            agent_id=self.agent_id,
            timestamp=time.time()
        )

    async def _extract_facts(self, search_results: List[Dict[str, Any]], task: Dict[str, Any]) -> str:
        """Extract factual information from search results"""
        
        prompt = f"""
        Task: {task.get('title', 'Unknown')}
        Description: {task.get('description', 'No description')}
        
        Search Results:
        {search_results}
        
        Extract the most important factual information related to this task. Focus on:
        1. Key facts and figures
        2. Statistical data
        3. Expert opinions
        4. Recent developments
        5. Verifiable claims
        
        Provide a clear, organized summary with bullet points.
        """
        
        return await self.llm_client.get_completion(prompt)

    async def _calculate_confidence(self, facts: str, sources: List[Dict[str, Any]]) -> float:
        """Calculate confidence level based on source quality and fact consistency"""
        
        # Simple confidence calculation based on source quality
        high_quality_sources = sum(1 for s in sources if self._is_high_quality_source(s))
        total_sources = len(sources)
        
        if total_sources == 0:
            return 0.0
        
        base_confidence = high_quality_sources / total_sources
        return min(1.0, base_confidence + 0.2)  # Add some base confidence

    def _is_high_quality_source(self, source: Dict[str, Any]) -> bool:
        """Check if a source is high quality"""
        domain = source.get('domain', '').lower()
        high_quality_domains = ['.edu', '.gov', '.org', 'wikipedia.org', 'reuters.com', 'bbc.com']
        return any(domain.endswith(d) for d in high_quality_domains)

class SourceCheckerAgent:
    """Agent specialized in evaluating source quality and reliability"""
    
    def __init__(self, config: Dict[str, Any], agent_id: str = "source_checker"):
        self.config = config
        self.agent_id = agent_id
        self.logger = setup_logging(f"agent_{agent_id}")
        self.llm_client = LLMClient(config)
        
        self.system_prompt = """You are a source quality specialist. Your job is to:
1. Evaluate the reliability of information sources
2. Check for bias and credibility
3. Verify source authority
4. Assess information freshness
5. Identify potential conflicts or contradictions

Rate sources as High, Medium, or Low reliability."""

    async def evaluate_sources(self, sources: List[Dict[str, Any]]) -> List[SourceInfo]:
        """Evaluate the quality and reliability of sources"""
        
        self.logger.info(f"Evaluating {len(sources)} sources")
        
        evaluated_sources = []
        for source in sources:
            evaluation = await self._evaluate_single_source(source)
            evaluated_sources.append(evaluation)
        
        return evaluated_sources

    async def _evaluate_single_source(self, source: Dict[str, Any]) -> SourceInfo:
        """Evaluate a single source"""
        
        prompt = f"""
        Evaluate this source for reliability and quality:
        
        URL: {source.get('url', 'Unknown')}
        Title: {source.get('title', 'Unknown')}
        Snippet: {source.get('snippet', 'No snippet')}
        Domain: {source.get('domain', 'Unknown')}
        
        Rate this source on:
        1. Authority (0-10)
        2. Credibility (0-10)
        3. Bias level (0-10, 0=neutral)
        4. Information freshness (0-10)
        5. Overall reliability: "high", "medium", or "low"
        
        Return as JSON with these fields.
        """
        
        response = await self.llm_client.get_completion(prompt)
        evaluation = self._parse_evaluation(response)
        
        return SourceInfo(
            url=source.get('url', ''),
            title=source.get('title', ''),
            snippet=source.get('snippet', ''),
            domain=source.get('domain', ''),
            quality_score=evaluation.get('quality_score', 0.5),
            reliability=evaluation.get('reliability', 'medium')
        )

    def _parse_evaluation(self, response: str) -> Dict[str, Any]:
        """Parse the evaluation response"""
        try:
            import json
            return json.loads(response)
        except:
            return {
                'quality_score': 0.5,
                'reliability': 'medium'
            }

class ConflictDetectorAgent:
    """Agent specialized in detecting conflicts and contradictions"""
    
    def __init__(self, config: Dict[str, Any], agent_id: str = "conflict_detector"):
        self.config = config
        self.agent_id = agent_id
        self.logger = setup_logging(f"agent_{agent_id}")
        self.llm_client = LLMClient(config)
        
        self.system_prompt = """You are a conflict detection specialist. Your job is to:
1. Identify contradictions between sources
2. Spot conflicting data or claims
3. Detect bias and perspective differences
4. Highlight areas of uncertainty
5. Suggest which sources are more reliable

Be thorough but fair in your analysis."""

    async def detect_conflicts(self, research_results: List[ResearchResult]) -> List[Dict[str, Any]]:
        """Detect conflicts and contradictions in research results"""
        
        self.logger.info(f"Detecting conflicts in {len(research_results)} research results")
        
        if len(research_results) < 2:
            return []
        
        # Compare results for conflicts
        conflicts = []
        for i, result1 in enumerate(research_results):
            for j, result2 in enumerate(research_results[i+1:], i+1):
                conflict = await self._compare_results(result1, result2)
                if conflict:
                    conflicts.append(conflict)
        
        return conflicts

    async def _compare_results(self, result1: ResearchResult, result2: ResearchResult) -> Optional[Dict[str, Any]]:
        """Compare two research results for conflicts"""
        
        prompt = f"""
        Compare these two research results for conflicts or contradictions:
        
        Result 1 (Task: {result1.title}):
        {result1.content}
        Sources: {[s.get('url', '') for s in result1.sources]}
        
        Result 2 (Task: {result2.title}):
        {result2.content}
        Sources: {[s.get('url', '') for s in result2.sources]}
        
        Identify any conflicts, contradictions, or significant disagreements.
        Return as JSON with:
        - conflict_type: "data", "opinion", "methodology", "none"
        - description: description of the conflict
        - severity: "low", "medium", "high"
        - sources_involved: list of conflicting sources
        """
        
        response = await self.llm_client.get_completion(prompt)
        conflict = self._parse_conflict(response)
        
        if conflict and conflict.get('conflict_type') != 'none':
            return conflict
        
        return None

    def _parse_conflict(self, response: str) -> Dict[str, Any]:
        """Parse the conflict detection response"""
        try:
            import json
            return json.loads(response)
        except:
            return {
                'conflict_type': 'none',
                'description': 'No conflicts detected',
                'severity': 'low',
                'sources_involved': []
            }

class ResearchTeam:
    """
    Coordinates multiple specialized research agents for parallel research execution.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = setup_logging("research_team")
        
        # Initialize specialized agents
        self.fact_finder = FactFinderAgent(config, "fact_finder")
        self.source_checker = SourceCheckerAgent(config, "source_checker")
        self.conflict_detector = ConflictDetectorAgent(config, "conflict_detector")
        
        # Research results storage
        self.research_results = []
        self.evaluated_sources = []
        self.detected_conflicts = []

    async def execute_parallel_research(self, research_plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute research tasks in parallel using multiple agents.
        
        Args:
            research_plan: List of research tasks to execute
            
        Returns:
            Dictionary with findings, sources, and conflicts
        """
        self.logger.info(f"Executing parallel research for {len(research_plan)} tasks")
        
        # Reset results
        self.research_results = []
        self.evaluated_sources = []
        self.detected_conflicts = []
        
        # Execute research tasks in parallel
        tasks = [self.fact_finder.research_task(task) for task in research_plan]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and store results
        for result in results:
            if isinstance(result, ResearchResult):
                self.research_results.append(result)
        
        # Evaluate sources
        all_sources = []
        for result in self.research_results:
            all_sources.extend(result.sources)
        
        self.evaluated_sources = await self.source_checker.evaluate_sources(all_sources)
        
        # Detect conflicts
        self.detected_conflicts = await self.conflict_detector.detect_conflicts(self.research_results)
        
        self.logger.info(f"Research completed: {len(self.research_results)} results, {len(self.evaluated_sources)} sources, {len(self.detected_conflicts)} conflicts")
        
        return {
            'findings': [self._result_to_dict(r) for r in self.research_results],
            'sources': [self._source_to_dict(s) for s in self.evaluated_sources],
            'conflicts': self.detected_conflicts
        }

    async def execute_parallel_research_streaming(self, research_plan: List[Dict[str, Any]]) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute research with streaming updates.
        
        Args:
            research_plan: List of research tasks to execute
            
        Yields:
            Progress updates and partial results
        """
        self.logger.info(f"Starting streaming research for {len(research_plan)} tasks")
        
        # Reset results
        self.research_results = []
        
        # Execute tasks with progress updates
        for i, task in enumerate(research_plan):
            yield {
                'type': 'task_start',
                'task_id': task.get('id'),
                'task_title': task.get('title'),
                'progress': f"{i+1}/{len(research_plan)}"
            }
            
            try:
                result = await self.fact_finder.research_task(task)
                self.research_results.append(result)
                
                yield {
                    'type': 'task_complete',
                    'task_id': task.get('id'),
                    'result': self._result_to_dict(result)
                }
            except Exception as e:
                yield {
                    'type': 'task_error',
                    'task_id': task.get('id'),
                    'error': str(e)
                }
        
        # Evaluate sources
        yield {'type': 'evaluating_sources', 'message': 'Evaluating source quality...'}
        all_sources = []
        for result in self.research_results:
            all_sources.extend(result.sources)
        
        self.evaluated_sources = await self.source_checker.evaluate_sources(all_sources)
        yield {'type': 'sources_evaluated', 'count': len(self.evaluated_sources)}
        
        # Detect conflicts
        yield {'type': 'detecting_conflicts', 'message': 'Detecting conflicts...'}
        self.detected_conflicts = await self.conflict_detector.detect_conflicts(self.research_results)
        yield {'type': 'conflicts_detected', 'count': len(self.detected_conflicts)}

    async def get_final_results(self) -> Dict[str, Any]:
        """Get the final research results"""
        return {
            'findings': [self._result_to_dict(r) for r in self.research_results],
            'sources': [self._source_to_dict(s) for s in self.evaluated_sources],
            'conflicts': self.detected_conflicts
        }

    def _result_to_dict(self, result: ResearchResult) -> Dict[str, Any]:
        """Convert ResearchResult to dictionary"""
        return {
            'task_id': result.task_id,
            'title': result.title,
            'content': result.content,
            'sources': result.sources,
            'confidence': result.confidence,
            'agent_id': result.agent_id,
            'timestamp': result.timestamp
        }

    def _source_to_dict(self, source: SourceInfo) -> Dict[str, Any]:
        """Convert SourceInfo to dictionary"""
        return {
            'url': source.url,
            'title': source.title,
            'snippet': source.snippet,
            'domain': source.domain,
            'quality_score': source.quality_score,
            'reliability': source.reliability
        }

# Example usage
async def test_research_team():
    """Test the research team with sample tasks"""
    
    config = {
        "llm_provider": "openai",
        "model": "gpt-4",
        "temperature": 0.3,
        "search_provider": "tavily"
    }
    
    research_team = ResearchTeam(config)
    
    sample_tasks = [
        {
            "id": "task_1",
            "title": "Electric Car Benefits",
            "description": "Research the benefits of electric cars",
            "keywords": ["electric car benefits", "EV advantages"],
            "priority": "high",
            "estimated_sources": 5
        },
        {
            "id": "task_2", 
            "title": "Environmental Impact",
            "description": "Research environmental impact of electric cars",
            "keywords": ["electric car environmental impact", "EV carbon footprint"],
            "priority": "high",
            "estimated_sources": 5
        }
    ]
    
    print("Testing Research Team...")
    results = await research_team.execute_parallel_research(sample_tasks)
    
    print(f"Research completed:")
    print(f"  - Findings: {len(results['findings'])}")
    print(f"  - Sources: {len(results['sources'])}")
    print(f"  - Conflicts: {len(results['conflicts'])}")

if __name__ == "__main__":
    asyncio.run(test_research_team())
