import streamlit as st
import pandas as pd
import numpy as np
# import asyncio
from sqlalchemy import create_engine, text
from annotated_text import annotated_text

DB_URL = "postgresql://neondb_owner:npg_cq2K3jhIQBEN@ep-nameless-salad-a5yrvfdl-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
engine = create_engine(DB_URL)

st.set_page_config(layout="wide")
st.title("HR Schedule")

@st.cache_data
def get_data():
    with engine.connect() as conn:
        query = text("""
        SELECT ho.employee_id, ho.employee_name, hj.position_name, tt.created, cc.client_name
        FROM project_project AS pp
        JOIN timesheet_timesheet AS tt ON pp.project_id = tt.project_id
        JOIN client_client AS cc ON pp.client_id = cc.client_id
        JOIN hr_employee AS ho ON tt.user_id = ho.user_id
        JOIN hr_position_assignment AS h ON h.employee_id = ho.employee_id
        JOIN hr_job_position AS hj ON h.position_id = hj.position_id
        ORDER BY tt.created;
        """)
        result = conn.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df

def categorize_week_vectorized(date_series):
    return np.where(date_series.dt.day <= 7, "Week 1",
           np.where(date_series.dt.day <= 14, "Week 2",
           np.where(date_series.dt.day <= 21, "Week 3", "Week 4")))

@st.cache_data
def preprocess_data(df):
    df_pivot = df.pivot_table(
        index=['employee_name', 'position_name', 'month'],
        columns='week',
        values='client_name',
        aggfunc=lambda x: ', '.join(x.unique())
    ).reset_index()
    df_pivot.fillna('-', inplace=True)
    return df_pivot.sort_values(by=['employee_name', 'month'])

# Load employees
# @st.cache_data
# def get_employees():
#     with engine.connect() as conn:
#         query = text("""
#         SELECT ho.employee_id, ho.employee_name, hj.position_name
#         FROM hr_employee AS ho
#         JOIN hr_position_assignment AS h ON h.employee_id = ho.employee_id
#         JOIN hr_job_position AS hj ON h.position_id = hj.position_id
#         ORDER BY ho.employee_name;
#         """)
#         result = conn.execute(query)
#         df = pd.DataFrame(result.fetchall(), columns=result.keys())
#     return df

# Insert new employee data
def insert_data(df):
    df.to_sql("new_employee_records", con=engine, if_exists="append", index=False)

# Batch delete function
def delete_records(records):
    with engine.connect() as conn:
        for record in records:
            query = text("""
                DELETE FROM new_employee_records
                WHERE employee_id = :employee_id 
                AND created = :created 
                AND client_name = :client_name;
            """)
            conn.execute(query, {
                "employee_id": record[0],
                "created": record[1],
                "client_name": record[2]
            })
        conn.commit()

# Fetch inserted records
def get_inserted_data():
    with engine.connect() as conn:
        query = text("SELECT * FROM new_employee_records ORDER BY created DESC;")
        result = conn.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df

employees_df = get_data()

with st.expander("Add New Data"):
    col1, col2 = st.columns([1, 1])

    with col1:
        selected_employees = st.multiselect(  
            "Select Employees",
            employees_df['employee_name'].sort_values().unique()
        )

    created_date = st.date_input("Select Created Date")
    client_names = st.multiselect(
        "Select Client(s)",
        employees_df['client_name'].sort_values().unique()
    )

    if st.button("Commit"):
        if not selected_employees:
            st.warning("Please select at least one employee.")
        elif not client_names:
            st.warning("Please select at least one client.")
        else:
            new_entries = []
            for employee in selected_employees:
                position_name = employees_df.loc[employees_df["employee_name"] == employee, "position_name"].values[0]
                employee_id = employees_df.loc[employees_df["employee_name"] == employee, "employee_id"].values[0]
                
                for client in client_names:
                    new_entries.append({
                        "employee_id": employee_id,
                        "employee_name": employee,
                        "position_name": position_name,
                        "created": created_date,
                        "client_name": client
                    })

            # Convert list to DataFrame and insert
            new_entries_df = pd.DataFrame(new_entries)
            insert_data(new_entries_df)

            st.success(f"Successfully added {len(new_entries)} records!")
            st.session_state["last_inserted"] = new_entries_df

    st.write("### Recently Inserted Records")
    inserted_data = get_inserted_data()
    st.dataframe(inserted_data.iloc[::-1].head(5), use_container_width=True)

with st.expander("Delete Data"):
    if 'Delete?' not in inserted_data.columns:
        inserted_data['Delete?'] = False  # Default unchecked

    # Multi-select filter for employee names
    selected_employees = st.multiselect(
        "Filter by Employee Name", 
        options=inserted_data["employee_name"].unique(), 
        default=inserted_data["employee_name"].unique()  # Default selects all
    )

    filtered_data = inserted_data[inserted_data["employee_name"].isin(selected_employees)]

    edited_df = st.data_editor(
        filtered_data,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Delete?": st.column_config.CheckboxColumn(required=True)
        }
    )

    # Delete selected rows
    if st.button("Delete Selected Rows"):
        selected_records = edited_df[edited_df["Delete?"]]

        if not selected_records.empty:
            records_to_delete = [
                (row["employee_id"], row["created"], row["client_name"])
                for _, row in selected_records.iterrows()
            ]
            delete_records(records_to_delete)
            st.success("Selected records deleted successfully!")
            st.rerun()
        else:
            st.warning("No records selected for deletion.")

