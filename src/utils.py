import json
import os
from datetime import datetime

# Groq Llama 3.1 8B is incredibly cheap, roughly $0.05 per 1M tokens.
PRICE_PER_TOKEN = 0.00000005 

def log_cost(role: str, query: str, total_tokens: int):
    """
    Calculates the cost of an LLM call and saves it to a local log file.
    """
    estimated_cost = total_tokens * PRICE_PER_TOKEN
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "role": role,
        "query": query,
        "tokens_used": total_tokens,
        "estimated_cost_usd": estimated_cost
    }
    
    # Append the log entry to our JSONL (JSON Lines) file
    log_path = os.path.join("logs", "cost_log.jsonl")
    
    # Create the directory if it doesn't exist just in case
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    with open(log_path, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
        
    return estimated_cost