import operator
from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage

class ResearchState(TypedDict):
    topic: str
    user_profile: str
    research_data: str
    analysis: str
    risks: str
    report: str
    messages: Annotated[list[BaseMessage], operator.add]
    irrelevant: bool
    csv_data: str
    retrieved_context: str
    citations: list[str]
    query_type: str
    language: str
