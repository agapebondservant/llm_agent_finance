import streamlit as st
from langchain_chroma import Chroma
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import (
    StreamlitChatMessageHistory,
)
import chromadb
import os
from util import embedding
from util import query

# Load environment variables
chroma_collection_name = os.getenv("CHROMA_COLLECTION_NAME")
embedding_model = embedding.init_embedding_model()
api_url = os.getenv("PARASOL_API_URL")
api_key = os.getenv("PARASOL_API_KEY")
model_name = os.getenv("LLM_NAME")

# Debug: Check for missing environment variables
if not chroma_collection_name or not api_url or not api_key or not model_name:
    st.write("Error: One or more environment variables are missing.")
    raise ValueError("Missing environment variables")

# Initialize LLM
llm = query.init_llm(api_url, api_key, model_name)

# Load data from vector db
client = chromadb.HttpClient(host="chroma-db", port=8000)

# # Setup Chroma DB
db = Chroma(
    client=client,
    collection_name=chroma_collection_name,
    embedding_function=embedding_model,
    collection_metadata={"hnsw:space": "cosine"},
)

# Debug: List all collections
# try:
#     collections = client.list_collections()
#     st.write("Available collections:", collections)

#     # Try to get the collection directly
#     collection = client.get_collection(name = chroma_collection_name)
#     if collection is None:
#         st.write(f"Collection '{chroma_collection_name}' does not exist.")
#     else:
#         st.write(f"Collection '{chroma_collection_name}' exists with {collection.count()} items.")
# except Exception as e:
#     st.write(f"Error accessing collections: {str(e)}")


st.title("Financial Analysis Assistant")

msgs = StreamlitChatMessageHistory(key="special_app_key")
history = StreamlitChatMessageHistory(key="chat_messages")


if len(msgs.messages) == 0:
    msgs.add_ai_message("How can I help you?")

template = query.chat_history_template

chain = query.query_rag_streamlit(db, llm, template)
chain_with_history = RunnableWithMessageHistory(
    chain,
    lambda session_id: msgs,  # Always return the instance created earlier
    input_messages_key="question",
    history_messages_key="history",
)

for msg in msgs.messages:
    st.chat_message(msg.type).write(msg.content)

if prompt := st.chat_input():
    st.chat_message("human").write(prompt)

    # Debug: Show what documents are being retrieved
    try:
        docs = db.similarity_search(prompt, k=3)
        st.write("Retrieved Documents:")
        for i, doc in enumerate(docs):
            st.write(f"Document {i+1}:")
            st.write(f"Content: {doc.page_content[:200]}...")
            st.write(f"Metadata: {doc.metadata}")
    except Exception as e:
        st.write(f"Error retrieving documents: {str(e)}")

    # As usual, new messages are added to StreamlitChatMessageHistory
    # when the Chain is called.
    try:
        config = {"configurable": {"session_id": "any"}}
        response = chain_with_history.invoke({"question": prompt}, config)
        st.chat_message("ai").write(response)
    except Exception as e:
        st.write(f"Error generating response: {str(e)}")
