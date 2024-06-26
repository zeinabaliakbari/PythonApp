import streamlit as st
import sys
import os
from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain_community.llms import LlamaCpp
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
# Setting CUDA_VISIBLE_DEVICES
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

# Loading PDF documents
loader = PyPDFDirectoryLoader("GermanStories")
data = loader.load()

# Splitting documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
text_chunks = text_splitter.split_documents(data[:10])  # Load fewer documents initially

# Setting up HuggingFace embeddings
embeddings_model = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(model_name=embeddings_model)

# Creating FAISS vector store
vector_store = FAISS.from_documents(text_chunks, embedding=embeddings)

# Defining the ChatPromptTemplate
prompt = ChatPromptTemplate.from_template("""
Answer the questions based on the provided context only.
Please provide the most accurate response based on the question
<context>
{context}
<context>
query:{query}

""")

# Creating the LLM 
llm =  Ollama(model="llama3:70b")

# Creating the retrieval chain
generator_llm =  llm
critic_llm = llm
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


generator = TestsetGenerator.from_langchain(
    generator_llm,
    critic_llm,
    embeddings
)

distributions = {
    simple: 0.5,
    multi_context: 0.4,
    reasoning: 0.1
}

# generate testset
#testset = generator.generate_with_llama_index_docs(documents, 100,distributions)


testset = generator.generate_with_langchain_docs(text_chunks, test_size=10, distributions=distributions)
testset.to_pandas()
