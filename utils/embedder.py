# embedder.py

from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss
import os
import pickle

# 把模型定义延迟到用的时候才加载
model = None

def load_model():
    global model
    if model is None:
        model = SentenceTransformer('models/text2vec-base-chinese',
                                    trust_remote_code=True,
                                    local_files_only=True)
    return model

def split_text(text, chunk_size=200, chunk_overlap=20):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_text(text)

def embed_text_list(text_list):
    return load_model().encode(text_list)

def build_faiss_index(text_chunks, save_path='knowledge_base/index'):
    embeddings = embed_text_list(text_chunks)
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))

    faiss.write_index(index, f"{save_path}.index")
    with open(f"{save_path}_texts.pkl", 'wb') as f:
        pickle.dump(text_chunks, f)

    print("✅ 知识库构建完成，保存成功！")
