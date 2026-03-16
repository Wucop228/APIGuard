import json
import os
from pathlib import Path
from typing import Optional

import torch
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger

from app.core.config import settings

KNOWLEDGE_PATH = Path(__file__).parent / "knowledge.json"

_embeddings: Optional[HuggingFaceEmbeddings] = None
_chroma_db: Optional[Chroma] = None


def get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings

    if _embeddings is not None:
        return _embeddings

    logger.info(f"Загрузка модели эмбеддингов: {settings.EMBEDDING_MODEL}")

    device = "cuda" if torch.cuda.is_available() else "cpu"

    _embeddings = HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL,
        model_kwargs={"device": device},
        encode_kwargs={"normalize_embeddings": True},
    )

    logger.success(f"Модель эмбеддингов загружена (device={device})")
    return _embeddings


def connect_to_chroma() -> Chroma:
    global _chroma_db

    if _chroma_db is not None:
        return _chroma_db

    try:
        embeddings = get_embeddings()

        _chroma_db = Chroma(
            persist_directory=settings.CHROMA_PATH,
            embedding_function=embeddings,
            collection_name=settings.CHROMA_COLLECTION_NAME,
            collection_metadata={"hnsw:space": "cosine"},
        )

        count = _chroma_db._collection.count()
        logger.success(f"Успешное подключение к базе Chroma, документов: {count}")
        return _chroma_db

    except Exception as e:
        logger.error(f"Ошибка подключения к Chroma: {e}")
        raise


def split_text_into_chunks(text: str, metadata: dict) -> list:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len,
        is_separator_regex=False,
    )

    chunks = text_splitter.create_documents(
        texts=[text],
        metadatas=[metadata],
    )
    return chunks


def generate_chroma_db() -> Optional[Chroma]:
    global _chroma_db

    try:
        os.makedirs(settings.CHROMA_PATH, exist_ok=True)

        if not KNOWLEDGE_PATH.exists():
            logger.warning(f"Файл {KNOWLEDGE_PATH} не найден, пропускаю seed")
            return None

        with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
            documents = json.load(f)

        if not documents:
            logger.warning("knowledge.json пустой, нет документов для добавления")
            return None

        embeddings = get_embeddings()

        existing_db = Chroma(
            persist_directory=settings.CHROMA_PATH,
            embedding_function=embeddings,
            collection_name=settings.CHROMA_COLLECTION_NAME,
        )

        if existing_db._collection.count() > 0:
            logger.info(
                f"ChromaDB уже содержит {existing_db._collection.count()} документов, "
                f"пропускаю seed"
            )
            _chroma_db = existing_db
            return existing_db

        logger.info(f"Создание Chroma DB из {len(documents)} документов...")

        all_chunks = []
        for i, doc in enumerate(documents):
            chunks = split_text_into_chunks(doc["text"], doc.get("metadata", {}))
            all_chunks.extend(chunks)
            logger.info(
                f"Документ {i + 1}/{len(documents)} (id={doc['id']}) "
                f"разбит на {len(chunks)} чанков"
            )

        texts = [chunk.page_content for chunk in all_chunks]
        metadatas = [chunk.metadata for chunk in all_chunks]
        ids = [f"doc_{i}" for i in range(len(all_chunks))]

        chroma_db = Chroma.from_texts(
            texts=texts,
            embedding=embeddings,
            ids=ids,
            metadatas=metadatas,
            persist_directory=settings.CHROMA_PATH,
            collection_name=settings.CHROMA_COLLECTION_NAME,
            collection_metadata={"hnsw:space": "cosine"},
        )

        _chroma_db = chroma_db

        logger.success(
            f"База Chroma инициализирована, добавлено {len(all_chunks)} чанков "
            f"из {len(documents)} документов"
        )
        return chroma_db

    except Exception as e:
        logger.error(f"Ошибка инициализации Chroma: {e}")
        raise