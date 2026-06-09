import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

groq_api_key = os.getenv(
    "GROQ_API_KEY"
)

# Create Groq client
client_groq = Groq(
    api_key=groq_api_key
)

# -----------------------------------
# ChromaDB Client
# -----------------------------------
client = chromadb.PersistentClient(
    path="chroma_DB"
)

collection = client.get_or_create_collection(
    name="documents"
)


# -----------------------------------
# Load Environment Variables
# -----------------------------------
load_dotenv()

groq_api_key = os.getenv(
    "GROQ_API_KEY"
)

client_groq = Groq(
    api_key=groq_api_key
)

# -----------------------------------
# Local Embedding Model
# -----------------------------------
embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# -----------------------------------
# Text Chunking
# -----------------------------------
def chunk_text(
    text,
    chunk_size=500,
    overlap=100
):
    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end]

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# -----------------------------------
# Store Document
# -----------------------------------
def store_document_in_chroma(
    text,
    file_name
):
    chunks = chunk_text(text)

    ids = [
        f"{file_name}_{i}"
        for i in range(len(chunks))
    ]

    # Create embeddings locally
    embeddings = embedding_model.encode(
        chunks
    ).tolist()

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids
    )

    return len(chunks)
# -----------------------------------
# Ask Question
# -----------------------------------
def ask_question(
    question,
    chat_history=[]
):

    # Create query embedding
    query_embedding = embedding_model.encode(
        [question]
    ).tolist()

    # Search top chunks
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3
    )

    retrieved_chunks = results[
        "documents"
    ][0]

    # Best chunk for citation
    best_chunk = retrieved_chunks[0]

    # Context for LLM
    context = "\n".join(
        retrieved_chunks
    )
    history_text = ""

    for chat in chat_history:

        if "question" in chat:
            history_text += (
               f"User: {chat['question']}\n"
        )

        if "answer" in chat:
           history_text += (
               f"Assistant: {chat['answer']}\n"
        )
    
    prompt = f"""
       You are an intelligent AI assistant.

       Your job:
        - Answer ONLY using the provided document context.
        - Also understand previous conversations.
        - If user says:
           "explain simply"
           "summarize"
           "short answer"
          then use previous answer.

       Previous Conversation:
       {history_text}

       Document Context:
       {context}

       Current Question:
       {question}

       Rules:
       - Be helpful and conversational.
       - Keep answer clear.
       - Do not hallucinate.
       - If not found in document say:
       'I could not find this in the document.'
    """

    response = client_groq.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response.choices[
        0
    ].message.content

    return {
        "answer": answer,
        "citation": best_chunk
    }