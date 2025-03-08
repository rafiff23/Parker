# import streamlit as st
# import pandas as pd
# from annotated_text import annotated_text


# st.set_page_config(layout="wide") 

# def categorize_week(date):
#     day = date.day
#     if day <= 7:
#         return "Week 1"
#     elif day <= 14:
#         return "Week 2"
#     elif day <= 21:
#         return "Week 3"
#     else:
#         return "Week 4"

# month_order = [
#     "January", "February", "March", "April", "May", "June",
#     "July", "August", "September", "October", "November", "December"
# ]

# st.title("HR Schedule")

# # Editable data editor
# st.write("### Add New Data")


# df = pd.read_csv('tes.csv')
# df['created'] = pd.to_datetime(df['created'])
# df['month'] = df['created'].dt.strftime('%B')
# df['week'] = df['created'].apply(categorize_week)

# edited_df = st.data_editor(
#     df,
#     num_rows="dynamic",  # Allows adding new rows
#     use_container_width=True
# )

# # Save updated DataFrame if changed
# if st.button("Save Changes"):
#     edited_df.to_csv("tes.csv", index=False)
#     st.success("Data saved successfully!")

# df_pivot = df.pivot_table(
#     index=['employee_name', 'position_name', 'month'],
#     columns='week',
#     values='client_name',
#     aggfunc=lambda x: ', '.join(x.unique())
# ).reset_index()
# df_pivot.fillna('-', inplace=True)
# df_pivot['month'] = pd.Categorical(df_pivot['month'], categories=month_order, ordered=True)
# df_pivot = df_pivot.sort_values(by=['employee_name', 'month'])

# col1, col2 = st.columns([0.5, 0.5])
# all_employees = ['All'] + list(df_pivot['employee_name'].unique())
# all_months = ['All'] + list(df_pivot['month'].unique())

# with col1:
#     selected_employees = st.multiselect("Select Employee(s)", options=all_employees, default=['All'])
# with col2:
#     selected_months = st.multiselect("Select Month(s)", options=all_months, default=['All'])

# if 'All' in selected_employees:
#     selected_employees = df_pivot['employee_name'].unique()
# if 'All' in selected_months:
#     selected_months = df_pivot['month'].unique()

# filtered_df = df_pivot[df_pivot['employee_name'].isin(selected_employees) & df_pivot['month'].isin(selected_months)]

# def highlight_weeks(val):
#     if val != "-" and val != "" and not pd.isna(val):
#         return "background-color: lightgreen; color: black"
#     return ""

# styled_df = filtered_df.style.applymap(highlight_weeks, subset=["Week 1", "Week 2", "Week 3", "Week 4"])

# st.write("### Processed Data")
# st.dataframe(styled_df)

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Koneksi ke Neon PostgreSQL
DB_URL = "postgresql://neondb_owner:npg_cq2K3jhIQBEN@ep-nameless-salad-a5yrvfdl-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(DB_URL)

def get_data():
    query = """
    SELECT ho.employee_name, hj.position_name , tt.created, cc.client_name
    FROM project_project AS pp
    JOIN timesheet_timesheet AS tt ON pp.project_id = tt.project_id
    JOIN client_client AS cc on pp.client_id = cc.client_id
    JOIN hr_employee AS ho ON tt.user_id = ho.user_id
    JOIN hr_position_assignment AS h ON h.employee_id = ho.employee_id
    JOIN hr_job_position AS hj ON h.position_id = hj.position_id
    ORDER BY tt.created;
    """
    return pd.read_sql(query, engine)

st.set_page_config(layout="wide")
st.title("HR Schedule")

st.write("### Add New Data")

df = get_data()
df['created'] = pd.to_datetime("created")
df['month'] = df['created'].dt.strftime('%B')

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

df['week'] = df['created'].apply(categorize_week)

edited_df = st.data_editor(
    df,
    num_rows="dynamic",
    use_container_width=True
)

if st.button("Save Changes"):
    st.warning("Changes are currently not saved to the database. Implement save logic if needed.")
    st.success("Data displayed successfully!")

month_order = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

df_pivot = df.pivot_table(
    index=['employee_name', 'position_name', 'month'],
    columns='week',
    values='user_id',
    aggfunc='count'
).reset_index()
df_pivot.fillna('-', inplace=True)
df_pivot['month'] = pd.Categorical(df_pivot['month'], categories=month_order, ordered=True)
df_pivot = df_pivot.sort_values(by=['employee_name', 'month'])

col1, col2 = st.columns([0.5, 0.5])
all_employees = ['All'] + list(df_pivot['employee_name'].unique())
all_months = ['All'] + list(df_pivot['month'].unique())

with col1:
    selected_employees = st.multiselect("Select Employee(s)", options=all_employees, default=['All'])
with col2:
    selected_months = st.multiselect("Select Month(s)", options=all_months, default=['All'])

if 'All' in selected_employees:
    selected_employees = df_pivot['employee_name'].unique()
if 'All' in selected_months:
    selected_months = df_pivot['month'].unique()

filtered_df = df_pivot[df_pivot['employee_name'].isin(selected_employees) & df_pivot['month'].isin(selected_months)]

def highlight_weeks(val):
    if val != "-" and val != "" and not pd.isna(val):
        return "background-color: lightgreen; color: black"
    return ""

styled_df = filtered_df.style.applymap(highlight_weeks, subset=["Week 1", "Week 2", "Week 3", "Week 4"])

st.write("### Processed Data")
st.dataframe(styled_df)
