import streamlit as st
import pandas as pd

st.subheader('Orderbook')

df_orderbook = pd.read_csv('orderbook.csv')

if "df_write_orderbook" not in st.session_state:
    st.session_state.df_write_orderbook = pd.DataFrame(
        [{"Nama Perusahaan": "", "Termin": "", "Pekerjaan": "", "Fee": 0, "BULAN": "", "WEEK": "", "ESTIMASI CASH IN": "", "PIC": ""}]
    )

all_company_orderbook = ['All'] + list(df_orderbook['Nama Perusahaan'].unique())
all_termin = ['All'] + list(df_orderbook['Termin'].unique())
all_job_orderbook = ['All'] + list(df_orderbook['Pekerjaan'].unique())

tab1, tab2 = st.tabs(["Add Data", "Full Data"])

with tab1:
    edited_df = st.data_editor(st.session_state.df_write_orderbook, key="orderbook_editor")

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Add New Row", key="add_orderbook_row"):
            new_row = pd.DataFrame(
                [{"Nama Perusahaan": "", "Termin": "", "Pekerjaan": "", "Fee": 0, "BULAN": "", "WEEK": "", "ESTIMASI CASH IN": "", "PIC": ""}]
            )
            st.session_state.df_write_orderbook = pd.concat([st.session_state.df_write_orderbook, new_row], ignore_index=True)
            st.rerun()

    with col2:
        if st.button("Commit", key="commit_orderbook"):
            df_orderbook = pd.concat([df_orderbook, edited_df], ignore_index=True)
            st.success("Data appended successfully!")

with tab2:
    col3, col4, col5 = st.columns([1, 1, 1])

    with col3:
        selected_company = st.multiselect("Select Company", options=all_company_orderbook, default=['All'], key="company_orderbook")
    with col4:
        selected_termin = st.multiselect("Select Termin", options=all_termin, default=['All'], key="termin_orderbook")
    with col5:
        selected_job = st.multiselect("Select Job", options=all_job_orderbook, default=['All'], key="job_orderbook")

    if 'All' in selected_company:
        selected_company = df_orderbook['Nama Perusahaan'].unique()
    if 'All' in selected_termin:
        selected_termin = df_orderbook['Termin'].unique()
    if 'All' in selected_job:
        selected_job = df_orderbook['Pekerjaan'].unique()

    filtered_df = df_orderbook[
        df_orderbook['Nama Perusahaan'].isin(selected_company) &
        df_orderbook['Termin'].isin(selected_termin) &
        df_orderbook['Pekerjaan'].isin(selected_job)
    ]

    st.dataframe(filtered_df)

st.subheader('Greenbook')

df_greenbook = pd.read_csv('greenbook.csv')
if "df_write_greenbook" not in st.session_state:
    st.session_state.df_write_greenbook = pd.DataFrame(
        [{"Nama Perusahaan": "", "Pekerjaan": "", "Fee": 0, 'PIC': "", 'Schedule Invoice': "", 'Estimasi Cash In': ""}]
    )

all_company_greenbook = ['All'] + list(df_greenbook['Nama Perusahaan'].unique())
all_schedule = ['All'] + list(df_greenbook['Schedule Invoice'].unique())
all_job_greenbook = ['All'] + list(df_greenbook['Pekerjaan'].unique())

# Greenbook
tab3, tab4, tab5 = st.tabs(["Add Data", "Schedule", "Total"])

with tab3:
    edited_df = st.data_editor(st.session_state.df_write_greenbook, key="greenbook_editor")

    col6, col7 = st.columns([1, 1])
    
    with col6:
        if st.button("Add New Row", key="add_greenbook_row"):
            new_row = pd.DataFrame(
                 [{"Nama Perusahaan": "", "Pekerjaan": "", "Fee": 0, 'PIC': "", 'Schedule Invoice': "", 'Estimasi Cash In': ""}]
            )
            st.session_state.df_write_greenbook = pd.concat([st.session_state.df_write_greenbook, new_row], ignore_index=True)
            st.rerun()

    with col7:
        if st.button("Commit", key="commit_greenbook"):
            df_greenbook = pd.concat([df_greenbook, edited_df], ignore_index=True)
            st.success("Data appended successfully!")

with tab4:
    col8, col9, col10 = st.columns([1, 1, 1])
    
    with col8:
        selected_status = st.multiselect("Select Company", options=all_company_greenbook, default=['All'], key="company_greenbook")
    with col9:
        selected_client = st.multiselect("Select Schedule", options=all_schedule, default=['All'], key="schedule_greenbook")
    with col10:
        selected_job = st.multiselect("Select Job", options=all_job_greenbook, default=['All'], key="job_greenbook")

    if 'All' in selected_status:
        selected_status = df_greenbook['Nama Perusahaan'].unique()
    if 'All' in selected_client:
        selected_client = df_greenbook['Schedule Invoice'].unique()
    if 'All' in selected_job:
        selected_job = df_greenbook['Pekerjaan'].unique()

    filtered_df = df_greenbook[
        df_greenbook['Nama Perusahaan'].isin(selected_status) &
        df_greenbook['Schedule Invoice'].isin(selected_client) &
        df_greenbook['Pekerjaan'].isin(selected_job)
    ]

    st.dataframe(filtered_df)

with tab5:
    df1 = df_greenbook.groupby(['Nama Perusahaan', 'Pekerjaan'])['Fee'].sum().reset_index()
    
    col11, col12 = st.columns([1, 1])
    
    with col11:
        selected_status = st.multiselect("Select Company", options=all_company_greenbook, default=['All'], key="company_greenbook_total")
    with col12:
        selected_job = st.multiselect("Select Job", options=all_job_greenbook, default=['All'], key="job_greenbook_total")

    if 'All' in selected_status:
        selected_status = df_greenbook['Nama Perusahaan'].unique()
    if 'All' in selected_job:
        selected_job = df_greenbook['Pekerjaan'].unique()

    filtered_df = df1[df1['Nama Perusahaan'].isin(selected_status) & df1['Pekerjaan'].isin(selected_job)]
    
    st.dataframe(filtered_df)
