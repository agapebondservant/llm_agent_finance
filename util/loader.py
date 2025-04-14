import os
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_community.llms import VLLMOpenAI
from langchain_ollama.llms import OllamaLLM
from langchain_community.llms import Ollama
import sys
import traceback
import logging
from dotenv import load_dotenv
load_dotenv()
import httpx

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
logger.addHandler(handler)

def init_llm(llm_family, agentic=False):
    """
    Initializes LLM based on the family (Llama, Granite, etc) 
    and whether or not it is part of an agentic workflow.
    """
    try:
        api_url = os.getenv(f"{llm_family}_API_URL")
        
        api_key = os.getenv(f"{llm_family}_API_KEY")
        
        vllm_model_name = str(os.getenv(f"{llm_family}_API_LLM"))
        
        ollama_model_name = str(os.getenv(f"{llm_family}_OLLAMA_LLM"))
        
        vllm_params = {
            "openai_api_key": api_key, 
            "openai_api_base": api_url, 
            "model_name": vllm_model_name,
            "http_async_client": httpx.AsyncClient(verify=False),
        }
        
        ollama_params = {
            "model": ollama_model_name,
            "base_url": "http://ollama-container:11434",
        }
        
        rag_params = { 
            "temperature": 0.7,
            "max_tokens": 2048,
        }
        
        agentic_params = {
            "temperature": 0, 
            "request_timeout": 300, 
        }
        
        logger.info(f"{llm_family}\n================================\n\n\n")
        logger.info(f"vLLM model={vllm_model_name}\nOllama model={ollama_model_name}\n=============\n\n\n")
        logger.info(f"vllm_params={vllm_params}\n\nollama_params={ollama_params}\n\nrag_params={rag_params}\n\nagentic_params={agentic_params}\n\n\n")
        
        if api_url is not None and api_key is not None:
            logger.info(f"Will use vLLM for {llm_family}\n================================\n")
            llm_name = os.getenv("{llm_family}_API_LLM")
            llm = ChatOpenAI(**{**vllm_params, **agentic_params} ) if agentic else VLLMOpenAI(**{**vllm_params, **rag_params} )
        else:
            logger.info(f"Will use Ollama for {llm_family}\n================================\n")
            llm_name = os.getenv("{llm_family}_OLLAMA_LLM")
            llm = ChatOllama(**{**ollama_params, **agentic_params} ) if agentic else Ollama(**ollama_params)
    
        return llm
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise Exception(f"Could not load LLM with family={llm_family}: {str(e)}")