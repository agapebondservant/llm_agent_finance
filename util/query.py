from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama.llms import OllamaLLM
from operator import itemgetter
import os

from dotenv import load_dotenv

load_dotenv()

chat_history_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
    You are a financial analysis assistant with expertise in interpreting financial reports and economic data.
    
    Answer the question based ONLY on the following context:
    {context}
    - -
    
    Guidelines:
    1. Use ONLY the information provided in the context.
    2. If the context contains financial data, cite specific figures, percentages, and trends.
    3. When referencing information, mention the document and page number if available.
    4. If the question asks for an opinion or prediction not supported by the context, clarify that you can only provide information based on the given context.
    5. If there isn't sufficient context or you can't answer the question with the provided information, simply state that you don't have enough information to answer accurately.
    
    Remember: Accuracy is critical when discussing financial information.""",
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)


def format_docs(docs):
    formatted_docs = []
    for i, doc in enumerate(docs):
        # Extract metadata if available
        metadata = getattr(doc, 'metadata', {})
        source = metadata.get('source', 'Unknown source')
        page = metadata.get('page', 'Unknown page')
        
        # Format the document with metadata
        formatted_doc = f"[Document {i+1}] "
        if 'page' in metadata:
            formatted_doc += f"Page {page}: "
        formatted_doc += doc.page_content
        
        formatted_docs.append(formatted_doc)
    
    return "\n\n" + "-" * 50 + "\n\n".join(formatted_docs) + "\n\n" + "-" * 50


def init_llm():
    llm = OllamaLLM(model=os.getenv("LLM"))
    return llm


def query_rag_streamlit(Chroma_collection, llm_model, promp_template):
    """
    Query a Retrieval-Augmented Generation (RAG) system using Chroma db.
    Args:
      - query_text (str): The text to query the RAG system with.
      - prompt_template (str): Query prompt template
      inclding context and question
    Returns:
      - formatted_response (str): Formatted response including
      the generated text and sources.
      - response_text (str): The generated response text.
    """

    # Use the global format_docs function

    db = Chroma_collection

    retriever = db.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"score_threshold": 0.3, "k": 8},
    )

    context = itemgetter("question") | retriever | format_docs
    first_step = RunnablePassthrough.assign(context=context)
    chain = first_step | promp_template | llm_model

    return chain
