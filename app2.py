import streamlit as st
import pandas as pd
import altair as alt

st.title("Leads")

df = pd.read_csv('leads_clean.csv')
df = df.drop(columns=['Unnamed: 0', 'No'], axis=1)
df1 = df.groupby('Status')['Fee'].sum().reset_index().sort_values(by = 'Fee', ascending=False)

# a = alt.Chart(df1).mark_bar().encode(
#     y=alt.Y('Status', sort='-x'),  
#     x=alt.X('Fee', axis=alt.Axis(title="Fee", labels=True)) 
# )

a = alt.Chart(df1).mark_bar().encode(
    x=alt.X('Status', sort='-y'),
    y=alt.Y('Fee', axis=alt.Axis(title="Fee", labels=False))
)

df2 = df.groupby('Status')['Fee'].count().reset_index().sort_values(by = 'Fee', ascending=False)
df2.rename(columns={'Fee' : 'Total Count'}, inplace=True)
chart = alt.Chart(df2).mark_arc(innerRadius=50).encode(
    theta="Total Count:Q",
    color=alt.Color("Status:N", legend=alt.Legend(orient="top")),
    tooltip=["Status", "Total Count"]
).interactive()


col1, col2 = st.columns([1, 1])
with col1:
    st.altair_chart(a)
with col2 : 
    st.altair_chart(chart)

## Write 
if "df_write" not in st.session_state:
    st.session_state.df_write = pd.DataFrame(
        [{"Jenis Pekerjaan": "", "Nama Calon Klien": "", "Detail Pekerjaan": "", 'Fee': 0, 'PIC': "", 'Status': "", 'Notes': ""}]
    )

all_status = ['All'] + list(df['Status'].unique())
all_client = ['All'] + list(df['Nama Calon Klien'].unique())
all_job = ['All'] + list(df['Jenis Pekerjaan'].unique())


tab1, tab2 = st.tabs(["📈 Add Data", "🗃 Data"])
with tab1:
    st.subheader('Add New Data')
    edited_df = st.data_editor(st.session_state.df_write)
    col3, col4 = st.columns([1, 1])
    with col3:
        if st.button("Add New Row"):
            new_row = pd.DataFrame(
                [{"Jenis Pekerjaan": "", "Nama Calon Klien": "", "Detail Pekerjaan": "", 'Fee': 0, 'PIC': "", 'Status': "", 'Notes': ""}]
            )
            st.session_state.df_write = pd.concat([st.session_state.df_write, new_row], ignore_index=True)
            st.rerun() 
    with col4:
        if st.button("Commit"):
            df = pd.concat([df, edited_df], ignore_index=True)
            st.success("Data appended successfully!")
with tab2:
    col5, col6, col7 = st.columns([1, 1, 1])
    with col5:
        selected_status = st.multiselect("Select Status", options=all_status, default=['All'])
    with col6:
        selected_client = st.multiselect("Select Client", options=all_client, default=['All'])
    with col7:
        selected_job = st.multiselect("Select Job", options=all_job, default=['All'])
    st.subheader('Full data')
    if 'All' in selected_status:
        selected_status = df['Status'].unique()
    if 'All' in selected_client:
        selected_client = df['Nama Calon Klien'].unique()
    if 'All' in selected_job:
        selected_job = df['Jenis Pekerjaan'].unique()

    filtered_df = df[df['Status'].isin(selected_status) & df['Nama Calon Klien'].isin(selected_client) & df['Jenis Pekerjaan'].isin(selected_job)]
    st.dataframe(filtered_df)

# col3, col4 = st.columns([1, 1])
# with col3:
#     if st.button("Add New Row"):
#         new_row = pd.DataFrame(
#             [{"Jenis Pekerjaan": "", "Nama Calon Klien": "", "Detail Pekerjaan": "", 'Fee': 0, 'PIC': "", 'Status': "", 'Notes': ""}]
#         )
#         st.session_state.df_write = pd.concat([st.session_state.df_write, new_row], ignore_index=True)
#         st.rerun() 
# with col4:
#     if st.button("Commit"):
#         df = pd.concat([df, edited_df], ignore_index=True)
#         st.success("Data appended successfully!")