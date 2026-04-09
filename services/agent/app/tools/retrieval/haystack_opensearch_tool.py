import asyncio
import logging
from typing import List, Optional, Type

from pydantic import BaseModel, Field, ConfigDict

from ... import get_settings

from langchain_core.documents import Document
from langchain_core.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

# Try to import OpenSearch backend depending on available package
try:
    from opensearch_haystack.document_store import OpenSearchDocumentStore
    from opensearch_haystack.retriever import OpenSearchHybridRetriever
    _OS_BACKEND = "opensearch_haystack"

    # Maintain original exception handling for robust OpenSearch error management
    from opensearchpy import (
        ConnectionError as OSConnectionError,
        TransportError,
        RequestError,
    )
except ModuleNotFoundError:
    from haystack_integrations.document_stores.opensearch import OpenSearchDocumentStore
    from haystack_integrations.components.retrievers.opensearch import (
        OpenSearchHybridRetriever,
    )
    _OS_BACKEND = "haystack_integrations"

    # Define placeholder exceptions if opensearchpy is not available
    class OSConnectionError(Exception):
        pass

    class TransportError(Exception):
        pass

    class RequestError(Exception):
        pass


from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.dataclasses import Document as HaystackDocument

logger = logging.getLogger(__name__)

settings = get_settings()

# --- Configuration variables ---
OPENSEARCH_HOST = settings.opensearch_host
OPENSEARCH_PORT = settings.opensearch_port
OPENSEARCH_INDEX = settings.opensearch_index
EMBED_DIM = settings.opensearch_embed_dim
EMBED_MODEL = settings.embedding_model
RETRIEVAL_K_NET = settings.retrieval_top_k

# --- Initialize OpenSearch document store ---
# Build http_auth: pass credentials only when both are set AND security is enabled.
# Haystack defaults to reading OPENSEARCH_USERNAME/OPENSEARCH_PASSWORD env vars,
# which conflicts with DISABLE_SECURITY_PLUGIN=true, so we override with None.
if settings.opensearch_user and settings.opensearch_password and settings.opensearch_use_ssl:
    _http_auth = (settings.opensearch_user, settings.opensearch_password)
else:
    _http_auth = None

doc_store = OpenSearchDocumentStore(
    hosts=[OPENSEARCH_HOST],
    port=OPENSEARCH_PORT,
    index=OPENSEARCH_INDEX,
    embedding_dim=EMBED_DIM,
    create_index=False,
    content_field="text",
    embedding_field="embedding",
    metadata_field="metadata",
    knn_space_type="cosinesimil",
    knn_engine="nmslib",
    http_auth=_http_auth,
    use_ssl=settings.opensearch_use_ssl,
    verify_certs=settings.opensearch_use_ssl,
)

# --- Embedder and retriever initialization ---
query_embedder = SentenceTransformersTextEmbedder(
    model=EMBED_MODEL,
    normalize_embeddings=True,
)

haystack_retriever_instance = OpenSearchHybridRetriever(
    document_store=doc_store,
    embedder=query_embedder,
    top_k_bm25=RETRIEVAL_K_NET,
    top_k_embedding=RETRIEVAL_K_NET,
    join_mode="reciprocal_rank_fusion",
)

def _convert_docs(haystack_docs: List[HaystackDocument]) -> List[Document]:
    """
    Convert Haystack Document objects into LangChain Document objects.
    Args:
        haystack_docs: List of Haystack documents retrieved from OpenSearch.
    Returns:
        List of LangChain Document instances with standardized metadata.
    """
    out: List[Document] = []
    for h_doc in haystack_docs:
        raw_meta = dict(h_doc.meta or {})
        inner = raw_meta.pop("metadata", {}) if "metadata" in raw_meta else {}
        meta = {**inner, **raw_meta}

        meta["score"] = getattr(h_doc, "score", None)
        meta["opensearch_backend"] = _OS_BACKEND

        page_content = (
            h_doc.content
            or meta.get("text")
            or meta.get("content")
            or ""
        )

        meta.pop("text", None)
        meta.pop("content", None)

        out.append(Document(page_content=page_content, metadata=meta))

    logger.debug("OpenSearch returned %d documents", len(out))
    return out


class RetrieverInput(BaseModel):
    """Schema for the HybridOpenSearchTool input arguments."""
    query: str = Field(
        description="User query to search insurance policy documents in OpenSearch."
    )
    k: Optional[int] = Field(
        None,
        description="Number of documents to retrieve (overrides default).",
    )


class HybridOpenSearchTool(BaseTool):
    """
    Hybrid retriever tool combining BM25 and dense embeddings (RRF fusion).
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = "hybrid_opensearch_search"
    description: str = (
        "Searches the OpenSearch index (BM25 + embeddings + RRF) and returns "
        "a list of Chilean insurance policy documents with metadata (file, page, score). "
        "In case of error, returns a document containing the error in metadata['error']."
    )
    args_schema: Type[BaseModel] = RetrieverInput
    haystack_retriever: OpenSearchHybridRetriever

    def _return_error_doc(self, msg: str, error_type: str, exc: Exception | None = None) -> List[Document]:
        """Return a standardized document containing error information."""
        return [
            Document(
                page_content="Unable to query OpenSearch.",
                metadata={
                    "error": msg,
                    "error_type": error_type,
                    "opensearch_backend": _OS_BACKEND,
                    "exception": str(exc) if exc else None,
                },
            )
        ]

    def _run(
        self,
        query: str,
        k: Optional[int] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> List[Document]:
        """
        Synchronous retrieval pipeline.
        Retrieves documents using OpenSearchHybridRetriever (BM25 + embeddings + RRF).
        """
        effective_k = k or RETRIEVAL_K_NET

        try:
            results = self.haystack_retriever.run(
                query=query,
                top_k_bm25=effective_k,
                top_k_embedding=effective_k,
            )
            docs = _convert_docs(results.get("documents", []))
            return docs[:effective_k]

        except OSConnectionError as e:
            logger.error("Unable to connect to OpenSearch at %s: %s", OPENSEARCH_HOST, e, exc_info=True)
            return self._return_error_doc(
                "Error: Unable to connect to the OpenSearch database.",
                "connection_error",
                e,
            )
        except RequestError as e:
            logger.warning("Invalid OpenSearch query: %s, error=%s", query, e, exc_info=True)
            return self._return_error_doc(
                f"Error: Invalid Query OpenSearch ({e.error}).",
                "request_error",
                e,
            )
        except TransportError as e:
            logger.error("OpenSearch transport error (status %s): %s", getattr(e, "status_code", "?"), e, exc_info=True)
            return self._return_error_doc(
                f"Error: Transport error with OpenSearch (status {getattr(e, 'status_code', 'unknown')}).",
                "transport_error",
                e,
            )
        except Exception as e:
            logger.exception("HybridOpenSearchTool._run failed unexpectedly")
            return self._return_error_doc(
                f"Error: Internal search unavailable ({type(e).__name__}).",
                "unexpected_error",
                e,
            )

    async def _arun(
        self,
        query: str,
        k: Optional[int] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> List[Document]:
        """Async wrapper — delegates to the synchronous _run via a thread."""
        return await asyncio.to_thread(self._run, query, k, run_manager)


# --- Instantiate the retrieval tool ---
retrieval_tool = HybridOpenSearchTool(
    haystack_retriever=haystack_retriever_instance,
)