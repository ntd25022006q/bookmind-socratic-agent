from langgraph.graph import StateGraph, END
from src.state import ResearchState
from src.agents.guardrail_agent import guardrail_node
from src.agents.profiler_agent import profiler_node
from src.agents.recommender_agent import recommender_node
from src.agents.questioner_agent import questioner_node
from src.agents.critic_agent import critic_node
from src.agents.reporter_agent import reporter_node

def route_after_guardrail(state: ResearchState) -> str:
    if state.get("irrelevant", False):
        return END
    return "profiler"

graph = StateGraph(ResearchState)

graph.add_node("guardrail", guardrail_node)
graph.add_node("profiler", profiler_node)
graph.add_node("recommender", recommender_node)
graph.add_node("questioner", questioner_node)
graph.add_node("critic", critic_node)
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

def route_after_questioner(state: ResearchState) -> str:
    if state.get("socratic_answers"):
        return "critic"
    return END

graph.add_edge("profiler", "recommender")
graph.add_edge("recommender", "questioner")

graph.add_conditional_edges(
    "questioner",
    route_after_questioner,
    {
        "critic": "critic",
        END: END
    }
)

graph.add_edge("critic", "reporter")
graph.add_edge("reporter", END)

app = graph.compile()
