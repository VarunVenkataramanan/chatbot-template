from typing import Annotated

from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState


@tool
def weather_tool(state: Annotated[dict, InjectedState]) -> str:
	"""Tool to get find what the weather is in Chennai"""
	variable = state.get("variable")
	return f"Weather is {variable} in Chennai."
