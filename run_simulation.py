import warnings
warnings.filterwarnings("ignore")

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

    query = input("\n[ENTER DISPATCH REQUEST]: ")

    print(f"\n[USER]: {query}")
    print("\n[AGENT IS THINKING AND CALLING TOOLS...]\n")

    response = chat_with_data(user_query=query, chat_history=[], df=mock_df, metrics=mock_metrics)

    print(f"[SYSTEM RESPONSE]:\n{response}")


if __name__ == "__main__":
    main()
