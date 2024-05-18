import shelve
from dotenv import load_dotenv
import os
import time
import logging

load_dotenv()
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
# client = OpenAI(api_key=OPENAI_API_KEY)

from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")

      

from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


loader = WebBaseLoader("https://cleartax.in/s/80c-80-deductions")
documents = loader.load_and_split()
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 0)
# all_splits = text_splitter.split_documents(documents)
db = FAISS.from_documents(documents, embeddings)
