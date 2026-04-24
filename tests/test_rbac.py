import pytest
from src.retriever import get_retriever

# We don't need to call the LLM to test access control. 
# We just need to check if the retriever brings back the right files.

def test_hr_can_access_hr():
    retriever = get_retriever(["hr"])
    docs = retriever.invoke("What is the parental leave policy?")
    
    # Check that it found documents, and that they belong to HR
    assert len(docs) > 0
    for doc in docs:
        assert "hr" in doc.metadata["role"]

def test_finance_can_access_finance():
    retriever = get_retriever(["finance"])
    docs = retriever.invoke("What is the Q1 revenue?")
    
    assert len(docs) > 0
    for doc in docs:
        assert "finance" in doc.metadata["role"]

def test_finance_cannot_access_hr():
    retriever = get_retriever(["finance"])
    # A finance user trying to search for HR stuff
    docs = retriever.invoke("What is the parental leave policy?")
    
    # The retriever might pull finance docs that share common words, 
    # but it absolutely MUST NOT pull any HR docs.
    for doc in docs:
        assert "hr" not in doc.metadata["role"]

def test_csuite_can_access_everything():
    # C-suite is given all roles in our app
    retriever = get_retriever(["hr", "finance", "csuite"])
    
    hr_docs = retriever.invoke("parental leave")
    finance_docs = retriever.invoke("revenue")
    csuite_docs = retriever.invoke("strategic plan")
    
    assert len(hr_docs) > 0
    assert len(finance_docs) > 0
    assert len(csuite_docs) > 0

def test_unknown_role_gets_nothing():
    retriever = get_retriever(["janitor"])
    docs = retriever.invoke("What is the parental leave policy?")
    
    # An invalid role should return absolutely zero documents
    assert len(docs) == 0