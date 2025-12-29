
## Dependencies 
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient







#                               Configurations 
#***********************************************************************************************************

QDRANT_URL = "http://localhost:6333" # setting url of running qdrant 
VECTOR_STORE_NAME = "vector_db"

#***********************************************************************************************************





# vector database configurations 
model_name = "BAAI/bge-large-en"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}

# creating database instance
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

# creating client that will be integrate with Qdrant vector store 
client = QdrantClient(
    url=QDRANT_URL, prefer_grpc=False
)


# creating database instance
db = QdrantVectorStore(
    client=client, 
    embedding=embeddings, 
    collection_name=VECTOR_STORE_NAME
)


print("------- everything is setup -------")
def main():

    while True:
        query = input("\n\n\t>> Query: ")

        if query == "exit":
            break 

        # retrieving docs from retriever
        docs = db.similarity_search_with_score(query=query, k=3)
        for i in docs:
            doc, score = i
            print(f"score: {score}", f"content: {doc.page_content}", sep="\n\n**********\n")
            print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")








if __name__ == "__main__":

    main()



    