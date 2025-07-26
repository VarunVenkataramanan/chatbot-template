import logging
import sqlite3
from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command

from app.utilities.instances import get_db_manager

from .prompt import get_system_prompt
from .state import AgentState
from .tools import weather_tool


class Agent:
	def __init__(self):
		self.tools = [
			weather_tool,
		]
		self.graph = None
		self.memory = None
		self.graph_path = Path("output/agent_graph.png")

	def _create_sqlite_connection(self) -> sqlite3.Connection:
		try:
			conn = sqlite3.connect(
				"app/databases/agent_memory.db",
				check_same_thread=False,
				timeout=30.0,
			)
			conn.execute("PRAGMA foreign_keys = ON")
			conn.execute("PRAGMA journal_mode = WAL")
			return conn
		except sqlite3.Error as e:
			logging.error(f"Failed to initialize SQLite connection: {e!s}", exc_info=True)
			raise

	def create_agent(self, llm):
		tools = self.tools
		graph_builder = StateGraph(AgentState)

		def chatbot(state: AgentState):
			# Sample for get_db_manager() and Command usage
			# verified = get_db_manager().verify_customer(variable)
			# if not verified:
			# 	return Command(goto="verify_customer")
			llm_with_tools = llm.bind_tools(tools)
			return {"messages": [llm_with_tools.invoke(state["messages"])]}

		tool_node = ToolNode(tools=tools)
		graph_builder.add_node("chatbot", chatbot)
		graph_builder.add_node("tools", tool_node)
		graph_builder.add_edge(START, "chatbot")
		graph_builder.add_conditional_edges(
			"chatbot",
			tools_condition,
		)
		graph_builder.add_edge("tools", "chatbot")
		conn = self._create_sqlite_connection()
		memory = SqliteSaver(conn)
		self.memory = memory
		logging.info("Successfully initialized SQLite connection")
		graph = graph_builder.compile(checkpointer=memory)
		self.graph = graph
		with self.graph_path.open("wb") as f:
			f.write(graph.get_graph().draw_mermaid_png())
		logging.info(f"Graph visualization saved to {self.graph_path}")
		return graph

	def process_message(self, user_input: str, session_id: str | None = None) -> str:
		try:
			logging.info("=== Starting message processing ===")
			logging.info(f"Session ID: {session_id}")
			logging.info(f"Input message: {user_input}")
			llm = ChatOpenAI(
				model="gpt-4.1",
				temperature=0.2,
				max_retries=3,
			)
			agent = self.create_agent(llm)
			config = {
				"configurable": {
					"thread_id": session_id,
				},
			}
			logging.info(f"Using thread ID: {config['configurable']['thread_id']}")
			logging.info("Invoking agent with message")
			events = agent.stream(
				{
					"messages": [
						HumanMessage(content=user_input if user_input else "ignore this message. Dont reply to this message"),
						SystemMessage(content=get_system_prompt()),
					],
					"llm": llm,
				},
				config,
				stream_mode="values",
			)
			for event in events:
				last_message = event["messages"][-1]
			logging.info("Agent response received successfully")
			logging.info(f"Response content: {last_message.content[:100]}...")
			return last_message.content
		except Exception as e:
			logging.error(f"Unexpected error in process_message: {e!s}", exc_info=True)
			raise

	def clear_memory(self, session_id: str):
		try:
			thread_id = session_id
			logging.info("=== Starting memory clear operation ===")
			logging.info(f"Clearing memory for thread: {thread_id}")
			conn = self._create_sqlite_connection()
			cursor = conn.cursor()
			cursor.execute("DELETE FROM checkpoints WHERE thread_id = ?", (thread_id,))
			conn.commit()
			logging.info(f"Cleared memory for thread {thread_id} from database")
			conn.close()
			logging.info("=== Memory clear operation completed successfully ===")
		except sqlite3.Error as e:
			logging.error(
				f"Failed to clear thread memory from database: {e!s}",
				exc_info=True,
			)
			raise
