import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

from planning_agent import PlanningAgent
from research_agents import ResearchTeam
from synthesis_agent import SynthesisAgent
from report_writer import ReportWriter
from utils import setup_logging, load_config

load_dotenv()

@dataclass
class ResearchContext:
    user_question: str
    research_plan: List[Dict[str, Any]]
    findings: Dict[str, Any]
    sources: List[Dict[str, Any]]
    conflicts: List[Dict[str, Any]]
    user_profile: Optional[Dict[str, Any]] = None

class DeepResearchSystem:
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or load_config()
        self.logger = setup_logging("deep_research_system")
        
        self.planning_agent = PlanningAgent(self.config)
        self.research_team = ResearchTeam(self.config)
        self.synthesis_agent = SynthesisAgent(self.config)
        self.report_writer = ReportWriter(self.config)
        
        self.logger.info("Deep Research System initialized successfully")
    
    async def conduct_research(self, question: str, user_profile: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.logger.info(f"Starting research on: {question}")
        
        context = ResearchContext(
            user_question=question,
            research_plan=[],
            findings={},
            sources=[],
            conflicts=[],
            user_profile=user_profile
        )
        
        try:
            self.logger.info("Phase 1: Planning research approach")
            context.research_plan = await self.planning_agent.create_research_plan(question)
            self.logger.info(f"Created research plan with {len(context.research_plan)} tasks")
            
            self.logger.info("Phase 2: Executing parallel research")
            research_results = await self.research_team.execute_parallel_research(context.research_plan)
            context.findings = research_results['findings']
            context.sources = research_results['sources']
            context.conflicts = research_results['conflicts']
            
            self.logger.info("Phase 3: Synthesizing findings")
            synthesis = await self.synthesis_agent.synthesize_findings(
                context.findings, 
                context.sources, 
                context.conflicts
            )
            
            self.logger.info("Phase 4: Generating final report")
            final_report = await self.report_writer.create_research_report(
                question=question,
                synthesis=synthesis,
                sources=context.sources,
                conflicts=context.conflicts,
                user_profile=user_profile
            )
            
            self.logger.info("Research completed successfully")
            return final_report
            
        except Exception as e:
            self.logger.error(f"Research failed: {str(e)}")
            raise
    
    async def research_with_streaming(self, question: str, user_profile: Optional[Dict[str, Any]] = None):
        self.logger.info(f"Starting streaming research on: {question}")
        
        context = ResearchContext(
            user_question=question,
            research_plan=[],
            findings={},
            sources=[],
            conflicts=[],
            user_profile=user_profile
        )
        
        try:
            yield {"phase": "planning", "message": "Creating research plan..."}
            context.research_plan = await self.planning_agent.create_research_plan(question)
            yield {"phase": "planning", "complete": True, "tasks": len(context.research_plan)}
            
            yield {"phase": "research", "message": "Executing parallel research..."}
            async for update in self.research_team.execute_parallel_research_streaming(context.research_plan):
                yield {"phase": "research", "update": update}
            
            research_results = await self.research_team.get_final_results()
            context.findings = research_results['findings']
            context.sources = research_results['sources']
            context.conflicts = research_results['conflicts']
            
            yield {"phase": "synthesis", "message": "Synthesizing findings..."}
            synthesis = await self.synthesis_agent.synthesize_findings(
                context.findings, 
                context.sources, 
                context.conflicts
            )
            yield {"phase": "synthesis", "complete": True}
            
            yield {"phase": "report", "message": "Generating final report..."}
            final_report = await self.report_writer.create_research_report(
                question=question,
                synthesis=synthesis,
                sources=context.sources,
                conflicts=context.conflicts,
                user_profile=user_profile
            )
            
            yield {"phase": "complete", "report": final_report}
            
        except Exception as e:
            self.logger.error(f"Streaming research failed: {str(e)}")
            yield {"phase": "error", "error": str(e)}

async def main():
    research_system = DeepResearchSystem()
    
    test_questions = [
        "What are the benefits of electric cars?",
        "Compare the environmental impact of electric vs hybrid vs gas cars",
        "How has artificial intelligence changed healthcare from 2020 to 2024, including both benefits and concerns from medical professionals?",
        "Analyze the economic impact of remote work policies on small businesses vs large corporations, including productivity data and employee satisfaction trends"
    ]
    
    user_profile = {
        "name": "Alex",
        "city": "San Francisco",
        "topic": "Technology and AI",
        "expertise_level": "Intermediate"
    }
    
    print("Testing Deep Research System with Level 1 question...")
    result = await research_system.conduct_research(
        test_questions[0], 
        user_profile=user_profile
    )
    
    print("\n" + "="*50)
    print("RESEARCH REPORT")
    print("="*50)
    print(f"Question: {test_questions[0]}")
    print(f"Report: {result['summary']}")
    print(f"Sources: {len(result['sources'])} found")
    print(f"Conflicts: {len(result['conflicts'])} detected")

if __name__ == "__main__":
    asyncio.run(main())
