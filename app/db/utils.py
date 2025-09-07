from typing import Iterable, Sequence
from sqlalchemy.engine import Connection
from sqlalchemy import text


def insert_embeddings(conn: Connection, rows: Iterable[tuple[str, Sequence[float]]]) -> None:
    # rows: (chunk_id, embedding_vector)
    conn.execute(
        text("DELETE FROM chunk_embeddings WHERE chunk_id = ANY(:ids)"),
        {"ids": [r[0] for r in rows]},
    )
    conn.execute(
        text("INSERT INTO chunk_embeddings (chunk_id, embedding) VALUES " +
             ", ".join([f"(:id{i}, :emb{i})" for i, _ in enumerate(rows)])),
        {**{f"id{i}": r[0] for i, r in enumerate(rows)},
         **{f"emb{i}": r[1] for i, r in enumerate(rows)}},
    )
