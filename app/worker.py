from app.router import send_unified_request
from app.database import update_evaluation

async def queue_async_evaluation(log_id: int, prompt: str, assigned_tier: str, response_text: str):
    if assigned_tier == "tier_3":
        # We don't evaluate the highest tier model against itself
        update_evaluation(log_id, score=5, escalated=False)
        return

    eval_prompt = f"""
    Rate the quality of this response to the prompt on a scale of 1 to 5. 
    Only output a single integer.
    Prompt: {prompt}
    Response: {response_text}
    """
    
    # Swapped from gpt-4o-mini to llama3-70b so it uses your Groq key
    judge_response = await send_unified_request(eval_prompt, "llama3-70b")
    
    try:
        score_text = judge_response.get("text", "").strip()
        # Find the first number in the output
        score = int(''.join(filter(str.isdigit, score_text))[:1]) 
    except:
        score = 3 
        
    escalated = score <= 2
    update_evaluation(log_id, score, escalated)