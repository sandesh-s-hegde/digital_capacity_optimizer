import pandas as pd
from ai_brain import chat_with_data


def main():
    print("🚀 Booting Digital Capacity Optimizer...")

    mock_metrics = {
        'transport_mode': 'Road',
        'avg_demand': 120,
        'unit_cost': 50,
        'selling_price': 85
    }
    mock_df = pd.DataFrame()

    query = "I need to dispatch 5 refrigerated trucks to Germany (DE). Evaluate the route and check if the grid can support the load sustainably."

    print(f"\n[USER]: {query}")
    print("\n[AGENT IS THINKING AND CALLING TOOLS...]\n")

    response = chat_with_data(user_query=query, chat_history=[], df=mock_df, metrics=mock_metrics)

    print(f"[SYSTEM RESPONSE]:\n{response}")


if main == "__main__":
    main()
