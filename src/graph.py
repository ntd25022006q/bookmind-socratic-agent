from langgraph.graph import StateGraph, END
from src.state import ResearchState
from src.agents.guardrail_agent import guardrail_node
from src.agents.researcher_agent import researcher_node as profiler_node
from src.agents.analyst_agent import analyst_node as recommender_node
from src.agents.risk_assessor_agent import risk_assessor_node as questioner_node
from src.agents.reporter_agent import reporter_node

def route_after_guardrail(state: ResearchState) -> str:
    if state.get("irrelevant", False):
        return END
    return "profiler"

# StateGraph
graph = StateGraph(ResearchState)

graph.add_node("guardrail", guardrail_node)
graph.add_node("profiler", profiler_node)
graph.add_node("recommender", recommender_node)
graph.add_node("questioner", questioner_node)
graph.add_node("reporter", reporter_node)

graph.set_entry_point("guardrail")

graph.add_conditional_edges(
    "guardrail",
    route_after_guardrail,
    {
        "profiler": "profiler",
        END: END
    }
)

graph.add_edge("profiler", "recommender")
graph.add_edge("recommender", "questioner")
graph.add_edge("questioner", "reporter")
graph.add_edge("reporter", END)

app = graph.compile()
