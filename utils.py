"""
Utilities - Helper functions and configuration management
"""

import os
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

def setup_logging(name: str, level: str = "INFO") -> logging.Logger:
    """
    Set up logging for a component.
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        Configured logger
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid adding handlers if they already exist
    if logger.handlers:
        return logger
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from file or environment variables.
    
    Args:
        config_path: Path to config file (optional)
        
    Returns:
        Configuration dictionary
    """
    
    config = {}
    
    # Load from file if provided
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config.update(json.load(f))
        except Exception as e:
            print(f"Warning: Failed to load config file {config_path}: {e}")
    
    # Load from environment variables
    env_config = {
        "llm_provider": os.getenv("DEFAULT_LLM_PROVIDER", "openai"),
        "search_provider": os.getenv("DEFAULT_SEARCH_PROVIDER", "tavily"),
        "model": os.getenv("LLM_MODEL", "gpt-4"),
        "temperature": float(os.getenv("LLM_TEMPERATURE", "0.3")),
        "max_tokens": int(os.getenv("LLM_MAX_TOKENS", "2000")),
        "max_results": int(os.getenv("SEARCH_MAX_RESULTS", "10")),
        "log_level": os.getenv("LOG_LEVEL", "INFO")
    }
    
    config.update(env_config)
    
    return config

def save_config(config: Dict[str, Any], config_path: str) -> bool:
    """
    Save configuration to file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to save config file
        
    Returns:
        True if successful, False otherwise
    """
    
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def validate_api_keys() -> Dict[str, bool]:
    """
    Validate that required API keys are set.
    
    Returns:
        Dictionary mapping service names to availability status
    """
    
    api_keys = {
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "tavily": bool(os.getenv("TAVILY_API_KEY")),
        "search_api": bool(os.getenv("SEARCH_API_KEY"))
    }
    
    return api_keys

def create_user_profile(name: str, city: str, topic: str, expertise_level: str = "Intermediate") -> Dict[str, Any]:
    """
    Create a user profile for personalization.
    
    Args:
        name: User's name
        city: User's city
        topic: User's area of interest
        expertise_level: User's expertise level
        
    Returns:
        User profile dictionary
    """
    
    return {
        "name": name,
        "city": city,
        "topic": topic,
        "expertise_level": expertise_level,
        "created_at": datetime.now().isoformat(),
        "preferences": {
            "detail_level": "comprehensive",
            "citation_style": "academic",
            "language": "english"
        }
    }

def format_timestamp(timestamp: Optional[float] = None) -> str:
    """
    Format timestamp for display.
    
    Args:
        timestamp: Unix timestamp (optional, uses current time if not provided)
        
    Returns:
        Formatted timestamp string
    """
    
    if timestamp is None:
        timestamp = datetime.now().timestamp()
    
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def extract_domain_from_url(url: str) -> str:
    """
    Extract domain from URL.
    
    Args:
        url: URL to extract domain from
        
    Returns:
        Domain string
    """
    
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix
        if domain.startswith("www."):
            domain = domain[4:]
        
        return domain
    except:
        return "unknown"

def calculate_confidence_score(sources: list, conflicts: list, findings_count: int) -> float:
    """
    Calculate overall confidence score for research results.
    
    Args:
        sources: List of sources
        conflicts: List of conflicts
        findings_count: Number of findings
        
    Returns:
        Confidence score between 0 and 1
    """
    
    if not sources:
        return 0.0
    
    # Base score from source quality
    high_quality_sources = sum(1 for s in sources if s.get('reliability') == 'high')
    source_quality_score = high_quality_sources / len(sources)
    
    # Penalty for conflicts
    conflict_penalty = min(0.3, len(conflicts) * 0.1)
    
    # Bonus for multiple findings
    findings_bonus = min(0.2, findings_count * 0.05)
    
    confidence = source_quality_score - conflict_penalty + findings_bonus
    return max(0.0, min(1.0, confidence))

