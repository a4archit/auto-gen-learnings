
## Dependencies
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance 

# -----------------------------
# Load PDF
# -----------------------------
loader = PyPDFLoader(
    "/home/archit-elitebook/Documents/Rockets.pdf"
)
documents = loader.load()

# -----------------------------
# Split text
# -----------------------------
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
texts = text_splitter.split_documents(documents)

# -----------------------------
# Embeddings
# -----------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-large-en",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True}
)

print("✅ BGE embeddings loaded")

# -----------------------------
# Qdrant Client (EXPLICIT)
# -----------------------------
client = QdrantClient(
    url="http://localhost:6333"
)


# -----------------------------
# CREATE COLLECTION (THIS WAS MISSING)
# -----------------------------
client.recreate_collection(
    collection_name="vector_db",
    vectors_config=VectorParams(
        size=1024,                 # bge-large-en embedding size
        distance=Distance.COSINE
    )
)

print("✅ Qdrant collection created")


# -----------------------------
# Create Vector Store (SAFE PATH)
# -----------------------------
qdrant = QdrantVectorStore(
    client=client,
    collection_name="vector_db",
    embedding=embeddings
)

qdrant.add_documents(texts)

print("✅ Vector DB successfully created")
