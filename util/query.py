from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import VLLMOpenAI
from langchain_ollama.llms import OllamaLLM
from langchain_community.llms import Ollama
from operator import itemgetter
from util import agentic
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

chat_history_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a financial analysis assistant with expertise in interpreting financial reports and economic data.

            Previous conversation:
            {history}

            Use the following context, if any was returned, to help you answer your question:
            {context}
            - -

            Guidelines:
            1. Prioritize any returned context in answering the user question. 
            2. If the context contains financial data, cite specific figures, percentages, and trends.
            3. When referencing information, always place the citation at the end of the relevant statement, and include the document and page number if available.
            4. If the question is unclear or ambiguous, ask for clarification before providing a response.
            5. Do not repeat or summarize the response after the citation. Ensure the citation is the last element in the response.
            6. Do not include conversation history, your thought patterns, or previous responses in the response output.
            7. Do not include or respond with any harmful or hurtful content.
            8. Be concise, but provide a thoughtful response. 

            Remember: Accuracy is critical when discussing financial information.""",
                    ),
                    ("human", "{question}"),
    ]
)


def format_docs(docs):
    formatted_docs = []
    for i, doc in enumerate(docs):
        # Extract metadata if available
        metadata = getattr(doc, "metadata", {})
        source = metadata.get("source", "Unknown source")
        page = metadata.get("page", "Unknown page")

        # Format the document with metadata
        formatted_doc = f"[Document {i+1}] "
        if "page" in metadata:
            formatted_doc += f"Page {page}: "
        formatted_doc += doc.page_content

        formatted_docs.append(formatted_doc)

    return "\n\n" + "-" * 50 + "\n\n".join(formatted_docs) + "\n\n" + "-" * 50


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
    output_parser = StrOutputParser()

    retriever = db.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"score_threshold": 0.7, "k": 5},
    )

    context = itemgetter("question") | retriever | format_docs
    first_step = RunnablePassthrough.assign(context=context)
    chain = first_step | promp_template | llm_model | output_parser

    return chain

def agentic_graph_streamlit():
    return agentic.invoke_graph()
