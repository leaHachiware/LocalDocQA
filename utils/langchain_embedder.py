import os
import pickle
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# 向量模型
embedding_model = HuggingFaceEmbeddings(model_name="models/text2vec-base-chinese")

def build_faiss_with_langchain(text: str, index_dir="knowledge_base"):
    # 1. 切块
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    docs = splitter.split_documents([Document(page_content=text)])

    # 2. 构建向量数据库
    vectorstore = FAISS.from_documents(docs, embedding_model)

    # 3. 保存 index 和 文本
    os.makedirs(index_dir, exist_ok=True)
    vectorstore.save_local(index_dir)

def retrieve_similar_chunks(query: str, index_dir="knowledge_base", k=3):
    vectorstore = FAISS.load_local(index_dir, embeddings=embedding_model, allow_dangerous_deserialization=True)
    docs = vectorstore.similarity_search(query, k=k)
    return [doc.page_content for doc in docs]
