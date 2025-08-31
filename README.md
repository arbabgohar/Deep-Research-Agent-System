# Deep Research Agent System

A sophisticated multi-agent research system inspired by OpenAI Deep Research, Anthropic Research, and Google Deep Research. This system can handle complex research questions by breaking them down into manageable tasks, conducting parallel research, evaluating sources, detecting conflicts, and synthesizing findings into professional reports.

## 🚀 Features

### Core Capabilities
- **Research Planning**: Breaks complex questions into manageable research tasks
- **Parallel Research**: Multiple specialized agents work simultaneously
- **Source Quality Assessment**: Evaluates reliability of information sources
- **Conflict Detection**: Identifies and highlights conflicting information
- **Research Synthesis**: Combines findings into organized insights
- **Professional Reporting**: Generates comprehensive reports with citations
- **Personalization**: Adapts research to user profiles and preferences

### Multi-Agent Architecture
- **Planning Agent**: Creates research plans and task breakdowns
- **Fact Finder Agent**: Specializes in finding factual information
- **Source Checker Agent**: Evaluates source quality and reliability
- **Conflict Detector Agent**: Identifies contradictions between sources
- **Synthesis Agent**: Combines findings into coherent insights
- **Report Writer Agent**: Creates professional research reports

## 📋 Requirements

- Python 3.10+
- API keys for LLM providers (OpenAI or Anthropic)
- API keys for search providers (Tavily recommended, DuckDuckGo as fallback)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Deep-Research-Agent-System
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```env
   # LLM Provider Keys
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   
   # Search Provider Keys
   TAVILY_API_KEY=your_tavily_api_key_here
   SEARCH_API_KEY=your_search_api_key_here
   
   # Configuration
   DEFAULT_LLM_PROVIDER=openai
   DEFAULT_SEARCH_PROVIDER=tavily
   LLM_MODEL=gpt-4
   LLM_TEMPERATURE=0.3
   LLM_MAX_TOKENS=2000
   SEARCH_MAX_RESULTS=10
   LOG_LEVEL=INFO
   ```

## 🚀 Quick Start

### Basic Usage

```python
import asyncio
from deep_research_system import DeepResearchSystem

async def main():
    # Initialize the system
    research_system = DeepResearchSystem()
    
    # Conduct research
    question = "What are the benefits of electric cars?"
    result = await research_system.conduct_research(question)
    
    # Print results
    print(f"Research Question: {question}")
    print(f"Summary: {result['summary']}")
    print(f"Sources: {len(result['sources'])} found")
    print(f"Conflicts: {len(result['conflicts'])} detected")

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Usage with User Profile

```python
import asyncio
from deep_research_system import DeepResearchSystem

