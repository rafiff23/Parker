import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

st.set_page_config(layout="wide") 

st.title("Leads")

# Load data
df = pd.read_csv('leads_clean.csv')
df = df.drop(columns=['Unnamed: 0', 'No'], axis=1)

## Write
if "df_write" not in st.session_state:
    st.session_state.df_write = pd.DataFrame(
        [{"Jenis Pekerjaan": "", "Nama Calon Klien": "", "Detail Pekerjaan": "", 'Fee': 0, 'PIC': "", 'Status': "", 'Status Level': "", 'Notes': ""}]
    )

with st.expander("Add New Data"):
    edited_df = st.data_editor(st.session_state.df_write)
    col3, col4 = st.columns([1, 1])

    with col3:
        if st.button("Add New Row"):
            new_row = pd.DataFrame(
                [{"Jenis Pekerjaan": "", "Nama Calon Klien": "", "Detail Pekerjaan": "", 'Fee': 0, 'PIC': "", 'Status': "", 'Status Level': "", 'Notes': ""}]
            )
            st.session_state.df_write = pd.concat([st.session_state.df_write, new_row], ignore_index=True)
            st.rerun()

    with col4:
        if st.button("Commit"):
            valid_rows = edited_df.dropna(how="all")  
            valid_rows = valid_rows[
                valid_rows.apply(lambda row: row.astype(str).str.strip().ne("").sum() >= 2, axis=1)
            ] 
            if not valid_rows.empty:
                df = pd.concat([df, valid_rows], ignore_index=True)
                st.success("Data appended successfully!")
            else:
                st.warning("No valid rows to append. Fill at least two columns.")


col1, col2= st.columns([0.5, 0.5])

count_confirm = df[df['Status Level'].str.lower().isin(['confirm'])].shape[0]
count_opportunity = df[df['Status Level'].str.lower().isin(['opportunity'])].shape[0]
# count_weak = df[df['Status Level'].str.lower().isin(['weak'])].shape[0]

total_fee_confirm = df[df['Status Level'].str.lower().isin(['confirm'])]['Fee'].sum()
total_fee_opportunity = df[df['Status Level'].str.lower().isin(['opportunity'])]['Fee'].sum()
# total_fee_weak = df[df['Status Level'].str.lower().isin(['weak'])]['Fee'].sum()

formatted_fee_confirm = f"Rp {total_fee_confirm:,.0f}"
formatted_fee_opportunity = f"Rp {total_fee_opportunity:,.0f}"
# formatted_fee_weak = f"Rp {total_fee_weak:,.0f}"

st.markdown("""
    <style>
        .metric-container {
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 15px;
            border-radius: 10px;
            min-width: 150px;
            min-height: 100px;
            color: white;
        }
        .confirm-bg { background-color: #007BFF; } /* Blue */
        .opportunity-bg { background-color: #28A745; } /* Green */
        .weak-bg { background-color: #DC3545; } /* Red */
        .metric-title { font-size: 24px; font-weight: bold; }
        .metric-value { font-size: 20px; font-weight: bold; }
        .metric-delta { font-size: 20px; opacity: 0.8; }
    </style>
""", unsafe_allow_html=True)

with col1:
    st.markdown(f"""
        <div class='metric-container confirm-bg'>
            <div class='metric-title'>Confirm</div>
            <div class='metric-value'>{count_confirm}</div>
            <div class='metric-delta'>{formatted_fee_confirm}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class='metric-container opportunity-bg'>
            <div class='metric-title'>Opportunity</div>
            <div class='metric-value'>{count_opportunity}</div>
            <div class='metric-delta'>{formatted_fee_opportunity}</div>
        </div>
    """, unsafe_allow_html=True)

# with col3:
#     st.markdown(f"""
#         <div class='metric-container weak-bg'>
#             <div class='metric-title'>Weak</div>
#             <div class='metric-value'>{count_weak}</div>
#             <div class='metric-delta'>{formatted_fee_weak}</div>
#         </div>
#     """, unsafe_allow_html=True)