df = get_data()
df['created'] = pd.to_datetime(df['created'])
df['month'] = df['created'].dt.strftime('%B %y')
df['week'] = categorize_week_vectorized(df['created'])
df_pivot = preprocess_data(df)

# st.dataframe(inserted_data.iloc[::-1].head(5), use_container_width=True)
col1, col2 = st.columns([0.5, 0.5])
all_employees = ['All'] + list(df_pivot['employee_name'].unique())
all_months = ['All'] + list(df_pivot['month'].unique())

today1 = pd.Timestamp.today().strftime('%B %y')

with col1:
    selected_employees = st.multiselect("Select Employee(s)", options=all_employees, default=['Achmad Nur Huda'])
with col2:
    selected_month = st.selectbox("Select Month", options=all_months, index=all_months.index(today1))

if 'All' in selected_employees:
    selected_employees = df_pivot['employee_name'].unique()
if selected_month == 'All':
    selected_months = df_pivot['month'].unique()
else:
    selected_months = [selected_month]


filtered_df = df_pivot[df_pivot['employee_name'].isin(selected_employees) & df_pivot['month'].isin(selected_months)]

df1 = inserted_data.drop(columns='employee_id', axis=1)
df1['created'] = pd.to_datetime(df1['created'])
df1['month'] = df1['created'].dt.strftime('%B %y')
df1['week'] = categorize_week_vectorized(df1['created'])
df1_pivot = preprocess_data(df1)
filtered_df1 = df1_pivot[df1_pivot['employee_name'].isin(selected_employees) & df1_pivot['month'].isin(selected_months)]

filtered_df["source"] = "filtered"  # Green clients
filtered_df1["source"] = "new"  # Blue clients

df1_melted = filtered_df.melt(id_vars=['employee_name','position_name' ,'month','source'], var_name='Week', value_name='client_name')
df2_melted = filtered_df1.melt(id_vars=['employee_name','position_name' ,'month','source'], var_name='Week', value_name='client_name')
combined_df = pd.concat([df1_melted, df2_melted], ignore_index=True)

def format_jobs(group):
    blue_jobs = [f"<span style='color:blue'>{x}</span>" for x in group[group["source"] == "new"]["client_name"]]
    red_jobs = [f"<span style='color:red'>{x}</span>" for x in group[group["source"] == "filtered"]["client_name"]]
    return ", ".join(blue_jobs + red_jobs)

styled_combined = combined_df.groupby(['employee_name','position_name' ,'month', 'Week']).apply(format_jobs).reset_index()
styled_combined.columns = ['employee_name','position_name' ,'month', 'Week', 'client_name']
styled_pivot = styled_combined.pivot(index='employee_name', columns='Week', values='client_name').reset_index()
styled_pivot.columns.name = None

ordered_weeks = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
available_weeks = [col for col in ordered_weeks if col in styled_pivot.columns]
styled_pivot = styled_pivot[['employee_name'] + available_weeks]

st.markdown(styled_pivot.to_html(escape=False, index=False), unsafe_allow_html=True)

with st.expander("Alternatif"):
    # Gabungkan kedua dataframe
    df_all = pd.concat([df1_melted, df2_melted], ignore_index=True)

    # Color code jobs
    def style_clients(row):
        if row['source'] == 'new':
            return f"<span style='color:blue'>{row['client_name']}</span>"
        else:
            return f"<span style='color:red'>{row['client_name']}</span>"

    df_all['styled_job'] = df_all.apply(style_clients, axis=1)

    # Group by employee_name, month, week
    df_grouped = df_all.groupby(['employee_name', 'position_name', 'month', 'Week'], as_index=False).agg({'styled_job': ', '.join})

    # Display in readable format
    st.write("📊 **Grouped Job Assignments with Colored Labels**")

    for index, row in df_grouped.iterrows():
        html_text = f"""
        <b>👤 Employee:</b> {row['employee_name']} &nbsp;&nbsp; 
        <b>💼 Position:</b> {row['position_name']} &nbsp;&nbsp; 
        <b>📅 Month:</b> {row['month']} &nbsp;&nbsp; 
        <b>🗓️ Week:</b> {row['Week']}<br>
        <b>📌 Jobs:</b> {row['styled_job']}
        <hr>
        """
        st.markdown(html_text, unsafe_allow_html=True)



with st.expander("Alternatif (Annotated Text Version)"):
    df_all = pd.concat([df1_melted, df2_melted], ignore_index=True)
    df_all = df_all[df_all['client_name'] != "-"]

    def style_clients(row):
        if row['source'] == 'new':
            return (row['client_name'], "NEW", "#1E90FF")  # Blue for new
        else:
            return (row['client_name'], "EXISTING", "#FF4500")  # Red for existing

    df_all['styled_job'] = df_all.apply(style_clients, axis=1)

    # Group into a list of annotated elements
    grouped = df_all.groupby(['employee_name', 'position_name', 'month'])
    st.write("📊 **Grouped Job Assignments with Colored Labels (Annotated Text)**")

    for (employee, position, month), group in grouped:
        st.markdown(f"**👤 Employee:** {employee}  \n**💼 Position:** {position}  \n**📅 Month:** {month}")
        
        for week in ['Week 1', 'Week 2', 'Week 3', 'Week 4']:
            week_jobs = group[group['Week'] == week]['styled_job'].tolist()
            if week_jobs:
                st.markdown(f"**🗓️ {week}:**")
                annotated_text(*week_jobs)

        st.markdown("---")
