import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# 1. Load the secret keys from the .env file
load_dotenv()

# 2. Check if the Groq key was loaded properly
groq_key = os.getenv("GROQ_API_KEY")
if not groq_key or groq_key == "your_groq_key_here":
    print("Error: GROQ_API_KEY is missing or invalid in the .env file.")
    exit()

print("API Key loaded successfully! Connecting to Groq...")

# 3. Initialize the LLM (Llama 3.1 8B)
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0  # 0 means strictly factual, no creative guessing
)

# 4. Send a test message
try:
    response = llm.invoke("Hello! Are you online and receiving this?")
    print("\n--- AI Response ---")
    print(response.content)
    print("-------------------")
    print("\nSuccess! Phase 1 is complete.")
except Exception as e:
    print(f"\nAn error occurred: {e}")