df_confirmed = df[df['Status Level'].str.lower().isin(['confirm'])].drop(columns = 'Status Level')
df_opportunity = df[df['Status Level'].str.lower().isin(['opportunity'])].drop(columns = 'Status Level')
df_weak = df[df['Status Level'].str.lower().isin(['weak'])].drop(columns = 'Status Level')

# st.markdown("""
#     <style>
#         .block-container {
#             padding-top: 1rem;
#             padding-bottom: 0rem;
#             margin: 0;
#         }
#         .stDataFrame {
#             max-height: 500px !important;  
#             overflow: auto !important;
#         }
#     </style>
# """, unsafe_allow_html=True)

col1, col2 = st.columns([0.5, 0.5])

with col1:
    st.subheader("Confirmed")
    with st.container(border = True):
        tab1, tab2 = st.tabs(["Add Data", "Status Level"])
        with tab1:
            st.dataframe(df_confirmed.style.format({"Fee": lambda x: f"Rp {x:,.0f}".replace(",", ".")}), use_container_width=True) 
        with tab2:
            df_status_confirm = df_confirmed.groupby('Status')['Fee'].sum().reset_index().sort_values(by='Fee', ascending=False)
            st.dataframe(df_status_confirm.style.format({"Fee": lambda x: f"Rp {x:,.0f}".replace(",", ".")}), use_container_width=True) 

with col2:
    st.subheader("Opportunity")
    with st.container(border = True):
        tab1, tab2 = st.tabs(["Add Data", "Status Level"])
        with tab1:
            st.dataframe(df_opportunity.style.format({"Fee": lambda x: f"Rp {x:,.0f}".replace(",", ".")}), use_container_width=True)
        with tab2:
            df_status_opportunity = df_opportunity.groupby('Status')['Fee'].sum().reset_index().sort_values(by='Fee', ascending=False)
            st.dataframe(df_status_opportunity.style.format({"Fee": lambda x: f"Rp {x:,.0f}".replace(",", ".")}), use_container_width=True) 

# col5, col6 = st.columns([0.5,0.5])


st.subheader("Weak")
with st.container(border = True):
    tab1, tab2 = st.tabs(["Add Data", "Status Level"])
    with tab1:
        st.dataframe(df_weak.style.format({"Fee": lambda x: f"Rp {x:,.0f}".replace(",", ".")}), use_container_width=True)  
    with tab2:
        df_status_weak = df_weak.groupby('Status')['Fee'].sum().reset_index().sort_values(by='Fee', ascending=False)
        st.dataframe(df_status_weak.style.format({"Fee": lambda x: f"Rp {x:,.0f}".replace(",", ".")}), use_container_width=True) 

# with col6:
#     st.subheader("Distribution of")
#     with st.container(border = True):
#         tab1, tab2 = st.tabs(["Status", "Status Level"])
#         with tab1:
#             df_count = df.groupby("Status Level").size().reset_index(name="Total")
#             df_count["Percentage"] = (df_count["Total"] / df_count["Total"].sum()) * 100
#             df_count["Percentage"] = df_count["Percentage"].round(1)  

#             chart = alt.Chart(df_count).mark_arc(innerRadius=80, outerRadius=150).encode(
#                 theta=alt.Theta("Total:Q", title="Total Count"),
#                 color=alt.Color("Status Level:N", title="Status Level"),
#                 tooltip=["Status Level:N", "Percentage:Q"]
#             ).interactive()

#             st.altair_chart(chart, use_container_width=True)
#         with tab2:
#             df_count = df.groupby(["Status Level", "Status"]).size().reset_index(name="Count")
#             fig = px.bar(df_count, x="Status Level", y="Count", color="Status", barmode="group")
#             fig.update_layout(
#                 legend=dict(title_text=""),  
#                 legend_orientation="h",
#                 legend_yanchor="bottom",
#                 legend_y=1.1,
#                 legend_xanchor="center",
#                 legend_x=0.5,
#                 xaxis_title="Status Level",
#             )
#             st.plotly_chart(fig, use_container_width=True)
