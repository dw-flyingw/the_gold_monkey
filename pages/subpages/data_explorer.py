import streamlit as st
import pandas as pd
import numpy as np

def show_data_explorer():
    st.subheader("📊 Data Explorer")
    st.markdown("*🦜 Upload and analyze CSV files*")
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file to explore"
    )
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success(f"Successfully loaded {len(df)} rows and {len(df.columns)} columns")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Data Preview")
                st.dataframe(df.head())
            with col2:
                st.subheader("Data Info")
                st.write(f"**Shape:** {df.shape}")
                st.write(f"**Columns:** {list(df.columns)}")
                st.write(f"**Data Types:**")
                st.write(df.dtypes)
            st.markdown("---")
            st.subheader("📈 Data Analysis")
            analysis_col1, analysis_col2 = st.columns(2)
            with analysis_col1:
                st.subheader("📊 Basic Statistics")
                if df.select_dtypes(include=[np.number]).columns.any():
                    st.write(df.describe())
                else:
                    st.info("No numeric columns found for statistical analysis")
            with analysis_col2:
                st.subheader("📋 Missing Values")
                missing_data = df.isnull().sum()
                if missing_data.sum() > 0:
                    st.write(missing_data[missing_data > 0])
                else:
                    st.success("No missing values found!")
            st.markdown("---")
            st.subheader("📊 Visualizations")
            viz_col1, viz_col2 = st.columns(2)
            with viz_col1:
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    selected_col = st.selectbox("Select column for histogram", numeric_cols)
                    if selected_col:
                        st.subheader(f"Histogram: {selected_col}")
                        st.bar_chart(df[selected_col].value_counts())
            with viz_col2:
                if len(numeric_cols) > 1:
                    st.subheader("Correlation Matrix")
                    corr_matrix = df[numeric_cols].corr()
                    st.write(corr_matrix)
        except Exception as e:
            st.error(f"Error loading file: {e}")
    else:
        st.info("👆 Upload a CSV file to get started")

if __name__ == "__main__":
    show_data_explorer() 