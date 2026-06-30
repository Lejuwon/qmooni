from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
from langchain_core.messages import AIMessage
from typing import TypedDict
from dotenv import load_dotenv
import os
from .tools import retrieve_context_from_vectorstore  # @tool 안 써도 됨

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ LLM 및 도구 설정
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=OPENAI_API_KEY)

# ✅ 필수 인자 넣어서 도구 정의
tools = [
    Tool.from_function(
        func=retrieve_context_from_vectorstore,
        name="retrieve_context_from_vectorstore",
        description="벡터스토어에서 관련 문맥을 검색합니다."
    )
]

# ✅ Agent 초기화
agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type="zero-shot-react-description",
    verbose=True
)

# ✅ 상태 정의
class MessagesState(TypedDict):
    messages: list

# ✅ 노드 함수
def generate_query_or_respond(state: MessagesState) -> MessagesState:
    last_message = state["messages"][-1].content  # ✅ 수정
    response = agent_executor.run(last_message)
    return {"messages": [AIMessage(content=response)]}  # 객체로 감싸는 것이 LangGraph에 더 안전

def generate_answer(state: MessagesState) -> MessagesState:
    last_tool_output = state["messages"][-1].content  # ✅ 수정
    followup = llm.invoke(
        f"""
        다음 정보를 바탕으로 사용자의 질문에 정리된 답변을 제공하세요:
        {last_tool_output}

        답변:
        """
    )
    return {"messages": [AIMessage(content=followup.content)]}  # ✅ AIMessage로 감싸기