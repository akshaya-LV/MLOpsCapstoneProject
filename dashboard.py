import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# --- 1. Data Preparation and Loading ---
st.set_page_config(layout="wide")
st.title("Retail Store & Customer Insights")
st.markdown("This dashboard visualizes key aspects of a sample retail store dataset.")

# Function to load data from a user-uploaded CSV file
@st.cache_data
def load_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        # Assuming the CSV has a 'total_revenue' column, or we can create one
        if 'total_revenue' not in df.columns:
            if 'quantity' in df.columns and 'price' in df.columns:
                df['total_revenue'] = df['quantity'] * df['price']
            else:
                st.error("Uploaded file must contain 'total_revenue' or both 'quantity' and 'price' columns.")
                return None
        return df
    except Exception as e:
        st.error(f"Error: Unable to read the uploaded CSV file. {e}")
        return None

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    df = load_data(uploaded_file)
    if df is not None:
        # Pre-processing for visualizations
        # Ensure 'invoice_date' column exists and is in datetime format
        if 'invoice_date' in df.columns:
            df['invoice_date'] = pd.to_datetime(df['invoice_date'])
            df['invoice_month'] = df['invoice_date'].dt.strftime('%Y-%m')
            df['day_of_week'] = df['invoice_date'].dt.day_name()
            df['month_name'] = df['invoice_date'].dt.strftime('%B')
        else:
            st.warning("The 'invoice_date' column was not found. Seasonal trendlines and day of week plots will not be displayed.")
            df['invoice_month'] = None
            df['day_of_week'] = None
            df['month_name'] = None
        
        st.write("Data successfully loaded!")
        st.dataframe(df.head())

# Pre-processing for visualizations
df['invoice_month'] = df['invoice_date'].dt.strftime('%Y-%m')
df['day_of_week'] = df['invoice_date'].dt.day_name()
df['month_name'] = df['invoice_date'].dt.strftime('%B')

# --- 2. Create the Dashboard Layout ---
st.header("1. Correlation Heatmap")
st.markdown("A heatmap to show the correlation between numerical features.")
numerical_cols = ['age', 'quantity', 'price', 'total_revenue']
corr_matrix = df[numerical_cols].corr()

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
st.pyplot(fig)

st.header("2. Seasonal Trendlines")
st.markdown("Monthly trend of total revenue over time.")

monthly_revenue = df.groupby('invoice_month')['total_revenue'].sum().reset_index()

fig_trend = px.line(monthly_revenue, x='invoice_month', y='total_revenue',
                    title='Total Revenue Over Time',
                    labels={'invoice_month': 'Month', 'total_revenue': 'Total Revenue ($)'})
st.plotly_chart(fig_trend)


st.header("3. Univariate Bar Plots")
st.markdown("Distribution of categorical variables.")
st.write("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Gender Distribution")
    gender_counts = df['gender'].value_counts().reset_index()
    gender_counts.columns = ['gender', 'count']
    fig_gender = px.bar(gender_counts, x='gender', y='count', color='gender',
                        title='Customer Count by Gender')
    st.plotly_chart(fig_gender)

with col2:
    st.subheader("Category Distribution")
    category_counts = df['category'].value_counts().reset_index()
    category_counts.columns = ['category', 'count']
    fig_category = px.bar(category_counts, x='category', y='count', color='category',
                          title='Customer Count by Category')
    st.plotly_chart(fig_category)

st.header("4. Bivariate Bar Plots")
st.markdown("Relationship between a categorical and a numerical variable.")
st.write("---")

col3, col4 = st.columns(2)

with col3:
    st.subheader("Average Revenue by Shopping Mall")
    mall_revenue = df.groupby('shopping_mall')['total_revenue'].mean().reset_index()
    fig_mall = px.bar(mall_revenue, x='shopping_mall', y='total_revenue', color='shopping_mall',
                      title='Average Revenue per Shopping Mall',
                      labels={'total_revenue': 'Average Revenue ($)'})
    st.plotly_chart(fig_mall)

with col4:
    st.subheader("Total Revenue by Day of the Week")
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_revenue = df.groupby('day_of_week')['total_revenue'].sum().reindex(day_order).reset_index()
    fig_day = px.bar(day_revenue, x='day_of_week', y='total_revenue', color='day_of_week',
                     title='Total Revenue by Day of Week',
                     labels={'total_revenue': 'Total Revenue ($)'})
    st.plotly_chart(fig_day)

st.write("---")
# --- NEW: Customer Segment Analysis Plots ---
if 'customer_segment_y' in df.columns:
    st.subheader("Customer Segment Bivariate Analysis")
    st.markdown("---")
            
    col_seg1, col_seg2, col_seg3 = st.columns(3)
            
    # Dynamic check for payment column (based on image truncated name 'payment_me' or similar)
    payment_col = next((col for col in df.columns if 'payment_method' in col.lower()), None)
            
    # Plot 1: Customer Segment vs Shopping Mall
    with col_seg1:
        if 'shopping_mall' in df.columns:
            st.caption("Segment Count by Shopping Mall")
            segment_mall = df.groupby(['customer_segment_y', 'shopping_mall']).size().reset_index(name='count')
            fig_seg_mall = px.bar(segment_mall, x='shopping_mall', y='count', color='customer_segment_y', title='Segment vs. Mall',
            labels={'customer_segment_y': 'Segment', 'shopping_mall': 'Mall'})
            st.plotly_chart(fig_seg_mall)
        else:
            st.warning("Skipping Segment vs Mall plot: 'shopping_mall' column missing.")
            
            # Plot 2: Customer Segment vs Payment Method
    with col_seg2:
        if payment_col:
            st.caption("Segment Count by Payment Method")
            segment_payment = df.groupby(['customer_segment_y', payment_col]).size().reset_index(name='count')
            fig_seg_payment = px.bar(segment_payment, x=payment_col, y='count', color='customer_segment_y',
            title='Segment vs. Payment Method',
            labels={'customer_segment_y': 'Segment', payment_col: 'Payment Method'})
            st.plotly_chart(fig_seg_payment)
        else:
            st.warning("Skipping Segment vs Payment plot: Payment column (containing 'payment') missing.")
            
            # Plot 3: Customer Segment vs Category
    with col_seg3:
        if 'category' in df.columns:
            st.caption("Segment Count by Category")
            segment_category = df.groupby(['customer_segment_y', 'category']).size().reset_index(name='count')
            fig_seg_category = px.bar(segment_category, x='category', y='count', color='customer_segment_y',
                                              title='Segment vs. Category',
                                              labels={'customer_segment_y': 'Segment', 'category': 'Category'})
            st.plotly_chart(fig_seg_category)
        else:
            st.warning("Skipping Segment vs Category plot: 'category' column missing.")
else:
    st.warning("Cannot perform customer segment analysis: 'customer_segment' column is missing or could not be created (requires 'customer_id' and 'total_revenue').")
        
st.write("---")
st.info("The visualizations are based on the data in your uploaded CSV file.")

#st.info("The visualizations are based on a randomly generated dataset for demonstration purposes.")
#streamlit run dashboard.py