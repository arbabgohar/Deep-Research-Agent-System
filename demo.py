"""
Deep Research Agent System - Demo Script
Showcases the system's capabilities with different test scenarios
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any

from deep_research_system import DeepResearchSystem
from utils import create_user_profile, setup_logging

class DeepResearchDemo:
    """Demo class for showcasing the Deep Research Agent System"""
    
    def __init__(self):
        self.logger = setup_logging("demo")
        self.research_system = DeepResearchSystem()
        
        # Test questions from the assignment
        self.test_questions = {
            "level_1": "What are the benefits of electric cars?",
            "level_2": "Compare the environmental impact of electric vs hybrid vs gas cars",
            "level_3": "How has artificial intelligence changed healthcare from 2020 to 2024, including both benefits and concerns from medical professionals?",
            "level_4": "Analyze the economic impact of remote work policies on small businesses vs large corporations, including productivity data and employee satisfaction trends"
        }
        
        # Sample user profiles
        self.user_profiles = {
            "academic": create_user_profile("Dr. Sarah Chen", "Boston", "Academic Research", "Expert"),
            "business": create_user_profile("Mike Johnson", "New York", "Business Strategy", "Intermediate"),
            "student": create_user_profile("Alex Rivera", "Austin", "Technology", "Beginner")
        }
    
    async def run_basic_demo(self):
        """Run a basic demonstration with Level 1 question"""
        
        print("\n" + "="*60)
        print("🚀 DEEP RESEARCH AGENT SYSTEM - BASIC DEMO")
        print("="*60)
        
        question = self.test_questions["level_1"]
        print(f"\n📝 Research Question: {question}")
        
        try:
            # Conduct research
            print("\n🔍 Conducting research...")
            result = await self.research_system.conduct_research(question)
            
            # Display results
            self._display_basic_results(result)
            
        except Exception as e:
            print(f"❌ Demo failed: {str(e)}")
            print("💡 Make sure you have set up your API keys in the .env file")
    
    async def run_advanced_demo(self):
        """Run an advanced demonstration with user personalization"""
        
        print("\n" + "="*60)
        print("🎯 DEEP RESEARCH AGENT SYSTEM - ADVANCED DEMO")
        print("="*60)
        
        question = self.test_questions["level_2"]
        user_profile = self.user_profiles["business"]
        
        print(f"\n📝 Research Question: {question}")
        print(f"👤 User: {user_profile['name']} ({user_profile['expertise_level']} level)")
        print(f"🏢 Context: {user_profile['city']}, {user_profile['topic']}")
        
        try:
            # Conduct research with personalization
            print("\n🔍 Conducting personalized research...")
            result = await self.research_system.conduct_research(question, user_profile)
            
            # Display detailed results
            self._display_detailed_results(result)
            
        except Exception as e:
            print(f"❌ Advanced demo failed: {str(e)}")
    
    async def run_streaming_demo(self):
        """Run a streaming demonstration with real-time updates"""
        
        print("\n" + "="*60)
        print("⚡ DEEP RESEARCH AGENT SYSTEM - STREAMING DEMO")
        print("="*60)
        
        question = self.test_questions["level_3"]
        user_profile = self.user_profiles["academic"]
        
        print(f"\n📝 Research Question: {question}")
        print(f"👤 User: {user_profile['name']} ({user_profile['expertise_level']} level)")
        print("\n🔄 Starting streaming research...")
        
        try:
            # Conduct streaming research
            async for update in self.research_system.research_with_streaming(question, user_profile):
                self._display_streaming_update(update)
            
            print("\n✅ Streaming research completed!")
            
        except Exception as e:
            print(f"❌ Streaming demo failed: {str(e)}")
    
    async def run_comparison_demo(self):
        """Run a comparison demo showing different user profiles"""
        
        print("\n" + "="*60)
        print("🔄 DEEP RESEARCH AGENT SYSTEM - COMPARISON DEMO")
        print("="*60)
        
        question = self.test_questions["level_1"]
        
        print(f"\n📝 Research Question: {question}")
        print("\n🔄 Comparing results for different user profiles...")
        
        results = {}
        
        for profile_name, profile in self.user_profiles.items():
            print(f"\n👤 Testing with {profile_name} profile: {profile['name']}")
            
            try:
                result = await self.research_system.conduct_research(question, profile)
                results[profile_name] = result
                
                print(f"✅ Completed for {profile_name}")
                
            except Exception as e:
                print(f"❌ Failed for {profile_name}: {str(e)}")
        
        # Compare results
        self._compare_results(results)
    
    def _display_basic_results(self, result: Dict[str, Any]):
        """Display basic research results"""
        
        print("\n📊 RESEARCH RESULTS")
        print("-" * 40)
        print(f"📋 Title: {result.get('title', 'N/A')}")
        print(f"📝 Summary: {result.get('summary', 'N/A')}")
        print(f"🔍 Sources: {len(result.get('sources', []))} found")
        print(f"⚠️  Conflicts: {len(result.get('conflicts', []))} detected")
        print(f"📈 Confidence: {result.get('metadata', {}).get('confidence_level', 0):.1%}")
        
        # Show key findings
        findings = result.get('key_findings', [])
        if findings:
            print(f"\n🎯 Key Findings ({len(findings)}):")
            for i, finding in enumerate(findings[:3], 1):  # Show first 3
                print(f"   {i}. {finding}")
            if len(findings) > 3:
                print(f"   ... and {len(findings) - 3} more")
    
    def _display_detailed_results(self, result: Dict[str, Any]):
        """Display detailed research results"""
        
        print("\n📊 DETAILED RESEARCH RESULTS")
        print("-" * 50)
        
        # Basic info
        print(f"📋 Title: {result.get('title', 'N/A')}")
        print(f"📝 Executive Summary: {result.get('executive_summary', 'N/A')[:200]}...")
        
        # Statistics
        metadata = result.get('metadata', {})
        print(f"\n📈 Research Statistics:")
        print(f"   • Total Sources: {metadata.get('total_sources', 0)}")
        print(f"   • High-Quality Sources: {metadata.get('high_quality_sources', 0)}")
        print(f"   • Conflicts Detected: {metadata.get('conflicts_detected', 0)}")
        print(f"   • Confidence Level: {metadata.get('confidence_level', 0):.1%}")
        
        # Key findings
        findings = result.get('key_findings', [])
        if findings:
            print(f"\n🎯 Key Findings ({len(findings)}):")
            for i, finding in enumerate(findings, 1):
                print(f"   {i}. {finding}")
        
        # Conclusions
        conclusions = result.get('conclusions', [])
        if conclusions:
            print(f"\n💡 Conclusions ({len(conclusions)}):")
            for i, conclusion in enumerate(conclusions, 1):
                print(f"   {i}. {conclusion}")
        
        # Recommendations
        recommendations = result.get('recommendations', [])
        if recommendations:
            print(f"\n🚀 Recommendations ({len(recommendations)}):")
            for i, recommendation in enumerate(recommendations, 1):
                print(f"   {i}. {recommendation}")
        
        # Citations
        citations = result.get('citations', [])
        if citations:
            print(f"\n📚 Citations ({len(citations)}):")
            for i, citation in enumerate(citations[:3], 1):  # Show first 3
                print(f"   {citation['id']} {citation['reference'][:100]}...")
            if len(citations) > 3:
                print(f"   ... and {len(citations) - 3} more citations")
    
    def _display_streaming_update(self, update: Dict[str, Any]):
        """Display streaming research updates"""
        
        phase = update.get('phase', 'unknown')
        
        if phase == 'planning':
            print(f"📋 Planning: {update.get('message', 'Creating research plan...')}")
            if update.get('complete'):
                print(f"   ✅ Created {update.get('tasks', 0)} research tasks")
        
        elif phase == 'research':
            research_update = update.get('update', {})
            update_type = research_update.get('type', 'unknown')
            
            if update_type == 'task_start':
                print(f"🔍 Research: Starting task '{research_update.get('task_title', 'Unknown')}' ({research_update.get('progress', 'N/A')})")
            elif update_type == 'task_complete':
                print(f"   ✅ Completed task: {research_update.get('task_id', 'Unknown')}")
            elif update_type == 'task_error':
                print(f"   ❌ Task failed: {research_update.get('error', 'Unknown error')}")
            elif update_type == 'evaluating_sources':
                print(f"🔍 Research: {research_update.get('message', 'Evaluating sources...')}")
            elif update_type == 'sources_evaluated':
                print(f"   ✅ Evaluated {research_update.get('count', 0)} sources")
            elif update_type == 'detecting_conflicts':
                print(f"🔍 Research: {research_update.get('message', 'Detecting conflicts...')}")
            elif update_type == 'conflicts_detected':
                print(f"   ✅ Detected {research_update.get('count', 0)} conflicts")
        
        elif phase == 'synthesis':
            print(f"🧠 Synthesis: {update.get('message', 'Synthesizing findings...')}")
            if update.get('complete'):
                print("   ✅ Synthesis completed")
        
        elif phase == 'report':
            print(f"📝 Report: {update.get('message', 'Generating final report...')}")
        
        elif phase == 'complete':
            report = update.get('report', {})
            print(f"🎉 Research completed! Report: {report.get('title', 'N/A')}")
        
        elif phase == 'error':
            print(f"❌ Error: {update.get('error', 'Unknown error')}")
    
    def _compare_results(self, results: Dict[str, Dict[str, Any]]):
        """Compare results across different user profiles"""
        
        print("\n📊 COMPARISON RESULTS")
        print("-" * 50)
        
        for profile_name, result in results.items():
            print(f"\n👤 {profile_name.upper()} Profile:")
            metadata = result.get('metadata', {})
            print(f"   • Sources: {metadata.get('total_sources', 0)}")
            print(f"   • High-Quality: {metadata.get('high_quality_sources', 0)}")
            print(f"   • Conflicts: {metadata.get('conflicts_detected', 0)}")
            print(f"   • Confidence: {metadata.get('confidence_level', 0):.1%}")
            print(f"   • Findings: {len(result.get('key_findings', []))}")
            print(f"   • Recommendations: {len(result.get('recommendations', []))}")
    
    async def save_demo_results(self, results: Dict[str, Any], filename: str = None):
        """Save demo results to file"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"demo_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n💾 Results saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save results: {str(e)}")

async def main():
    """Main demo function"""
    
    print("🎯 Deep Research Agent System - Interactive Demo")
    print("=" * 60)
    
    # Check if API keys are available
    api_keys = {
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "tavily": bool(os.getenv("TAVILY_API_KEY"))
    }
    
    print("\n🔑 API Key Status:")
    for service, available in api_keys.items():
        status = "✅ Available" if available else "❌ Missing"
        print(f"   • {service.upper()}: {status}")
    
    if not any(api_keys.values()):
        print("\n⚠️  No API keys found! Please set up your .env file with the required API keys.")
        print("   See the README.md file for setup instructions.")
        return
    
    # Create demo instance
    demo = DeepResearchDemo()
    
    # Run demos
    try:
        # Basic demo
        await demo.run_basic_demo()
        
        # Advanced demo
        await demo.run_advanced_demo()
        
        # Streaming demo
        await demo.run_streaming_demo()
        
        # Comparison demo
        await demo.run_comparison_demo()
        
        print("\n🎉 All demos completed successfully!")
        print("\n💡 To run your own research, use:")
        print("   python deep_research_system.py")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
