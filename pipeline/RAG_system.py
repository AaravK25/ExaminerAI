#Just some basic code will connect them together and form a complete RAG structure...

from llama_index.embeddings.google import GoogleEmbedding
from llama_index.core import Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex
from llama_index.core import Document


#Emdedings
Settings.embed_model = GoogleEmbedding(
    model_name="models/embedding-001"
)

#Qdrant Hybrid Index
vector_store = QdrantVectorStore(
    client=client,
    collection_name="rubrics",
    enable_hybrid=True  # KEY
)

index = VectorStoreIndex.from_vector_store(vector_store)

#ingest rubrics
docs = [
    Document(
        text="Ohm's law: V = IR...",
        metadata={"subject": "physics", "question_id": "q1"}
    )
]

index.insert_nodes(docs)

#Query Routing
def route(query, llm):
    prompt = f"""
    Classify subject: physics, chemistry, biology, math.

    Text: {query}
    Subject:
    """
    return llm.complete(prompt).text.lower()

#Hybrid retrieval
retriever = index.as_retriever(
    similarity_top_k=8,
    vector_store_query_mode="hybrid"
)

nodes = retriever.retrieve(query)

#CRAG
def crag_filter(query, nodes, llm):
    good = []

    for n in nodes:
        prompt = f"""
        Query: {query}
        Context: {n.text}

        Relevant for grading? yes/no
        """
        res = llm.complete(prompt).text.lower()

        if "yes" in res:
            good.append(n.text)

    return good

#complete rag retriever
class RAGRetriever:
    def __init__(self, index, llm):
        self.index = index
        self.llm = llm

    def retrieve(self, query):
        subject = route(query, self.llm)

        retriever = self.index.as_retriever(
            similarity_top_k=8,
            vector_store_query_mode="hybrid"
        )

        nodes = retriever.retrieve(query)

        # optional: filter by subject
        nodes = [n for n in nodes if n.metadata.get("subject") == subject]

        return crag_filter(query, nodes, self.llm)
