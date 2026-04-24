import os
import json
from dotenv import load_dotenv
from datasets import Dataset

from ragas import evaluate
from ragas.metrics import Faithfulness, AnswerRelevancy, ContextRecall

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

from src.chain import ask_atliq_bot

load_dotenv()

def run_evaluation():
    print("Starting Automated Ragas Evaluation...")
    
    grader_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    grader_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    test_cases = [
        {
            "question": "What is the parental leave policy?",
            "ground_truth": "Primary carers are entitled to 12 weeks of paid leave, and secondary carers are entitled to 4 weeks. It is paid at 100% of base salary and requires 6 months of continuous tenure.",
            "role": ["hr"]
        },
        {
            "question": "What was the Q1 revenue and marketing spend?",
            "ground_truth": "The Q1 revenue was $4.2M and the marketing spend was $320K.",
            "role": ["finance"]
        }
    ]
    
    data = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": []
    }
    
    print("Gathering responses from AtliQ Bot...")
    for tc in test_cases:
        print(f"Testing: '{tc['question']}'")
        
        import sys
        original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        
        response = ask_atliq_bot(tc["question"], tc["role"])
        
        sys.stdout = original_stdout 
        
        data["question"].append(tc["question"])
        data["answer"].append(response["answer"])
        data["contexts"].append(response["context_texts"])
        data["ground_truth"].append(tc["ground_truth"])

    dataset = Dataset.from_dict(data)

    print("\nGrading the bot's performance (this takes 30-60 seconds)...")
    
    result = evaluate(
        dataset=dataset,
        metrics=[Faithfulness(), AnswerRelevancy(), ContextRecall()],
        llm=grader_llm,
        embeddings=grader_embeddings
    )
    
    # FIX: Safely extract and average the lists directly from the result object
    def get_average(metric_name):
        try:
            val = result[metric_name]
            if isinstance(val, list):
                # Filter out any None/Empty values just in case
                valid_scores = [v for v in val if v is not None]
                return sum(valid_scores) / len(valid_scores) if valid_scores else 0.0
            return float(val)
        except Exception:
            return 0.0

    # Build our own clean dictionary
    final_scores = {
        "faithfulness": get_average("faithfulness"),
        "answer_relevancy": get_average("answer_relevancy"),
        "context_recall": get_average("context_recall")
    }

    print("\n--- Final Evaluation Scores ---")
    print(f"Faithfulness:     {final_scores['faithfulness']:.2f} (Target: > 0.85)")
    print(f"Answer Relevancy: {final_scores['answer_relevancy']:.2f} (Target: > 0.80)")
    print(f"Context Recall:   {final_scores['context_recall']:.2f} (Target: > 0.75)")
    
    os.makedirs("eval_results", exist_ok=True)
    with open("eval_results/ragas_scores.json", "w") as f:
        json.dump(final_scores, f, indent=4)
        
    print("\nScores successfully saved to eval_results/ragas_scores.json!")

if __name__ == "__main__":
    run_evaluation()