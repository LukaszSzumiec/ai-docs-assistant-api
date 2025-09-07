from typing import Sequence


SYSTEM_PROMPT = (
    "You are a helpful assistant answering questions strictly based on the provided context. "
    "If the answer is not in the context, say you don't know. Reply concisely. Include citations."
)


def build_prompt(query: str, contexts: Sequence[str]) -> str:
    ctx = "\n\n---\n\n".join(contexts)
    user = f"Question: {query}\n\nContext:\n{ctx}\n\nAnswer with citations [doc:chunk_index]."
    return user
