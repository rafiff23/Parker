import streamlit as st
import pandas as pd

def categorize_week(date):
    day = date.day
    if day <= 7:
        return "Week 1"
    elif day <= 14:
        return "Week 2"
    elif day <= 21:
        return "Week 3"
    else:
        return "Week 4"

month_order = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

st.title("HR Schedule")

# uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
# uploaded_file = pd.read_csv('tes.csv')

#if uploaded_file is not None:
df = pd.read_csv('tes.csv')
df['created'] = pd.to_datetime(df['created'])
df['month'] = df['created'].dt.strftime('%B')
df['week'] = df['created'].apply(categorize_week)

# Pivot the data
df_pivot = df.pivot_table(
    index=['employee_name', 'position_name', 'month'],
    columns='week',
    values='client_name',
    aggfunc=lambda x: ', '.join(x.unique())
).reset_index()
df_pivot.fillna('-', inplace=True)
df_pivot['month'] = pd.Categorical(df_pivot['month'], categories=month_order, ordered=True)
df_pivot = df_pivot.sort_values(by=['employee_name', 'month'])

# Multi-select filters with narrow layout
col1, col2 = st.columns([1, 1])
all_employees = ['All'] + list(df_pivot['employee_name'].unique())
all_months = ['All'] + list(df_pivot['month'].unique())

with col1:
    selected_employees = st.multiselect("Select Employee(s)", options=all_employees, default=['All'])
with col2:
    selected_months = st.multiselect("Select Month(s)", options=all_months, default=['All'])

# Apply filters
if 'All' in selected_employees:
    selected_employees = df_pivot['employee_name'].unique()
if 'All' in selected_months:
    selected_months = df_pivot['month'].unique()

filtered_df = df_pivot[df_pivot['employee_name'].isin(selected_employees) & df_pivot['month'].isin(selected_months)]

# Display DataFrame
st.write("### Processed Data")
st.dataframe(filtered_df)