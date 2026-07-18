from langgraph.graph import StateGraph, START, END
from .state import AgentState
from . import nodes

def _after_route(state: AgentState) -> str:
    return state["route"]                       # "rag" | "web" | "direct"

def _after_grade(state: AgentState) -> str:
    if state["relevant"]:
        return "generate"
    if state["attempts"] >= nodes.MAX_ATTEMPTS:
        return "generate"    # jo hai usi se; prompt "not enough info" bol dega
    return "rewrite"

def build_graph():
    g = StateGraph(AgentState)

    g.add_node("route",         nodes.route)
    g.add_node("retrieve",      nodes.retrieve)
    g.add_node("grade",         nodes.grade)
    g.add_node("rewrite",       nodes.rewrite)
    g.add_node("web_search",    nodes.web_search)
    g.add_node("generate",      nodes.generate)
    g.add_node("direct_answer", nodes.direct_answer)

    g.add_edge(START, "route")
    g.add_conditional_edges("route", _after_route, {
        "rag":    "retrieve",
        "web":    "web_search",
        "direct": "direct_answer",
    })
    g.add_edge("retrieve", "grade")
    g.add_conditional_edges("grade", _after_grade, {
        "generate": "generate",
        "rewrite":  "rewrite",
    })
    g.add_edge("rewrite", "retrieve")        # <-- YAHI loop hai (cycle)
    g.add_edge("web_search", "generate")
    g.add_edge("generate", END)
    g.add_edge("direct_answer", END)

    return g.compile()

agent = build_graph()