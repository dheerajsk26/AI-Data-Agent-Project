from agents.data_agent import data_agent
from langchain_core.messages import HumanMessage

if __name__ == "__main__":
    response = data_agent.invoke(
        {"messages":[HumanMessage(content="I want to extract the data from the API endpoint 'https://pokeapi.co/api/v2/pokemon' and save it to data/extract folder in the csv folder")],
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
