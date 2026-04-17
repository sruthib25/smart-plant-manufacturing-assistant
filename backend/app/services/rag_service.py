"""
================================================================================
RAG SERVICE - RETRIEVAL-AUGMENTED GENERATION WITH CHROMADB
================================================================================

This module implements Retrieval-Augmented Generation (RAG) for document-based Q&A.

WHAT IT DOES:
- Ingests markdown documents (SOPs, manuals, procedures).
- Splits documents intelligently by headers for better context.
- Stores document chunks as embeddings in ChromaDB vector database.
- Retrieves relevant documents based on semantic similarity to user queries.

WHY CHROMADB?
- **Embedded Database**: Runs in-process, no separate server needed.
- **Zero Configuration**: Just works out of the box.
- **Automatic Persistence**: Saves to disk automatically.
- **Open Source**: Free, no vendor lock-in.
- **Python Native**: Designed for Python AI/ML workflows.
- **LangChain Integration**: Works seamlessly with LangChain.

Alternatives:
- Pinecone: Cloud-based, requires API key, has costs.
- Weaviate: Requires Docker or cloud deployment.
- FAISS: Fast but no built-in persistence.

WHY HUGGINGFACE EMBEDDINGS (all-MiniLM-L6-v2)?
- **Local**: No API costs, runs entirely on your machine.
- **Fast**: Optimized for speed (384-dimensional vectors).
- **Small**: Only ~80MB model size.
- **Quality**: Good semantic understanding for document retrieval.

HOW RAG WORKS:
1. **Indexing (one-time)**:
   - Load markdown files from data directory.
   - Split by headers to preserve document structure.
   - Convert text chunks to embeddings (numerical vectors).
   - Store embeddings in ChromaDB.

2. **Retrieval (per query)**:
   - Convert user query to embedding.
   - Find k most similar document chunks (cosine similarity).
   - Return the matching text content.

3. **Generation (in Orchestrator)**:
   - Combine retrieved documents with the query.
   - Send to LLM to generate a grounded answer.

BIG PICTURE:
- This enables the assistant to answer questions about SOPs and procedures.
- Without RAG, the LLM would only know its training data (no plant-specific info).
- With RAG, the LLM can reference actual documentation.

ARCHITECTURE:
    [User Query: "How do I maintain the hydraulic pump?"]
                        |
                        v
    [RAG Service]  <-- YOU ARE HERE
         |
         | 1. Convert query to embedding
         v
    [ChromaDB] -- similarity search --> [Matching Document Chunks]
         |
         | 2. Return relevant SOPs/manuals
         v
    [Orchestrator] -- passes to LLM --> [Answer based on documents]
================================================================================
"""

import os
from typing import List
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter


