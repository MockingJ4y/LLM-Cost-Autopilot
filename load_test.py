import asyncio
import httpx
import random
import time

PROMPTS = [
    # Tier 1 (Simple)
    "What is the capital of Japan?",
    "Convert 50 miles to kilometers.",
    "Who wrote '1984'?",
    "What is the boiling point of water in Celsius?",
    # Tier 2 (Moderate)
    "Summarize the plot of the Lord of the Rings in two paragraphs.",
    "Classify these items into fruits and vegetables: Apple, Carrot, Banana, Broccoli.",
    "Extract the email addresses from this text: Contact john@doe.com or jane@company.org.",
    "Translate this sentence into French: 'The weather is beautiful today.'",
    # Tier 3 (Complex)
    "Analyze the socioeconomic impact of the Industrial Revolution on European agriculture.",
    "Evaluate the pros and cons of microservices vs monolithic architectures in cloud computing.",
    "Write a Python script to scrape a website and save data to a CSV, complete with error handling.",
    "Compare and contrast the monetary policies of the US Federal Reserve and the European Central Bank during the 2008 financial crisis."
]

API_URL = "http://localhost:8000/v1/completions"

async def send_request(client, prompt, index):
    print(f"[{index}] Sending prompt: {prompt[:30]}...")
    try:
        response = await client.post(API_URL, json={"prompt": prompt}, timeout=60.0)
        data = response.json()
        print(f"[{index}] Routed to: {data.get('routed_model')} | Reason: {data.get('routing_reason')}")
    except Exception as e:
        print(f"[{index}] Failed: {e}")

async def run_load_test(num_requests=50):
    print(f"Starting Load Test with {num_requests} requests...\n")
    start_time = time.time()
    
    async with httpx.AsyncClient() as client:
        tasks = []
        for i in range(num_requests):
            # Pick a random prompt
            prompt = random.choice(PROMPTS)
            tasks.append(send_request(client, prompt, i+1))
            # Slight delay to avoid completely overwhelming local resources
            await asyncio.sleep(0.2) 
            
        await asyncio.gather(*tasks)
        
    duration = time.time() - start_time
    print(f"\n✅ Load test complete in {duration:.2f} seconds!")
    print("Check your dashboard at http://localhost:8501 to see the results!")

if __name__ == "__main__":
    # You can change this number to 500 when you want the final portfolio screenshot
    asyncio.run(run_load_test(25))