async def main():
    # Initialize the system
    research_system = DeepResearchSystem()
    
    # Create user profile for personalization
    user_profile = {
        "name": "Alex",
        "city": "San Francisco",
        "topic": "Technology and AI",
        "expertise_level": "Intermediate"
    }
    
    # Conduct research with personalization
    question = "How has artificial intelligence changed healthcare from 2020 to 2024?"
    result = await research_system.conduct_research(question, user_profile)
    
    # Access detailed results
    print(f"Title: {result['title']}")
    print(f"Executive Summary: {result['executive_summary']}")
    print(f"Key Findings: {len(result['key_findings'])}")
    print(f"Conclusions: {len(result['conclusions'])}")
    print(f"Recommendations: {len(result['recommendations'])}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Streaming Research with Progress Updates

```python
import asyncio
from deep_research_system import DeepResearchSystem

async def main():
    # Initialize the system
    research_system = DeepResearchSystem()
    
    # Conduct research with streaming updates
    question = "Compare the environmental impact of electric vs hybrid vs gas cars"
    
    async for update in research_system.research_with_streaming(question):
        if update['phase'] == 'planning':
            print(f"Planning: {update['message']}")
        elif update['phase'] == 'research':
            print(f"Research: {update['update']}")
        elif update['phase'] == 'synthesis':
            print(f"Synthesis: {update['message']}")
        elif update['phase'] == 'complete':
            print("Research completed!")
            report = update['report']
            print(f"Final report: {report['title']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📊 Test Challenges

The system is designed to handle research questions of increasing complexity:

### Level 1: Basic Research
- **Question**: "What are the benefits of electric cars?"
- **Focus**: Single topic, multiple sources
- **Expected**: Clear benefits list with supporting evidence

### Level 2: Comparative Analysis
- **Question**: "Compare the environmental impact of electric vs hybrid vs gas cars"
- **Focus**: Multiple topics, comparison needed
- **Expected**: Structured comparison with data points

### Level 3: Complex Investigation
- **Question**: "How has artificial intelligence changed healthcare from 2020 to 2024, including both benefits and concerns from medical professionals?"
- **Focus**: Time-based analysis, multiple perspectives, conflict detection
- **Expected**: Temporal analysis with conflicting viewpoints identified

### Level 4: Expert Challenge
- **Question**: "Analyze the economic impact of remote work policies on small businesses vs large corporations, including productivity data and employee satisfaction trends"
- **Focus**: Multi-dimensional analysis, data synthesis, professional-level research
- **Expected**: Comprehensive analysis with actionable insights

## 🏗️ System Architecture

### Core Components

1. **`deep_research_system.py`** - Main coordinator that orchestrates all agents
2. **`planning_agent.py`** - Breaks complex questions into research tasks
3. **`research_agents.py`** - Specialized agents for fact-finding, source checking, and conflict detection
4. **`synthesis_agent.py`** - Combines findings into organized insights
5. **`report_writer.py`** - Generates professional research reports
6. **`llm_client.py`** - Handles communication with LLM providers
7. **`search_client.py`** - Manages web search functionality
8. **`utils.py`** - Utility functions and configuration management

### Agent Roles

#### Planning Agent
- Analyzes question complexity
- Creates research task breakdown
- Optimizes research plan
- Validates plan completeness

#### Research Team
- **Fact Finder**: Searches for factual information
- **Source Checker**: Evaluates source quality and reliability
- **Conflict Detector**: Identifies contradictions between sources

#### Synthesis Agent
- Identifies themes and patterns
- Detects trends and emerging patterns
- Generates key insights
- Creates conclusions and recommendations

#### Report Writer
- Generates professional report structure
- Creates executive summaries
- Manages citations and references
- Personalizes content for users

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `ANTHROPIC_API_KEY` | Anthropic API key | Optional |
| `TAVILY_API_KEY` | Tavily search API key | Required |
| `SEARCH_API_KEY` | Generic search API key | Optional |
| `DEFAULT_LLM_PROVIDER` | Preferred LLM provider | `openai` |
| `DEFAULT_SEARCH_PROVIDER` | Preferred search provider | `tavily` |
| `LLM_MODEL` | LLM model to use | `gpt-4` |
| `LLM_TEMPERATURE` | LLM temperature setting | `0.3` |
| `LLM_MAX_TOKENS` | Maximum tokens for LLM responses | `2000` |
| `SEARCH_MAX_RESULTS` | Maximum search results per query | `10` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Configuration File

You can also use a JSON configuration file:

```json
{
  "llm_provider": "openai",
  "search_provider": "tavily",
  "model": "gpt-4",
  "temperature": 0.3,
  "max_tokens": 2000,
  "max_results": 10,
  "log_level": "INFO"
}
```

## 📈 Performance Optimization

### Parallel Processing
- Research tasks are executed in parallel for faster results
- Multiple search queries run simultaneously
- Source evaluation happens concurrently

### Caching
- Search results can be cached to avoid repeated API calls
- User profiles are persisted for personalization
- Configuration is cached for faster startup

### Error Handling
- Graceful fallbacks when APIs are unavailable
- Retry mechanisms for failed requests
- Comprehensive logging for debugging

## 🔧 Customization

### Adding New Search Providers

```python
# In search_client.py
class CustomSearchProvider:
    async def search(self, query: str, max_results: int):
        # Implement your search logic
        pass

# Register in SearchClient._initialize_clients()
elif self.provider == "custom":
    self.client = CustomSearchProvider()
```

### Adding New LLM Providers

```python
# In llm_client.py
async def _get_custom_completion(self, prompt: str, system_prompt: Optional[str] = None):
    # Implement your LLM integration
    pass

# Register in LLMClient._initialize_clients()
elif self.provider == "custom":
    self.client = CustomLLMClient()
```

### Custom Agent Specialization

```python
# Create a specialized agent
class CustomResearchAgent:
    def __init__(self, config):
        self.config = config
        self.llm_client = LLMClient(config)
    
    async def research_task(self, task):
        # Implement custom research logic
        pass

# Add to ResearchTeam
self.custom_agent = CustomResearchAgent(config)
```

## 📝 Output Formats

### JSON Report Structure

```json
{
  "title": "Research Report Title",
  "executive_summary": "Brief overview of findings",
  "methodology": "Research approach description",
  "key_findings": ["Finding 1", "Finding 2", "..."],
  "detailed_analysis": {
    "themes": "Theme analysis",
    "trends": "Trend analysis",
    "source_analysis": "Source quality analysis",
    "conflict_analysis": "Conflict analysis"
  },
  "conclusions": ["Conclusion 1", "Conclusion 2", "..."],
  "recommendations": ["Recommendation 1", "Recommendation 2", "..."],
  "citations": [
    {
      "id": "[1]",
      "reference": "Full citation text"
    }
  ],
  "metadata": {
    "research_question": "Original question",
    "report_generated": "2024-01-01T12:00:00",
    "total_sources": 15,
    "high_quality_sources": 12,
    "conflicts_detected": 2,
    "confidence_level": 0.85
  }
}
```

### Markdown Report

The system can also generate markdown-formatted reports with proper structure and formatting.

## 🧪 Testing

### Running Tests

```bash
# Test individual components
python -m pytest tests/

# Test specific agent
python planning_agent.py
python research_agents.py
python synthesis_agent.py
python report_writer.py

# Test full system
python deep_research_system.py
```

### Test Questions

Use the provided test questions to validate system performance:

1. **Level 1**: "What are the benefits of electric cars?"
2. **Level 2**: "Compare the environmental impact of electric vs hybrid vs gas cars"
3. **Level 3**: "How has artificial intelligence changed healthcare from 2020 to 2024?"
4. **Level 4**: "Analyze the economic impact of remote work policies on small businesses vs large corporations"

## 🐛 Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure all required API keys are set in environment variables
   - Check API key validity and quotas
   - Verify provider-specific requirements

2. **Search Failures**
   - Check internet connectivity
   - Verify search provider API status
   - Review rate limits and quotas

3. **LLM Errors**
   - Check LLM provider API status
   - Verify model availability
   - Review token limits and costs

4. **Performance Issues**
   - Reduce `max_results` for faster searches
   - Lower `max_tokens` for quicker responses
   - Use streaming mode for real-time feedback

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python deep_research_system.py
```

## 📚 API Reference

### DeepResearchSystem

#### Methods

- `conduct_research(question, user_profile=None)` - Conduct complete research
- `research_with_streaming(question, user_profile=None)` - Research with progress updates

#### Parameters

- `question` (str): Research question to investigate
- `user_profile` (dict, optional): User profile for personalization

#### Returns

- Dictionary containing complete research report

### Configuration

#### LLM Configuration

```python
config = {
    "llm_provider": "openai",  # or "anthropic"
    "model": "gpt-4",
    "temperature": 0.3,
    "max_tokens": 2000
}
```

#### Search Configuration

```python
config = {
    "search_provider": "tavily",  # or "duckduckgo"
    "max_results": 10
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by OpenAI Deep Research, Anthropic Research, and Google Deep Research
- Built with modern Python async/await patterns
- Uses industry-standard LLM and search APIs

## 📞 Support

For questions, issues, or contributions:

1. Check the troubleshooting section
2. Review existing issues
3. Create a new issue with detailed information
4. Include system configuration and error logs

---

**Happy Researching! 🚀**
