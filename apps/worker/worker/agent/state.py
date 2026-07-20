from typing import TypedDict, Literal

class AgentState(TypedDict, total=False):
    question:  str                              # original sawaal
    query:     str                              # current search query (rewrite ho sakti hai)
    route:     Literal["rag", "web", "direct"]
    contexts:  list[dict]                       # retrieved chunks (payload dicts)
    relevant:  bool                             # grade ka verdict
    attempts:  int                              # kitni baar retrieve kiya
    answer:    str
    document_id: str | None
    top_k:     int
    sub_questions: list[str]      # planner ka output
    sub_results:   list[dict]     # har sub-question ka {question, contexts}
