from typing import Any, Optional

from loguru import logger

from app.rag.store import connect_to_chroma


def search_knowledge(
    query: str,
    metadata_filter: Optional[dict] = None,
    k: int = 3,
) -> list[dict[str, Any]]:
    try:
        chroma_db = connect_to_chroma()

        results = chroma_db.similarity_search_with_score(
            query, k=k, filter=metadata_filter
        )

        logger.info(f"Найдено {len(results)} результатов для запроса: {query[:100]}...")

        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "text": doc.page_content,
                "metadata": doc.metadata,
                "similarity_score": score,
            })

        for i, item in enumerate(formatted_results):
            preview = item["text"][:80].replace("\n", " ")
            logger.debug(
                f"  RAG [{i + 1}] score={item['similarity_score']:.4f}: {preview}..."
            )

        return formatted_results

    except Exception as e:
        logger.error(f"Ошибка при поиске: {e}")
        raise


def search_knowledge_texts(
    query: str,
    metadata_filter: Optional[dict] = None,
    k: int = 3,
) -> list[str]:
    results = search_knowledge(query, metadata_filter, k)
    return [r["text"] for r in results]