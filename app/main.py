from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from dotenv import load_dotenv

from app.router import ComplexityClassifier, send_unified_request
from app.config import TIER_ROUTING, MODEL_REGISTRY
from app.database import init_db, log_request
from app.worker import queue_async_evaluation

load_dotenv()
app = FastAPI(title="LLM Cost Autopilot")
classifier = ComplexityClassifier()

# THIS is the function that was likely missing or misaligned!
@app.on_event("startup")
def startup_event():
    init_db()

# The class must be totally separate from the @app.on_event decorator
class CompletionRequest(BaseModel):
    prompt: str

@app.post("/v1/completions")
async def route_completion(request: CompletionRequest, background_tasks: BackgroundTasks):
    # 1. Classify complexity
    tier = classifier.predict_tier(request.prompt)
    target_model = TIER_ROUTING[tier]
    
    # 2. Forward to chosen model
    response_data = await send_unified_request(request.prompt, target_model)
    
    if "error" not in response_data:
        # 3. Log the successful request
        log_id = log_request(
            prompt=request.prompt, 
            tier=tier, 
            model=target_model, 
            cost=response_data["cost"], 
            latency=response_data["latency_ms"]
        )
        
        # 4. Trigger async verification loop
        background_tasks.add_task(
            queue_async_evaluation, 
            log_id=log_id,
            prompt=request.prompt, 
            assigned_tier=tier, 
            response_text=response_data["text"]
        )
    
    return {
        "status": "success",
        "routed_model": target_model,
        "complexity_tier": tier,
        "reasoning": f"Prompt classified as {tier} based on token count and keyword heuristics.",
        "data": response_data
    }

# --- Management Endpoints (Phase 5) ---

@app.get("/v1/models")
async def get_models():
    """List all available models in the registry and their costs."""
    return {"models": MODEL_REGISTRY}

@app.get("/v1/routing-config")
async def get_routing_config():
    """Show current tier-to-model mapping."""
    return {"active_routing": TIER_ROUTING}