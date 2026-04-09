from typing import List, Optional, Type
import pytest
from unittest.mock import Mock, patch
from langchain_core.documents import Document

from ...tools.retrieval.haystack_opensearch_tool import HybridOpenSearchTool


@pytest.fixture
def mock_retriever():
    retriever = Mock()
    docs = [
        Document(page_content="Doc 1 sobre seguros", metadata={"score": 0.9}),
        Document(page_content="Doc 2 sobre pólizas", metadata={"score": 0.8}),
        Document(page_content="Doc 3 sobre coberturas", metadata={"score": 0.7}),
    ]
    retriever.invoke.return_value = docs
    retriever.ainvoke.return_value = docs
    return retriever


def test_hybrid_tool_initialization(mock_retriever):
    tool = HybridOpenSearchTool(
        haystack_retriever=mock_retriever,
    )
    assert tool.name == "hybrid_opensearch_search"
    assert tool.haystack_retriever == mock_retriever
