from __future__ import annotations
from functools import lru_cache
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class AgentSettings(BaseSettings):
    """
    Configuración del agente (independiente del backend).
    Lee variables de entorno (.env o docker-compose).
    """

    # --- LLM (OpenAI-compatible endpoint: DO, Together, Groq, OpenAI, etc.) ---
    llm_api_key: Optional[str] = Field(
        default=None, validation_alias="LLM_API_KEY"
    )
    llm_base_url: str = Field(
        default="https://inference.do-ai.run/v1",
        validation_alias="LLM_BASE_URL",
    )
    llm_model: str = Field(
        default="openai-gpt-oss-120b", validation_alias="LLM_MODEL"
    )
    llm_temperature: Optional[float] = Field(
        default=None, validation_alias="LLM_TEMPERATURE"
    )
    llm_top_p: Optional[float] = Field(default=None, validation_alias="LLM_TOP_P")
    llm_max_output_tokens: Optional[int] = Field(
        default=None, validation_alias="LLM_MAX_OUTPUT_TOKENS"
    )

    # --- Tavily ---
    tavily_api_key: Optional[str] = Field(default=None, validation_alias="TAVILY_API_KEY")

    # --- OpenSearch (índice principal) ---
    opensearch_host: str = Field(default="http://opensearch", validation_alias="OPENSEARCH_HOST")
    opensearch_port: int = Field(default=9200, validation_alias="OPENSEARCH_PORT") 
    opensearch_index: str = Field(default="policies", validation_alias="OPENSEARCH_INDEX")
    opensearch_embed_dim: int = Field(default=384, validation_alias="OPENSEARCH_EMBED_DIM") 

    # --- Modelo de embeddings ---
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        validation_alias="EMBEDDING_MODEL",
    )

    # --- Retrieval ---
    retrieval_top_k: int = Field(default=40, validation_alias="RETRIEVAL_TOP_K")

    # --- OpenSearch (índice de resúmenes para el router semántico) ---
    policy_summaries_index: str = Field(
        default="policy_summaries_index",
        validation_alias="POLICY_SUMMARIES_INDEX",
    ) 

    # --- Seguridad/SSL opcional para OpenSearch ---
    opensearch_user: Optional[str] = Field(default=None, validation_alias="OPENSEARCH_USER") 
    opensearch_password: Optional[str] = Field(default=None, validation_alias="OPENSEARCH_PASSWORD") 
    opensearch_use_ssl: bool = Field(default=False, validation_alias="OPENSEARCH_USE_SSL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> AgentSettings:
    """Carga la configuración desde .env (cacheada)"""
    return AgentSettings()