import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.llm_pick import pick_llm
from utils.etl_tools import ETLTools
from Models.schema import RouterSchema, DataAgentSchema
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langchain.tools import tool
from langchain_anthropic import ChatAnthropic
from agents.etl_analyst import etl_analyst
from agents.sql_analyst import sql_analyst


llm = pick_llm("low")

llm_router = llm.with_structured_output(RouterSchema)


# ---------------------------- DATA AGENT GRAPH ---------------------------- #


def _extract_tool_activity(messages: list) -> list:
    """Pairs each tool call an AIMessage requested with the matching ToolMessage result."""

    calls = {}

    for msg in messages:
        for tool_call in getattr(msg, "tool_calls", None) or []:
            calls[tool_call["id"]] = {"tool": tool_call["name"], "args": tool_call["args"], "result": None}

    for msg in messages:
        if isinstance(msg, ToolMessage) and msg.tool_call_id in calls:
            calls[msg.tool_call_id]["result"] = msg.content

    return list(calls.values())


def router_node(state:DataAgentSchema):

    message = state.messages[-1].content

    route_response_dict = llm_router.invoke(message).model_dump()

    route_response = route_response_dict['answer']

    state.route_response = route_response

    return state

def etl_node(state:DataAgentSchema):

    message = state.messages[-1].content

    response = etl_analyst.invoke(
             {"messages":[HumanMessage(content=f"""
            {message}
    """)]}
        )

    state.details = {
        "tool_activity": _extract_tool_activity(response["messages"]),
        "final_answer": response["messages"][-1].content,
    }
    state.messages = state.messages + [response["messages"][-1]]

    return state

def sql_node(state:DataAgentSchema):

    message = state.messages[-1].content

    input_schema = {
        "messages": [],
        "user_question": f"{message}",
        "curated_ques": "",
        "prompt_query_context": "",
        "generated_sql_query": "",
        "is_safe": "No",
        "comments": "",
        "sql_query_execution_result": "",
        "final_answer": ""
    }

    response = sql_analyst.invoke(input_schema)

    state.details = {
        "curated_ques": response["curated_ques"],
        "generated_sql_query": response["generated_sql_query"],
        "is_safe": response["is_safe"],
        "comments": response["comments"],
        "final_answer": response["final_answer"],
    }
    state.messages = state.messages + [response["messages"][-1]]

    return state




data_agent_graph = StateGraph(DataAgentSchema)

data_agent_graph.add_node("router_node", router_node)
data_agent_graph.add_node("etl_node", etl_node)
data_agent_graph.add_node("sql_node", sql_node)

data_agent_graph.add_edge(START, "router_node")

def route_edge(state: DataAgentSchema) -> str:
    if state.route_response == "sql":
        return "sql_node"
    elif state.route_response == "etl":
        return "etl_node"
    else:
        raise ValueError(f"Invalid route response: {state.route_response}")


data_agent_graph.add_conditional_edges("router_node", route_edge,
                                      {
                                          "sql_node": "sql_node",
                                          "etl_node": "etl_node"
                                      })

data_agent = data_agent_graph.compile()

if __name__ == "__main__":

    # Optional
    from IPython.display import display, Image
    img = Image(data_agent.get_graph().draw_mermaid_png())
    with open("data_agent_graph.png", "wb") as f:
        f.write(img.data)

    response = data_agent.invoke(
        {"messages":[HumanMessage(content="I want to extract the data from the API endpoint 'https://pokeapi.co/api/v2/pokemon' and save it to data/extract folder in the csv folder")],
         "route_response": ""}
    )

    print(response)
