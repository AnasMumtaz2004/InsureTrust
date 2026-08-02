# RAG Infrastructure Pipeline

## Overview
The `rag/` directory houses the agent-agnostic Retrieval-Augmented Generation (RAG) infrastructure. It is consumed by the **Policy Interpretation Agent** (via `PolicyRetriever`) and the **Precedent Agent** (via `PrecedentRetriever`).

## Components
1. **Ingestion**:
   - `policy_doc_loader.py`: Splits master insurance policy documents into section/clause chunks.
   - `precedent_case_loader.py`: Formats historical claim outcomes, diagnosis codes, and procedure codes for semantic indexing.
   - `embedder.py`: Batched embedding generator supporting OpenAI Embeddings with deterministic fallback for offline/test execution.
2. **Vector Stores**:
   - `policy_store.py`: Vector index for policy wording and exclusions.
   - `precedent_store.py`: Vector index for historical adjudicated cases.
3. **Retrievers**:
   - `policy_retriever.py`: LangChain-compatible retriever used by `policy_interpretation_agent`.
   - `precedent_retriever.py`: LangChain-compatible retriever used by `precedent_agent`.
4. **Reranker**:
   - `reranker.py`: Post-retrieval cross-encoder/term-overlap scoring to ensure top-k relevancy before LLM prompting.

## Index Refresh Process
To reindex policies or precedents:
```python
from rag.vectorstore.policy_store import PolicyVectorStore
from rag.ingestion.policy_doc_loader import PolicyDocumentLoader

loader = PolicyDocumentLoader()
chunks = loader.load_and_chunk_policy(raw_text, policy_number="POL-2026", product_line="HEALTH")

store = PolicyVectorStore()
store.add_policy_clauses(chunks)
```
