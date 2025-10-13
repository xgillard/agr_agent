import pandas as pd
import streamlit as st

st.set_page_config(layout="wide")

df = pd.read_csv("tool_classifier.csv", header=0)
df = df[["input", "prompt", "tool"]]

with st.container(width=1800):
    st.data_editor(
        df[["prompt", "tool"]], 
        column_config={
            "tool": st.column_config.SelectboxColumn(
                label="tool", 
                width="small",
                options=[
                "Respond",
                "Analyses of Records / Free Search", 
                "Analyses of Records / Search Person", 
                "Genealogical sources / Church Registers",
                "Genealogical sources / Civil State Registers",
                "Online Help Resources",
            ])
        },
        hide_index=True,
        width="stretch",
        height=800,
    )

st.button(label="Save", on_click=lambda: df.to_csv("curated.csv"))