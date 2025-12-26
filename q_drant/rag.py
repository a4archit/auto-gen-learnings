from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient

model_name = "BAAI/bge-large-en"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

url = "http://localhost:6333"

client = QdrantClient(
    url=url, prefer_grpc=False
)

print(client)
print("##############")

db = QdrantVectorStore(client=client, embedding=embeddings, collection_name="vector_db")

print(db)
print("######")
def main():

    while True:
        query = input("\n\n\t>> Query: ")

        if query == "exit":
            break 

        docs = db.similarity_search_with_score(query=query, k=3)
        for i in docs:
            doc, score = i
            print(f"score: {score}", f"content: {doc.page_content}", sep="\n\n**********\n")
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")








if __name__ == "__main__":

    main()



    