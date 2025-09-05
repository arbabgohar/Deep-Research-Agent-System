import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from llm_client import LLMClient
from utils import setup_logging

@dataclass
class Citation:
    id: str
    url: str
    title: str
    author: Optional[str]
    publication_date: Optional[str]
    accessed_date: str
    reliability: str

@dataclass
class ResearchReport:
    title: str
    executive_summary: str
    methodology: str
    key_findings: List[str]
    detailed_analysis: Dict[str, Any]
    conclusions: List[str]
    recommendations: List[str]
    citations: List[Citation]
    metadata: Dict[str, Any]

class ReportWriter:
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = setup_logging("report_writer")
        self.llm_client = LLMClient(config)
        
        self.system_prompt = """You are an expert research report writer. Your job is to:
1. Create professional, well-structured research reports
2. Include proper citations and references
3. Write clear, concise, and actionable content
4. Organize information logically and coherently
5. Ensure academic/professional standards
6. Make complex information accessible to the target audience

Focus on clarity, accuracy, and professional presentation."""

    async def create_research_report(
        self,
        question: str,
        synthesis: Any,
        sources: List[Dict[str, Any]],
        conflicts: List[Dict[str, Any]],
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        self.logger.info(f"Creating research report for: {question}")
        
        title = await self._generate_report_title(question)
        
        executive_summary = await self._create_executive_summary(synthesis, question)
        
        methodology = await self._write_methodology(sources, conflicts)
        
        key_findings = await self._organize_key_findings(synthesis)
        
        detailed_analysis = await self._create_detailed_analysis(synthesis, sources, conflicts)
        
        conclusions = await self._write_conclusions(synthesis, conflicts)
        
        recommendations = await self._generate_recommendations(synthesis, user_profile)
        
        citations = await self._create_citations(sources)
        
        metadata = await self._generate_metadata(question, synthesis, sources, conflicts)
        
        report = ResearchReport(
            title=title,
            executive_summary=executive_summary,
            methodology=methodology,
            key_findings=key_findings,
            detailed_analysis=detailed_analysis,
            conclusions=conclusions,
            recommendations=recommendations,
            citations=citations,
            metadata=metadata
        )
        
        formatted_report = await self._format_report(report)
        
        self.logger.info("Research report created successfully")
        return formatted_report

    async def _generate_report_title(self, question: str) -> str:
        prompt = f"""
        Generate a professional, academic-style title for a research report based on this question:
        
        Question: "{question}"
        
        The title should be:
        1. Clear and descriptive
        2. Professional and academic in tone
        3. Concise but comprehensive
        4. Suitable for a research report
        
        Return only the title, no additional text.
        """
        
        return await self.llm_client.get_completion(prompt)

    async def _create_executive_summary(self, synthesis: Any, question: str) -> str:
        prompt = f"""
        Create an executive summary for a research report on: "{question}"
        
        Synthesis Data:
        - Key Insights: {synthesis.key_insights if hasattr(synthesis, 'key_insights') else 'N/A'}
        - Themes: {synthesis.themes if hasattr(synthesis, 'themes') else 'N/A'}
        - Conclusions: {synthesis.conclusions if hasattr(synthesis, 'conclusions') else 'N/A'}
        - Confidence Level: {synthesis.confidence_level if hasattr(synthesis, 'confidence_level') else 'N/A'}
        
        Write a 2-3 paragraph executive summary that:
        1. Summarizes the main findings
        2. Highlights key insights and conclusions
        3. Notes the confidence level and limitations
        4. Is suitable for decision-makers
        5. Provides actionable takeaways
        
        Keep it clear, concise, and professional.
        """
        
        return await self.llm_client.get_completion(prompt)

    async def _write_methodology(self, sources: List[Dict[str, Any]], conflicts: List[Dict[str, Any]]) -> str:
        prompt = f"""
        Write a methodology section for a research report based on:
        
        Sources Used: {len(sources)} sources
        Source Types: {[s.get('domain', 'Unknown') for s in sources]}
        Conflicts Detected: {len(conflicts)} conflicts
        
        Include:
        1. Research approach and methodology
        2. Source evaluation criteria
        3. Data collection methods
        4. Analysis approach
        5. Quality assurance measures
        6. Limitations and considerations
        
        Write in a professional, academic style.
        """
        
        return await self.llm_client.get_completion(prompt)

    async def _organize_key_findings(self, synthesis: Any) -> List[str]:
        if hasattr(synthesis, 'key_insights') and synthesis.key_insights:
            return synthesis.key_insights
        
        return [
            "Research findings require further analysis",
            "Multiple sources were consulted",
            "Additional research may be needed"
        ]

    async def _create_detailed_analysis(self, synthesis: Any, sources: List[Dict[str, Any]], conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        analysis = {}
        
        if hasattr(synthesis, 'themes') and synthesis.themes:
            analysis['themes'] = await self._analyze_themes(synthesis.themes)
        
        if hasattr(synthesis, 'trends') and synthesis.trends:
            analysis['trends'] = await self._analyze_trends(synthesis.trends)
        
        analysis['source_analysis'] = await self._analyze_sources(sources)
        
        if conflicts:
            analysis['conflict_analysis'] = await self._analyze_conflicts(conflicts)
        
        return analysis

    async def _analyze_themes(self, themes: List[Dict[str, Any]]) -> str:
        prompt = f"""
        Provide a detailed analysis of these research themes:
        
        Themes: {themes}
        
        For each theme, discuss:
        1. What the theme represents
        2. Strength of evidence
        3. Implications and significance
        4. How it relates to the overall research
        
        Write in a clear, analytical style.
        """
        
        return await self.llm_client.get_completion(prompt)

    async def _analyze_trends(self, trends: List[Dict[str, Any]]) -> str:
        prompt = f"""
        Provide a detailed analysis of these research trends:
        
        Trends: {trends}
        
        For each trend, discuss:
        1. What the trend indicates
        2. Evidence supporting the trend
        3. Implications and significance
        4. Future implications
        
        Write in a clear, analytical style.
        """
        
        return await self.llm_client.get_completion(prompt)

    async def _analyze_sources(self, sources: List[Dict[str, Any]]) -> str:
        prompt = f"""
        Provide an analysis of the sources used in this research:
        
        Sources: {sources}
        
        Discuss:
        1. Source diversity and quality
        2. Reliability assessment
        3. Potential biases
        4. Coverage and comprehensiveness
        5. Limitations of the source base
        
        Write in a clear, analytical style.
        """
        
        return await self.llm_client.get_completion(prompt)

    async def _analyze_conflicts(self, conflicts: List[Dict[str, Any]]) -> str:
        prompt = f"""
        Provide an analysis of the conflicts detected in this research:
        
        Conflicts: {conflicts}
        
        Discuss:
        1. Nature of the conflicts
        2. Potential causes
        3. Implications for findings
        4. How to address these conflicts
        5. Impact on confidence in results
        
        Write in a clear, analytical style.
        """
        
        return await self.llm_client.get_completion(prompt)

    async def _write_conclusions(self, synthesis: Any, conflicts: List[Dict[str, Any]]) -> List[str]:
        if hasattr(synthesis, 'conclusions') and synthesis.conclusions:
            return synthesis.conclusions
        
        prompt = f"""
        Generate conclusions for a research report based on:
        
        Synthesis: {synthesis}
        Conflicts: {conflicts}
        
        Write 3-5 clear, actionable conclusions that:
        1. Address the main research question
        2. Acknowledge limitations and conflicts
        3. Provide actionable insights
        4. Suggest next steps
        
        Return as a JSON array of conclusion strings.
        """
        
        response = await self.llm_client.get_completion(prompt)
        return self._parse_conclusions(response)

    async def _generate_recommendations(self, synthesis: Any, user_profile: Optional[Dict[str, Any]] = None) -> List[str]:
        if hasattr(synthesis, 'recommendations') and synthesis.recommendations:
            base_recommendations = synthesis.recommendations
        else:
            base_recommendations = ["Further research is recommended"]
        
        if user_profile:
            personalized_recommendations = await self._personalize_recommendations(base_recommendations, user_profile)
            return personalized_recommendations
        
        return base_recommendations

    async def _personalize_recommendations(self, recommendations: List[str], user_profile: Dict[str, Any]) -> List[str]:
        prompt = f"""
        Personalize these research recommendations for this user:
        
        User Profile: {user_profile}
        Base Recommendations: {recommendations}
        
        Adapt the recommendations to be relevant for:
        - User's location: {user_profile.get('city', 'Unknown')}
        - User's interests: {user_profile.get('topic', 'General')}
        - User's expertise level: {user_profile.get('expertise_level', 'General')}
        
        Make the recommendations more specific and actionable for this user.
        Return as a JSON array of personalized recommendation strings.
        """
        
        response = await self.llm_client.get_completion(prompt)
        return self._parse_recommendations(response)

    async def _create_citations(self, sources: List[Dict[str, Any]]) -> List[Citation]:
        citations = []
        for i, source in enumerate(sources):
            citation = Citation(
                id=f"[{i+1}]",
                url=source.get('url', ''),
                title=source.get('title', 'Unknown Title'),
                author=None,
                publication_date=None,
                accessed_date=datetime.now().strftime("%Y-%m-%d"),
                reliability=source.get('reliability', 'medium')
            )
            citations.append(citation)
        
        return citations

    async def _generate_metadata(self, question: str, synthesis: Any, sources: List[Dict[str, Any]], conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "research_question": question,
            "report_generated": datetime.now().isoformat(),
            "total_sources": len(sources),
            "high_quality_sources": sum(1 for s in sources if s.get('reliability') == 'high'),
            "conflicts_detected": len(conflicts),
            "confidence_level": getattr(synthesis, 'confidence_level', 0.0),
            "insights_count": len(getattr(synthesis, 'key_insights', [])),
            "themes_count": len(getattr(synthesis, 'themes', [])),
            "conclusions_count": len(getattr(synthesis, 'conclusions', [])),
            "recommendations_count": len(getattr(synthesis, 'recommendations', []))
        }

    async def _format_report(self, report: ResearchReport) -> Dict[str, Any]:
        formatted_citations = []
        for citation in report.citations:
            formatted_citations.append({
                "id": citation.id,
                "reference": f"{citation.title}. {citation.url}. Accessed {citation.accessed_date}. Reliability: {citation.reliability}."
            })
        
        formatted_report = {
            "title": report.title,
            "executive_summary": report.executive_summary,
            "methodology": report.methodology,
            "key_findings": report.key_findings,
            "detailed_analysis": report.detailed_analysis,
            "conclusions": report.conclusions,
            "recommendations": report.recommendations,
            "citations": formatted_citations,
            "metadata": report.metadata,
            "summary": report.executive_summary[:200] + "..." if len(report.executive_summary) > 200 else report.executive_summary
        }
        
        return formatted_report

    def _parse_conclusions(self, response: str) -> List[str]:
        try:
            import json
            return json.loads(response)
        except:
            return ["Conclusions require further analysis"]

    def _parse_recommendations(self, response: str) -> List[str]:
        try:
            import json
            return json.loads(response)
        except:
            return ["Recommendations require further analysis"]

    async def create_markdown_report(self, report: Dict[str, Any]) -> str:
        """Create a markdown formatted version of the report"""
        
        markdown = f"""# {report['title']}

## Executive Summary

{report['executive_summary']}

## Methodology

{report['methodology']}

## Key Findings

"""
        
        for i, finding in enumerate(report['key_findings'], 1):
            markdown += f"{i}. {finding}\n"
        
        markdown += "\n## Detailed Analysis\n\n"
        
        for section, content in report['detailed_analysis'].items():
            markdown += f"### {section.replace('_', ' ').title()}\n\n{content}\n\n"
        
        markdown += "## Conclusions\n\n"
        for conclusion in report['conclusions']:
            markdown += f"- {conclusion}\n"
        
        markdown += "\n## Recommendations\n\n"
        for recommendation in report['recommendations']:
            markdown += f"- {recommendation}\n"
        
        markdown += "\n## References\n\n"
        for citation in report['citations']:
            markdown += f"{citation['id']} {citation['reference']}\n"
        
        markdown += f"\n---\n*Report generated on {report['metadata']['report_generated']}*"
        
        return markdown

# Example usage
async def test_report_writer():
    """Test the report writer with sample data"""
    
    config = {
        "llm_provider": "openai",
        "model": "gpt-4",
        "temperature": 0.3
    }
    
    report_writer = ReportWriter(config)
    
    # Sample synthesis (simplified)
    class MockSynthesis:
        def __init__(self):
            self.key_insights = ["Electric cars reduce emissions", "Battery costs are decreasing"]
            self.themes = [{"name": "Environmental Benefits", "description": "EV environmental advantages"}]
            self.trends = [{"trend_name": "Cost Reduction", "description": "Decreasing EV costs"}]
            self.conclusions = ["EVs are becoming more viable", "Environmental benefits are significant"]
            self.recommendations = ["Consider EV adoption", "Invest in charging infrastructure"]
            self.confidence_level = 0.8
    
    synthesis = MockSynthesis()
    
    sample_sources = [
        {
            "url": "https://example.com/ev-benefits",
            "title": "Electric Vehicle Benefits",
            "reliability": "high",
            "quality_score": 0.9
        }
    ]
    
    sample_conflicts = []
    
    user_profile = {
        "name": "Alex",
        "city": "San Francisco",
        "topic": "Technology and AI",
        "expertise_level": "Intermediate"
    }
    
    print("Testing Report Writer...")
    report = await report_writer.create_research_report(
        "What are the benefits of electric cars?",
        synthesis,
        sample_sources,
        sample_conflicts,
        user_profile
    )
    
    print(f"Report created:")
    print(f"  - Title: {report['title']}")
    print(f"  - Key Findings: {len(report['key_findings'])}")
    print(f"  - Conclusions: {len(report['conclusions'])}")
    print(f"  - Citations: {len(report['citations'])}")
    
    # Create markdown version
    markdown_report = await report_writer.create_markdown_report(report)
    print(f"  - Markdown length: {len(markdown_report)} characters")

if __name__ == "__main__":
    asyncio.run(test_report_writer())
