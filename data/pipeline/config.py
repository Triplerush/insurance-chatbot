"""
Central configuration module for the data pipeline.

Uses Pydantic BaseSettings for validation and .env loading.
Re-exports module-level constants for backward compatibility
(pipeline scripts use `config.OPENSEARCH_HOST`, etc.).
"""
from __future__ import annotations

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class PipelineSettings(BaseSettings):
    """Configuration for S3, OpenSearch, EDA, and Ingestion processes."""

    # --- General ---
    pdf_dir: str = Field(default="./data/raw_policies", validation_alias="PDF_DIR")

    # --- S3 Download ---
    s3_bucket: str = Field(default="anyoneai-datasets", validation_alias="S3_BUCKET")
    s3_prefix: str = Field(default="queplan_insurance/", validation_alias="S3_PREFIX")
    s3_aws_access_key_id: Optional[str] = Field(default=None, validation_alias="S3_AWS_ACCESS_KEY_ID")
    s3_aws_secret_access_key: Optional[str] = Field(default=None, validation_alias="S3_AWS_SECRET_ACCESS_KEY")

    # --- EDA ---
    chunk_size: Optional[str] = Field(default=None, validation_alias="CHUNK_SIZE")
    chunk_overlap: Optional[str] = Field(default=None, validation_alias="CHUNK_OVERLAP")

    # --- OpenSearch ---
    opensearch_host: str = Field(default="localhost", validation_alias="OPENSEARCH_HOST")
    opensearch_port: int = Field(default=9200, validation_alias="OPENSEARCH_PORT")
    opensearch_user: Optional[str] = Field(default="admin", validation_alias="OPENSEARCH_USER")
    opensearch_password: Optional[str] = Field(default="admin", validation_alias="OPENSEARCH_PASSWORD")
    opensearch_index: str = Field(default="policies", validation_alias="OPENSEARCH_INDEX")
    opensearch_embed_dim: int = Field(default=384, validation_alias="OPENSEARCH_EMBED_DIM")
    opensearch_shards: int = Field(default=1, validation_alias="OPENSEARCH_SHARDS")
    opensearch_replicas: int = Field(default=0, validation_alias="OPENSEARCH_REPLICAS")

    # --- Ingestion ---
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        validation_alias="EMBEDDING_MODEL",
    )
    embed_batch_size: int = Field(default=128, validation_alias="EMBED_BATCH_SIZE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


_settings = PipelineSettings()

# --- Re-export as module-level constants for backward compatibility ---

# General
PDF_DIR = _settings.pdf_dir

# S3 Download
S3_BUCKET = _settings.s3_bucket
S3_PREFIX = _settings.s3_prefix
S3_AWS_ACCESS_KEY_ID = _settings.s3_aws_access_key_id
S3_AWS_SECRET_ACCESS_KEY = _settings.s3_aws_secret_access_key

# EDA
EDA_OUT_DIR = "./eda_out"
EDA_RECS_FILE = os.path.join(EDA_OUT_DIR, "eda_recommendations.json")
CHUNK_SIZE_ENV = _settings.chunk_size
CHUNK_OVERLAP_ENV = _settings.chunk_overlap

# OpenSearch
OPENSEARCH_HOST = _settings.opensearch_host
OPENSEARCH_PORT = _settings.opensearch_port
OPENSEARCH_USER = _settings.opensearch_user
OPENSEARCH_PASSWORD = _settings.opensearch_password
OPENSEARCH_INDEX = _settings.opensearch_index
OPENSEARCH_EMBED_DIM = _settings.opensearch_embed_dim
OPENSEARCH_SHARDS = _settings.opensearch_shards
OPENSEARCH_REPLICAS = _settings.opensearch_replicas

# Ingestion
EMBEDDING_MODEL = _settings.embedding_model
EMBED_BATCH_SIZE = _settings.embed_batch_size
