from dataclasses import dataclass
from typing import Dict

@dataclass
class ModelConfig:
    provider: str
    model_id: str
    input_cost_per_m: float
    output_cost_per_m: float
    quality_tier: str

# An expanded registry with multiple providers for comparison
MODEL_REGISTRY: Dict[str, ModelConfig] = {
    # --- GROQ (Free / Ultra-Fast) ---
    "llama3-8b": ModelConfig("groq", "groq/llama-3.1-8b-instant", 0.05, 0.08, "low"),
    "mixtral-8x7b": ModelConfig("groq", "groq/mixtral-8x7b-32768", 0.24, 0.24, "medium"),
    "llama3-70b": ModelConfig("groq", "groq/llama-3.3-70b-versatile", 0.59, 0.79, "high"),
    
    # --- DEEPSEEK (Cost-Efficiency Champion) ---
    "deepseek-chat": ModelConfig("deepseek", "deepseek/deepseek-chat", 0.14, 0.28, "low"),
    "deepseek-reasoner": ModelConfig("deepseek", "deepseek/deepseek-reasoner", 1.74, 3.48, "high"),

    # --- MISTRAL AI (European Powerhouse) ---
    "mistral-small": ModelConfig("mistral", "mistral/mistral-small-latest", 0.10, 0.30, "medium"),
    "mistral-large": ModelConfig("mistral", "mistral/mistral-large-latest", 2.00, 6.00, "high"),
    
    # --- OPENAI (Industry Standard) ---
    "gpt-4o-mini": ModelConfig("openai", "gpt-4o-mini", 0.15, 0.60, "medium"),
    "gpt-4o": ModelConfig("openai", "gpt-4o", 2.50, 10.00, "high")
}

# The Active Routing Map
# You can mix and match! For example, Tier 1 = DeepSeek, Tier 2 = Mistral, Tier 3 = OpenAI
# The Active Routing Map
TIER_ROUTING = {
    "tier_1": "llama3-8b",       # Switch back to Groq (which we know works!)
    "tier_2": "mistral-small",   # Mistral handles Tier 2
    "tier_3": "gpt-4o-mini"      # OpenAI handles Tier 3
}