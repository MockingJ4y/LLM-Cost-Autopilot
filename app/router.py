import time
from litellm import acompletion  # type: ignore[import]
from app.config import MODEL_REGISTRY

class ComplexityClassifier:
    def __init__(self):
        self.complex_keywords = ["analyze", "compare", "evaluate", "optimise", "prove", "code"]
        self.moderate_keywords = ["summarize", "extract", "classify", "translate"]

    def predict_tier_with_reason(self, prompt: str) -> tuple[str, str]:
        prompt_lower = prompt.lower()
        token_estimate = len(prompt_lower.split())
        
        for k in self.complex_keywords:
            if k in prompt_lower:
                return "tier_3", f"Contains complex keyword: '{k}'"
        if token_estimate > 500:
            return "tier_3", f"High token estimate: {token_estimate} > 500"
            
        for k in self.moderate_keywords:
            if k in prompt_lower:
                return "tier_2", f"Contains moderate keyword: '{k}'"
        if token_estimate > 150:
            return "tier_2", f"Moderate token estimate: {token_estimate} > 150"
            
        return "tier_1", "Simple prompt, short length, no complex keywords"

    def predict_tier(self, prompt: str) -> str:
        # Keep original for backward compatibility
        tier, _ = self.predict_tier_with_reason(prompt)
        return tier

async def send_unified_request(prompt: str, model_key: str):
    config = MODEL_REGISTRY[model_key]
    start_time = time.time()
    
    try:
        response = await acompletion(
            model=config.model_id,
            messages=[{"role": "user", "content": prompt}]
        )
        latency = (time.time() - start_time) * 1000
        
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        cost = (prompt_tokens / 1_000_000) * config.input_cost_per_m + \
               (completion_tokens / 1_000_000) * config.output_cost_per_m

        return {
            "text": response.choices[0].message.content,
            "cost": cost,
            "latency_ms": latency
        }
    except Exception as e:
        return {"error": str(e), "cost": 0, "latency_ms": 0}