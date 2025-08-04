
import streamlit as st
import pandas as pd
import json
import os

# Function to load data from a JSON file
def load_data(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data['data']['hoverDataList']

# Function to get data for all of India
def get_all_india_data(year, quarter):
    all_india_data = []
    states_path = "/Users/E2005/work/projects/phonepeData/pulse/data/map/transaction/hover/country/india/state"
    states = [s for s in os.listdir(states_path) if os.path.isdir(os.path.join(states_path, s))]
    for state in states:
        file_path = os.path.join(states_path, state, year, f"{quarter}.json")
        if os.path.exists(file_path):
            state_data = load_data(file_path)
            for item in state_data:
                item['state'] = state
                all_india_data.append(item)
    return all_india_data

# Main app
def main():
    st.title("PhonePe Pulse Transaction Data")

    # Sidebar for user selection
    st.sidebar.header("Select Time Period")

    # Get the list of states and add "All India"
    states_path = "/Users/E2005/work/projects/phonepeData/pulse/data/map/transaction/hover/country/india/state"
    states = ["All India"] + [s for s in os.listdir(states_path) if os.path.isdir(os.path.join(states_path, s))]
    selected_state = st.sidebar.selectbox("State", states)

    # Get the list of years
    if selected_state == "All India":
        years_path = os.path.join(states_path, "andhra-pradesh") # Use any state to get the years
    else:
        years_path = os.path.join(states_path, selected_state)
    years = [y for y in os.listdir(years_path) if os.path.isdir(os.path.join(years_path, y))]
    selected_year = st.sidebar.selectbox("Year", years)

    # Get the list of quarters
    quarters_path = os.path.join(years_path, selected_year)
    quarters = [q.replace('.json', '') for q in os.listdir(quarters_path) if q.endswith('.json')]
    selected_quarter = st.sidebar.selectbox("Quarter", quarters)

    # Load the data
    if selected_state == "All India":
        data = get_all_india_data(selected_year, selected_quarter)
    else:
        file_path = os.path.join(states_path, selected_state, selected_year, f"{selected_quarter}.json")
        if os.path.exists(file_path):
            data = load__data(file_path)
            for item in data:
                item['state'] = selected_state
        else:
            st.error("Data not found for the selected period.")
            return

    # Prepare data for the table
    table_data = []
    for item in data:
        table_data.append({
            "City/District": item['name'],
            "State": item['state'],
            "Transaction Count": item['metric'][0]['count'],
            "Transaction Amount": item['metric'][0]['amount']
        })

    df = pd.DataFrame(table_data)

    # Sort by transaction count
    df = df.sort_values(by='Transaction Count', ascending=False)

    # Add average transaction amount column
    df['Average Transaction Amount'] = df['Transaction Amount'] / df['Transaction Count']

    # Calculate total row
    total_count = df['Transaction Count'].sum()
    total_amount = df['Transaction Amount'].sum()
    average_total = total_amount / total_count if total_count > 0 else 0
    total_row = pd.DataFrame([{'City/District': 'Total', 'State': '-', 'Transaction Count': total_count, 'Transaction Amount': total_amount, 'Average Transaction Amount': average_total}])

    # Add total row to the dataframe
    df = pd.concat([df, total_row], ignore_index=True)

    # Format columns
    df['Transaction Count'] = df['Transaction Count'].map('{:,.0f}'.format)
    df['Transaction Amount'] = df['Transaction Amount'].map('{:,.0f}'.format)
    df['Average Transaction Amount'] = df['Average Transaction Amount'].map('{:,.0f}'.format)

    st.dataframe(df)

if __name__ == "__main__":
    main()
