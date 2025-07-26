from typing import Annotated

from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
	llm: ChatOpenAI
	messages: Annotated[list, add_messages]
	variable: str | None = "hot"