def create_research_summary(findings: list, sources: list, conflicts: list) -> str:
    """
    Create a brief summary of research results.
    
    Args:
        findings: List of research findings
        sources: List of sources
        conflicts: List of conflicts
        
    Returns:
        Summary string
    """
    
    summary_parts = []
    
    # Findings summary
    if findings:
        summary_parts.append(f"Found {len(findings)} key findings")
    
    # Sources summary
    if sources:
        high_quality = sum(1 for s in sources if s.get('reliability') == 'high')
        summary_parts.append(f"Consulted {len(sources)} sources ({high_quality} high-quality)")
    
    # Conflicts summary
    if conflicts:
        summary_parts.append(f"Detected {len(conflicts)} conflicts requiring attention")
    
    # Confidence
    confidence = calculate_confidence_score(sources, conflicts, len(findings))
    summary_parts.append(f"Overall confidence: {confidence:.1%}")
    
    return ". ".join(summary_parts) + "."

def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to directory
        
    Returns:
        True if successful, False otherwise
    """
    
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {directory_path}: {e}")
        return False

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for safe file system usage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    
    import re
    
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    
    # Limit length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    
    return sanitized

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"

def create_progress_bar(current: int, total: int, width: int = 50) -> str:
    """
    Create a text-based progress bar.
    
    Args:
        current: Current progress value
        total: Total value
        width: Width of progress bar
        
    Returns:
        Progress bar string
    """
    
    if total == 0:
        return "[" + " " * width + "] 0%"
    
    progress = current / total
    filled_width = int(width * progress)
    
    bar = "[" + "=" * filled_width + " " * (width - filled_width) + "]"
    percentage = f" {progress:.1%}"
    
    return bar + percentage

def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    
    import re
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def generate_report_filename(question: str, timestamp: Optional[datetime] = None) -> str:
    """
    Generate a filename for a research report.
    
    Args:
        question: Research question
        timestamp: Timestamp for filename (optional)
        
    Returns:
        Generated filename
    """
    
    if timestamp is None:
        timestamp = datetime.now()
    
    # Create base filename from question
    base_name = question.lower()
    base_name = base_name.replace("?", "").replace(" ", "_")
    base_name = sanitize_filename(base_name)
    
    # Add timestamp
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
    
    return f"research_report_{base_name}_{timestamp_str}.json"

def load_user_profiles(profiles_path: str = "user_profiles.json") -> Dict[str, Dict[str, Any]]:
    """
    Load user profiles from file.
    
    Args:
        profiles_path: Path to profiles file
        
    Returns:
        Dictionary of user profiles
    """
    
    if not os.path.exists(profiles_path):
        return {}
    
    try:
        with open(profiles_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading user profiles: {e}")
        return {}

def save_user_profile(profile: Dict[str, Any], profiles_path: str = "user_profiles.json") -> bool:
    """
    Save user profile to file.
    
    Args:
        profile: User profile dictionary
        profiles_path: Path to profiles file
        
    Returns:
        True if successful, False otherwise
    """
    
    try:
        profiles = load_user_profiles(profiles_path)
        profiles[profile['name']] = profile
        
        with open(profiles_path, 'w') as f:
            json.dump(profiles, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving user profile: {e}")
        return False

# Example usage
def test_utilities():
    """Test utility functions"""
    
    print("Testing Utilities...")
    
    # Test logging setup
    logger = setup_logging("test_utils")
    logger.info("Logger test successful")
    
    # Test config loading
    config = load_config()
    print(f"Loaded config: {config}")
    
    # Test API key validation
    api_keys = validate_api_keys()
    print(f"API keys status: {api_keys}")
    
    # Test user profile creation
    profile = create_user_profile("Alex", "San Francisco", "AI Research")
    print(f"User profile: {profile}")
    
    # Test text truncation
    long_text = "This is a very long text that needs to be truncated for display purposes"
    truncated = truncate_text(long_text, 30)
    print(f"Truncated text: {truncated}")
    
    # Test confidence calculation
    sources = [{"reliability": "high"}, {"reliability": "medium"}]
    conflicts = []
    confidence = calculate_confidence_score(sources, conflicts, 3)
    print(f"Confidence score: {confidence:.2f}")
    
    # Test progress bar
    progress = create_progress_bar(7, 10)
    print(f"Progress bar: {progress}")
    
    # Test filename generation
    filename = generate_report_filename("What are the benefits of electric cars?")
    print(f"Generated filename: {filename}")

if __name__ == "__main__":
    test_utilities()
