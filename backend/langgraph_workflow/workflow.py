from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from .nodes import generate_query_or_respond, generate_answer, tools

workflow = StateGraph(MessagesState)
workflow.add_node("generate_query_or_respond", generate_query_or_respond)
workflow.add_node("retrieve", ToolNode(tools))
workflow.add_node("generate_answer", generate_answer)

workflow.add_edge(START, "generate_query_or_respond")
workflow.add_conditional_edges(
    "generate_query_or_respond",
    tools_condition,
    {
        "tools": "retrieve",
        END: END,
    }
)
workflow.add_edge("retrieve", "generate_answer")
workflow.add_edge("generate_answer", END)

# 메모리 옵션 (선택 사항)
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()

graph = workflow.compile(checkpointer=memory)