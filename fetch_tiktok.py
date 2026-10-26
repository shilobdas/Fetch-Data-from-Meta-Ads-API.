import requests
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

# --- CONFIGURATION ---
# Replace these with your actual credentials from TikTok Developer Portal
TIKTOK_APP_KEY = "YOUR_TIKTOK_APP_KEY"
TIKTOK_APP_SECRET = "YOUR_TIKTOK_APP_SECRET"
TIKTOK_ACCESS_TOKEN = "YOUR_ACCESS_TOKEN" # You need to generate this via OAuth
# For now, let's try a public endpoint if available, or you might need to generate a token via the portal's "Test Tool"

# TikTok API Endpoint (Example: Fetching user video list)
# Note: TikTok APIs change frequently. Check the "API Explorer" in their dashboard for the latest endpoint.
# This is a conceptual example using the Content API v1.
API_URL = "https://open.tiktokapis.com/v2/user/@YOUR_USERNAME/videos/"

def get_tiktok_token():
    # In a real app, you exchange the Authorization Code for a token.
    # For this quick test, if you have a pre-generated token from the TikTok "API Explorer" tool:
    return TIKTOK_ACCESS_TOKEN

def fetch_tiktok_data():
    print("Fetching TikTok data...")
    # Since we don't have a live token in this snippet, we will simulate the structure
    # You MUST generate a real token in the TikTok Developer Portal "API Explorer" first.
    
    headers = {
        "Authorization": f"Bearer {TIKTOK_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Example: Fetching videos for your account
    # params = {"fields": "id,title,create_time,description,statistics"}
    # response = requests.get(API_URL, headers=headers, params=params)
    # data = response.json()
    
    # --- SIMULATION FOR DEMO ---
    # Replace this block with real API calls once you have your token
    mock_data = [
        "TikTok Video ID: 7123456789. Title: 'My Marketing Strategy'. Description: 'How I grew my account'. Views: 15000.",
        "TikTok Video ID: 7987654321. Title: 'TikTok Trends 2026'. Description: 'Top hashtags right now'. Views: 50000.",
        "TikTok Video ID: 7456123789. Title: 'RAG Bot Demo'. Description: 'Building AI chatbots'. Views: 2500."
    ]
    return mock_data

def create_vector_db(data):
    print("Creating Vector Database...")
    
    # 1. Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=10)
    chunks = text_splitter.create_documents(data)
    
    # 2. Embed and Store
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory="./tiktok_chroma")
    
    retriever = vector_store.as_retriever(search_kwargs={"k": 2})
    return retriever

def ask_tiktok_qa(retriever):
    print("--- TikTok RAG Chatbot ---")
    while True:
        query = input("\nAsk about TikTok data (or 'quit'): ")
        if query.lower() == 'quit':
            break
        
        # Retrieve relevant chunks
        docs = retriever.invoke(query)
        
        # Simple context formatting (In production, use an LLM chain like LangChain)
        context = " ".join([doc.page_content for doc in docs])
        
        print(f"\nContext found: {context}")
        print("Answer: (You need an LLM here to generate the final answer based on context)")
        # Example: "Based on the data, the video with the highest views is..."

if __name__ == "__main__":
    # 1. Fetch Data
    tiktok_data = fetch_tiktok_data()
    
    # 2. Create DB
    retriever = create_vector_db(tiktok_data)
    
    # 3. Ask Questions
    ask_tiktok_qa(retriever)