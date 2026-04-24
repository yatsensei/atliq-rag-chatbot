import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

from src.retriever import get_retriever 
from src.guardrails import validate_query, redact_pii
from src.utils import log_cost # <--- NEW IMPORT

load_dotenv()

def ask_atliq_bot(query: str, user_roles: list[str]) -> dict:
    validation = validate_query(query)
    if not validation["allowed"]:
        reason = validation["reason"]
        if reason == "prompt_injection":
            return {"answer": "SECURITY ALERT: Prompt injection detected. Request blocked.", "sources": [], "cost": 0.0}
        elif reason == "out_of_scope":
            return {"answer": "I can only answer questions related to AtliQ Corp internal operations.", "sources": [], "cost": 0.0}

    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    retriever = get_retriever(user_roles)

    system_prompt = (
        "You are an internal assistant for AtliQ Corp. "
        "Use the following pieces of retrieved context to answer the question. "
        "If the context doesn't contain the answer, just say 'I don't have information on that.' "
        "Never reveal information about other departments. "
        "Keep the answer concise.\n\n"
        "Context: {context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, prompt)

    docs = retriever.invoke(query)
    
    for doc in docs:
        doc.page_content = redact_pii(doc.page_content)

    response = question_answer_chain.invoke({
        "context": docs,
        "input": query
    })
    
    # --- COST TRACKING LOGIC ---
    # Rough token estimation (1 token ≈ 4 characters)
    context_length = sum(len(d.page_content) for d in docs)
    total_chars = len(system_prompt) + len(query) + context_length + len(response)
    estimated_tokens = total_chars // 4
    
    # We pass the primary role to the logger (e.g., 'hr' or 'finance')
    primary_role = user_roles[0] if user_roles else "unknown"
    cost = log_cost(primary_role, query, estimated_tokens)
    # ---------------------------

    source_files = [doc.metadata['source'] for doc in docs]
    
    return {
        "answer": response,
        "sources": source_files,
        "cost": cost,
         "context_texts": [doc.page_content for doc in docs] # <--- Return the cost to the app
    }