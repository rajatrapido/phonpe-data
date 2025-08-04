import streamlit as st
import pandas as pd
import json
import os

# Define the base path to the data directory relative to the project root
DATA_PATH = "data/map/transaction/hover/country/india/state"

# Function to load data from a JSON file
def load_data(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data['data']['hoverDataList']

# Function to get data for all of India
def get_all_india_data(year, quarter):
    all_india_data = []
    states_path = DATA_PATH
    # Check if the data path exists
    if not os.path.exists(states_path):
        st.error(f"Data directory not found. Make sure you have cloned the 'pulse' repository into the project root. Expected path: {os.path.abspath(states_path)}")
        return None
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

    states_path = DATA_PATH
    # Check if the data path exists
    if not os.path.exists(states_path):
        st.error(f"Data directory not found. Make sure you have cloned the 'pulse' repository into the project root as instructed in the README.md.")
        return

    # Get the list of states and add "All India"
    states = ["All India"] + [s for s in os.listdir(states_path) if os.path.isdir(os.path.join(states_path, s))]
    selected_state = st.sidebar.selectbox("State", states)

    # Get the list of years
    if selected_state == "All India":
        # Use a sample state to get the list of available years, as they are consistent across states
        years_path = os.path.join(states_path, "andhra-pradesh")
    else:
        years_path = os.path.join(states_path, selected_state)

    if not os.path.exists(years_path):
        st.error(f"Could not find data for state: {selected_state}")
        return

    years = [y for y in os.listdir(years_path) if os.path.isdir(os.path.join(years_path, y))]
    selected_year = st.sidebar.selectbox("Year", years)

    # Get the list of quarters
    quarters_path = os.path.join(years_path, selected_year)
    quarters = [q.replace('.json', '') for q in os.listdir(quarters_path) if q.endswith('.json')]
    selected_quarter = st.sidebar.selectbox("Quarter", quarters)

    # Load the data
    data = []
    if selected_state == "All India":
        data = get_all_india_data(selected_year, selected_quarter)
        if data is None:
            return # Stop execution if data couldn't be loaded
    else:
        file_path = os.path.join(states_path, selected_state, selected_year, f"{selected_quarter}.json")
        if os.path.exists(file_path):
            data = load_data(file_path)
            for item in data:
                item['state'] = selected_state
        else:
            st.error("Data not found for the selected period.")
            return

    if not data:
        st.warning("No data to display for the selected period.")
        return

    # Prepare data for the table
    table_data = []
    for item in data:
        table_data.append({
            "City/District": item['name'],
            "State": item.get('state', selected_state if selected_state != "All India" else "N/A"),
            "Transaction Count": item['metric'][0]['count'],
            "Transaction Amount": item['metric'][0]['amount']
        })

    df = pd.DataFrame(table_data)

    if df.empty:
        st.warning("No data to display for the selected period.")
        return

    # Sort by transaction count
    df = df.sort_values(by='Transaction Count', ascending=False)

    # Add average transaction amount column
    df['Average Transaction Amount'] = df.apply(lambda row: row['Transaction Amount'] / row['Transaction Count'] if row['Transaction Count'] > 0 else 0, axis=1)

    # Calculate total row
    total_count = df['Transaction Count'].sum()
    total_amount = df['Transaction Amount'].sum()
    average_total = total_amount / total_count if total_count > 0 else 0
    total_row = pd.DataFrame([{
        'City/District': 'Total',
        'State': '-',
        'Transaction Count': total_count,
        'Transaction Amount': total_amount,
        'Average Transaction Amount': average_total
    }])

    # Add total row to the dataframe
    df = pd.concat([df, total_row], ignore_index=True)

    # Format columns
    df['Transaction Count'] = df['Transaction Count'].map('{:,.0f}'.format)
    df['Transaction Amount'] = df['Transaction Amount'].map('{:,.0f}'.format)
    df['Average Transaction Amount'] = df['Average Transaction Amount'].map('{:,.0f}'.format)

    st.dataframe(df)

if __name__ == "__main__":
    main()