class RAGService:
    """
    Retrieval-Augmented Generation service using ChromaDB and HuggingFace embeddings.
    
    This service manages the vector database for document retrieval.
    Documents are ingested once (on first run) and then queried on demand.
    
    Attributes:
        data_path: Path to directory containing markdown documents.
        persist_directory: Path where ChromaDB stores its data.
        embeddings: The embedding model used to convert text to vectors.
        vector_db: The ChromaDB vector store instance.
    """
    
    def __init__(self, data_path: str = "backend/app/data"):
        """
        Initialize the RAG service.
        
        On first run, ingests all markdown files and creates the vector database.
        On subsequent runs, loads the existing database from disk.
        
        Args:
            data_path: Directory containing .md files to index.
        """
        self.data_path = data_path
        self.persist_directory = "backend/app/data/chroma_db"
        
        # =====================================================================
        # EMBEDDING MODEL SELECTION
        # =====================================================================
        # We use HuggingFace's all-MiniLM-L6-v2 for embeddings because:
        # - It's lightweight and fast (good for local development)
        # - No external API calls needed
        # - Good quality for semantic search tasks
        #
        # Alternative: OllamaEmbeddings(model="nomic-embed-text") if you
        # prefer to use Ollama for everything, but requires pulling the model.
        # =====================================================================
        from langchain_huggingface import HuggingFaceEmbeddings
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # =====================================================================
        # CHROMADB INITIALIZATION
        # =====================================================================
        # ChromaDB automatically persists to disk at the specified directory.
        # If the directory exists, it loads the existing database.
        # If not, we create a new one and ingest documents.
        # =====================================================================
        if os.path.exists(self.persist_directory):
            # Load existing vector database
            self.vector_db = Chroma(
                persist_directory=self.persist_directory, 
                embedding_function=self.embeddings
            )
        else:
            # Create new database and ingest documents
            self.vector_db = Chroma(
                persist_directory=self.persist_directory, 
                embedding_function=self.embeddings
            )
            self.ingest_data()

    def ingest_data(self):
        """
        Ingest all markdown files from the data directory into ChromaDB.
        
        WHAT: Reads .md files, splits them by headers, and stores as embeddings.
        HOW: 
            1. Walks through data directory finding .md files.
            2. Uses MarkdownHeaderTextSplitter to split by H1/H2/H3.
            3. Converts each chunk to an embedding.
            4. Stores in ChromaDB with source metadata.
        BIG PICTURE: This is run once on first startup to build the knowledge base.
        
        Why Split by Headers?
        - Preserves document structure and context.
        - Each chunk is a coherent section (not arbitrary 500 characters).
        - Metadata includes which headers the chunk belongs to.
        """
        docs = []
        
        # Walk through all files in data directory
        for root, dirs, files in os.walk(self.data_path):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    
                    # Read document content
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # =========================================================
                    # MARKDOWN HEADER SPLITTING
                    # =========================================================
                    # This splitter divides documents at header boundaries.
                    # Result: chunks that correspond to sections, not arbitrary
                    # character counts. Each chunk keeps header info as metadata.
                    # =========================================================
                    headers_to_split_on = [
                        ("#", "Header 1"),     # H1 headers
                        ("##", "Header 2"),    # H2 headers
                        ("###", "Header 3"),   # H3 headers
                    ]
                    markdown_splitter = MarkdownHeaderTextSplitter(
                        headers_to_split_on=headers_to_split_on
                    )
                    md_header_splits = markdown_splitter.split_text(content)
                    
                    # Add source file name to metadata for traceability
                    for split in md_header_splits:
                        split.metadata["source"] = file
                        docs.append(split)
        
        # =====================================================================
        # ADD DOCUMENTS TO CHROMADB
        # =====================================================================
        # ChromaDB automatically:
        # 1. Converts each document to an embedding using our embedding model.
        # 2. Stores the embedding + original text + metadata.
        # 3. Persists to disk (in Chroma 0.4+, this is automatic).
        # =====================================================================
        if docs:
            self.vector_db.add_documents(docs)
            # Note: self.vector_db.persist() not needed in Chroma 0.4+

    def query(self, question: str, k: int = 3):
        """
        Retrieve the most relevant documents for a given question.
        
        WHAT: Finds k documents most similar to the question.
        HOW: 
            1. Converts question to embedding.
            2. Performs cosine similarity search in ChromaDB.
            3. Returns top k matching document chunks.
        BIG PICTURE: This is called by the RAG agent in the Orchestrator
                     to get relevant context before generating an answer.
        
        Args:
            question: The user's query.
            k: Number of documents to retrieve (default: 3).
            
        Returns:
            List[Document]: List of LangChain Document objects with:
                - page_content: The text of the document chunk.
                - metadata: Source file, headers, etc.
                
        Example:
            >>> docs = rag_service.query("hydraulic pump maintenance")
            >>> print(docs[0].page_content)
            "To maintain the hydraulic pump, first ensure..."
        """
        return self.vector_db.similarity_search(question, k=k)


# Global singleton instance
# Created once when module is imported, ingests data if needed
rag_service = RAGService()

