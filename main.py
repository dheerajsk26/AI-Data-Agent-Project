from pathlib import Path

from agents.data_agent import data_agent
from langchain_core.messages import HumanMessage

QUERY_FILE = Path(__file__).parent / "query.txt"

if __name__ == "__main__":
    query = QUERY_FILE.read_text().strip()
    if not query:
        raise SystemExit(f"{QUERY_FILE} is empty. Add your request there and re-run.")

    response = data_agent.invoke(
        {"messages": [HumanMessage(content=query)],
         "route_response": ""}
    )

    route = response["route_response"]
    details = response["details"]

    print(f"Routed to: {route.upper()}")
    print()

    if route == "sql":
        print("Curated Question:")
        print(details["curated_ques"])
        print()

        print("SQL Query:")
        print(details["generated_sql_query"])
        print()

        print("Safety Check:", "SAFE" if details["is_safe"].lower() == "yes" else "UNSAFE")
        print("Reason:", details["comments"])
        print()

    elif route == "etl":
        print("Tool Activity:")
        for activity in details["tool_activity"]:
            print(f"- {activity['tool']}({activity['args']})")
            print(f"  Result: {activity['result']}")
        print()

    print("Answer:")
    print(details["final_answer"])
