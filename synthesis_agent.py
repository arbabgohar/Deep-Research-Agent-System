import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict

from llm_client import LLMClient
from utils import setup_logging

@dataclass
class SynthesisResult:
    key_insights: List[str]
    themes: List[Dict[str, Any]]
    trends: List[Dict[str, Any]]
    conclusions: List[str]
    confidence_level: float
    gaps_identified: List[str]
    recommendations: List[str]

class SynthesisAgent:
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = setup_logging("synthesis_agent")
        self.llm_client = LLMClient(config)
        
        self.system_prompt = """You are an expert research synthesis specialist. Your job is to:
1. Combine findings from multiple research tasks into coherent insights
2. Identify common themes and patterns across sources
3. Spot trends and emerging patterns
4. Draw meaningful conclusions
5. Identify gaps in the research
6. Provide actionable recommendations

Focus on creating a comprehensive, well-organized synthesis that adds value beyond the individual findings."""

    async def synthesize_findings(
        self, 
        findings: List[Dict[str, Any]], 
        sources: List[Dict[str, Any]], 
        conflicts: List[Dict[str, Any]]
    ) -> SynthesisResult:
        self.logger.info(f"Synthesizing {len(findings)} findings with {len(sources)} sources")
        
        themes = await self._identify_themes(findings)
        trends = await self._identify_trends(findings, sources)
        key_insights = await self._extract_key_insights(findings, themes)
        
        conclusions = await self._generate_conclusions(findings, themes, conflicts)
        
        gaps = await self._identify_research_gaps(findings, sources)
        
        recommendations = await self._generate_recommendations(findings, gaps, conflicts)
        
        confidence = await self._calculate_synthesis_confidence(findings, sources, conflicts)
        
        return SynthesisResult(
            key_insights=key_insights,
            themes=themes,
            trends=trends,
            conclusions=conclusions,
            confidence_level=confidence,
            gaps_identified=gaps,
            recommendations=recommendations
        )

    async def _identify_themes(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        prompt = f"""
        Analyze these research findings to identify common themes:
        
        Findings:
        {findings}
        
        Identify the main themes that emerge across these findings. For each theme:
        1. Provide a clear theme name
        2. Describe what the theme encompasses
        3. List the key evidence supporting this theme
        4. Indicate how many findings relate to this theme
        5. Rate the strength of evidence (1-10)
        
        Return as a JSON array of theme objects with:
        - name: theme name
        - description: theme description
        - evidence: list of supporting evidence
        - frequency: number of findings related to this theme
        - strength: evidence strength (1-10)
        """
        
        response = await self.llm_client.get_completion(prompt)
        return self._parse_themes(response)

    async def _identify_trends(self, findings: List[Dict[str, Any]], sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        prompt = f"""
        Analyze these research findings and sources to identify trends:
        
        Findings:
        {findings}
        
        Sources:
        {sources}
        
        Look for:
        1. Temporal trends (changes over time)
        2. Consensus patterns (agreement across sources)
        3. Emerging patterns (new developments)
        4. Regional or demographic patterns
        5. Methodological trends
        
        For each trend, provide:
        - trend_name: descriptive name
        - description: what the trend shows
        - evidence: supporting evidence
        - confidence: how confident you are (0-1)
        - implications: what this trend means
        
        Return as a JSON array of trend objects.
        """
        
        response = await self.llm_client.get_completion(prompt)
        return self._parse_trends(response)

    async def _extract_key_insights(self, findings: List[Dict[str, Any]], themes: List[Dict[str, Any]]) -> List[str]:
        prompt = f"""
        Based on these research findings and identified themes, extract the key insights:
        
        Findings:
        {findings}
        
        Themes:
        {themes}
        
        Identify the most important insights that emerge from this research. Focus on:
        1. Surprising or counterintuitive findings
        2. Strong consensus points
        3. Important implications
        4. Critical data points
        5. Novel perspectives
        
        Provide each insight as a clear, concise statement. Return as a JSON array of insight strings.
        """
        
        response = await self.llm_client.get_completion(prompt)
        return self._parse_insights(response)

    async def _generate_conclusions(
        self, 
        findings: List[Dict[str, Any]], 
        themes: List[Dict[str, Any]], 
        conflicts: List[Dict[str, Any]]
    ) -> List[str]:
        prompt = f"""
        Based on the research findings, themes, and conflicts, generate conclusions:
        
        Findings:
        {findings}
        
        Themes:
        {themes}
        
        Conflicts:
        {conflicts}
        
        Generate conclusions that:
        1. Address the main research question
        2. Acknowledge areas of agreement and disagreement
        3. Consider the strength of evidence
        4. Highlight the most reliable findings
        5. Note limitations and uncertainties
        
        Return as a JSON array of conclusion strings.
        """
        
        response = await self.llm_client.get_completion(prompt)
        return self._parse_conclusions(response)

    async def _identify_research_gaps(self, findings: List[Dict[str, Any]], sources: List[Dict[str, Any]]) -> List[str]:
        prompt = f"""
        Analyze the research findings and sources to identify gaps:
        
        Findings:
        {findings}
        
        Sources:
        {sources}
        
        Identify gaps such as:
        1. Missing data or information
        2. Under-researched areas
        3. Methodological limitations
        4. Temporal gaps (missing time periods)
        5. Geographic or demographic gaps
        6. Conflicting evidence that needs resolution
        
        Return as a JSON array of gap description strings.
        """
        
        response = await self.llm_client.get_completion(prompt)
        return self._parse_gaps(response)

    async def _generate_recommendations(
        self, 
        findings: List[Dict[str, Any]], 
        gaps: List[str], 
        conflicts: List[Dict[str, Any]]
    ) -> List[str]:
        prompt = f"""
        Based on the research findings, identified gaps, and conflicts, generate recommendations:
        
        Findings:
        {findings}
        
        Gaps:
        {gaps}
        
        Conflicts:
        {conflicts}
        
        Generate recommendations for:
        1. Further research needed
        2. Areas requiring more investigation
        3. How to resolve conflicts
        4. Practical applications of findings
        5. Policy or decision-making implications
        
        Return as a JSON array of recommendation strings.
        """
        
        response = await self.llm_client.get_completion(prompt)
        return self._parse_recommendations(response)

    async def _calculate_synthesis_confidence(
        self, 
        findings: List[Dict[str, Any]], 
        sources: List[Dict[str, Any]], 
        conflicts: List[Dict[str, Any]]
    ) -> float:
        total_findings = len(findings)
        high_quality_sources = sum(1 for s in sources if s.get('reliability') == 'high')
        total_sources = len(sources)
        conflict_count = len(conflicts)
        
        if total_findings == 0 or total_sources == 0:
            return 0.0
        
        source_confidence = high_quality_sources / total_sources if total_sources > 0 else 0.0
        
        conflict_penalty = min(0.3, conflict_count * 0.1)
        
        findings_bonus = min(0.2, total_findings * 0.05)
        
        confidence = source_confidence - conflict_penalty + findings_bonus
        return max(0.0, min(1.0, confidence))

    def _parse_themes(self, response: str) -> List[Dict[str, Any]]:
        try:
            import json
            return json.loads(response)
        except:
            return [
                {
                    "name": "General Theme",
                    "description": "General findings from the research",
                    "evidence": ["Various sources"],
                    "frequency": 1,
                    "strength": 5
                }
            ]

    def _parse_trends(self, response: str) -> List[Dict[str, Any]]:
        try:
            import json
            return json.loads(response)
        except:
            return [
                {
                    "trend_name": "General Trend",
                    "description": "General pattern in the research",
                    "evidence": ["Various sources"],
                    "confidence": 0.5,
                    "implications": "Further research needed"
                }
            ]

    def _parse_insights(self, response: str) -> List[str]:
        try:
            import json
            return json.loads(response)
        except:
            return ["Key insights require further analysis"]

    def _parse_conclusions(self, response: str) -> List[str]:
        try:
            import json
            return json.loads(response)
        except:
            return ["Conclusions require further analysis"]

    def _parse_gaps(self, response: str) -> List[str]:
        try:
            import json
            return json.loads(response)
        except:
            return ["Research gaps require further analysis"]

    def _parse_recommendations(self, response: str) -> List[str]:
        try:
            import json
            return json.loads(response)
        except:
            return ["Recommendations require further analysis"]

    async def create_executive_summary(self, synthesis: SynthesisResult) -> str:
        prompt = f"""
        Create an executive summary of this research synthesis:
        
        Key Insights: {synthesis.key_insights}
        Main Themes: {synthesis.themes}
        Trends: {synthesis.trends}
        Conclusions: {synthesis.conclusions}
        Confidence Level: {synthesis.confidence_level}
        
        Write a concise executive summary (2-3 paragraphs) that:
        1. Highlights the most important findings
        2. Summarizes key themes and trends
        3. Presents main conclusions
        4. Notes confidence level and limitations
        5. Is suitable for decision-makers
        
        Keep it clear, concise, and actionable.
        """
        
        return await self.llm_client.get_completion(prompt)

    async def create_detailed_report(self, synthesis: SynthesisResult) -> Dict[str, Any]:
        executive_summary = await self.create_executive_summary(synthesis)
        
        return {
            "executive_summary": executive_summary,
            "key_insights": synthesis.key_insights,
            "themes": synthesis.themes,
            "trends": synthesis.trends,
            "conclusions": synthesis.conclusions,
            "research_gaps": synthesis.gaps_identified,
            "recommendations": synthesis.recommendations,
            "confidence_level": synthesis.confidence_level,
            "metadata": {
                "insights_count": len(synthesis.key_insights),
                "themes_count": len(synthesis.themes),
                "trends_count": len(synthesis.trends),
                "conclusions_count": len(synthesis.conclusions),
                "gaps_count": len(synthesis.gaps_identified),
                "recommendations_count": len(synthesis.recommendations)
            }
        }

async def test_synthesis_agent():
    config = {
        "llm_provider": "openai",
        "model": "gpt-4",
        "temperature": 0.3
    }
    
    synthesis_agent = SynthesisAgent(config)
    
    sample_findings = [
        {
            "task_id": "task_1",
            "title": "Electric Car Benefits",
            "content": "Electric cars offer significant environmental benefits including reduced emissions and lower operating costs.",
            "confidence": 0.8
        },
        {
            "task_id": "task_2",
            "title": "Environmental Impact",
            "content": "EVs have 50-70% lower lifetime emissions compared to gas vehicles, though battery production has environmental costs.",
            "confidence": 0.7
        }
    ]
    
    sample_sources = [
        {
            "url": "https://example.com/ev-benefits",
            "title": "Electric Vehicle Benefits",
            "reliability": "high",
            "quality_score": 0.9
        }
    ]
    
    sample_conflicts = []
    
    print("Testing Synthesis Agent...")
    synthesis = await synthesis_agent.synthesize_findings(
        sample_findings, 
        sample_sources, 
        sample_conflicts
    )
    
    print(f"Synthesis completed:")
    print(f"  - Key Insights: {len(synthesis.key_insights)}")
    print(f"  - Themes: {len(synthesis.themes)}")
    print(f"  - Trends: {len(synthesis.trends)}")
    print(f"  - Confidence: {synthesis.confidence_level:.2f}")
    
    report = await synthesis_agent.create_detailed_report(synthesis)
    print(f"  - Executive Summary: {len(report['executive_summary'])} characters")

if __name__ == "__main__":
    asyncio.run(test_synthesis_agent())
