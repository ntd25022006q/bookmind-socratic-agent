import operator
from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage

class ResearchState(TypedDict):
    topic: str               # Tên sách hoặc câu hỏi đọc sách
    user_profile: str        # Hồ sơ độc giả (ngành học, sở thích)
    research_data: str       # Dữ liệu sách bổ trợ
    analysis: str            # Nhận xét gợi ý sách
    risks: str               # Các câu hỏi phản biện Socrates
    report: str              # Báo cáo gợi ý và nhật ký đọc
    messages: Annotated[list[BaseMessage], operator.add]
    irrelevant: bool         # Từ chối nếu câu hỏi ngoài chủ đề sách
    csv_data: str
    retrieved_context: str
    citations: list[str]
    query_type: str          # 'consulting' hoặc 'qa'
    language: str
