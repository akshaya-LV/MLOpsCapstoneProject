import streamlit as st
import pandas as pd
from databricks import sql
from datetime import datetime
import uuid

# --- 1. SETUP & CONFIGURATION ---

# IMPORTANT: Replace these with your actual Databricks table name and database.
DATABRICKS_TABLE_NAME = "workspace.default.customer_shopping_data_2"

# Load secrets from Streamlit secrets file (secrets.toml)
# Streamlit will look for these keys in .streamlit/secrets.toml
try:
    DATABRICKS_HOST = st.secrets["databricks"]["host"]
    DATABRICKS_HTTP_PATH = st.secrets["databricks"]["http_path"]
    DATABRICKS_TOKEN = st.secrets["databricks"]["token"]
except KeyError:
    st.error("Databricks secrets not configured! Please set 'host', 'http_path', and 'token' in .streamlit/secrets.toml")
    st.stop()


# --- 2. DATABASE CONNECTION FUNCTION ---

@st.cache_resource
def get_databricks_connection():
    """Initializes and caches a connection to the Databricks SQL Warehouse."""
    st.info("Attempting to connect to Databricks SQL Warehouse...")
    try:
        # --- CHANGE THE FUNCTION CALL HERE ---
        conn = sql.connect(
            server_hostname=DATABRICKS_HOST,
            http_path=DATABRICKS_HTTP_PATH,
            access_token=DATABRICKS_TOKEN
        )
        st.success("Successfully connected to Databricks.")
        return conn
    except Exception as e:
        st.error(f"Failed to connect to Databricks: {e}")
        st.stop()


# --- 3. DATA INGESTION FUNCTION ---

def append_data_to_databricks(new_record):
    """Appends a single record (list of values) to the Databricks table."""
    conn = get_databricks_connection()
    cursor = conn.cursor()

    # The SQL command uses placeholders (%s) to safely insert data, preventing SQL injection.
    sql_query = f"""
    INSERT INTO {DATABRICKS_TABLE_NAME} (
        invoice_no, customer_id, gender, age, category, quantity, price,
        payment_method, invoice_date, shopping_mall
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    try:
        # Execute the query, passing the list of values (new_record)
        cursor.execute(sql_query, new_record)
        
        # Commit the transaction to make changes permanent
        #conn.commit()
        st.success(f"Successfully inserted Invoice {new_record[0]} into Databricks!")
        return True
    except Exception as e:
        st.error(f"Error during SQL execution: {e}")
        #conn.rollback() # Rollback the transaction on failure
        return False
    finally:
        cursor.close()
        # NOTE: We keep the main connection open for the duration of the app session
        # because it is decorated with @st.cache_resource


# --- 4. STREAMLIT UI ---

st.set_page_config(page_title="Databricks Sales Data Ingester", layout="centered")
st.title("🛍️ Daily Sales Data Ingester")
st.markdown("Enter a single sales record to append to the Databricks Delta table.")

# Define the structure based on the image provided by the user
st.subheader("Sales Record Fields (Schema):")

# Use st.form to group input widgets and make an atomic submission
with st.form("sales_data_form"):
    
    # Generate unique ID for new invoice
    default_invoice_no = f"I{str(uuid.uuid4())[:7].upper()}"
    invoice_no = st.text_input("Invoice No", value=default_invoice_no, help="Unique identifier for the transaction.")

    # Input Fields based on the image
    col1, col2 = st.columns(2)
    with col1:
        customer_id = st.text_input("Customer ID", value="C" + str(uuid.uuid4())[:7].upper())
        age = st.number_input("Age", min_value=18, max_value=100, value=30, step=1)
        quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
        payment_method = st.selectbox("Payment Method", options=["Credit Card", "Ewallet", "Cash"])

    with col2:
        gender = st.selectbox("Gender", options=["Female", "Male"])
        category = st.selectbox("Category", options=["Clothing", "Food", "Electronics", "Books", "Shoes", "Home"])
        price = st.number_input("Price (USD)", min_value=0.01, value=150.00, format="%.2f")
        invoice_date = st.date_input("Invoice Date", value=datetime.today().date())
        shopping_mall = st.selectbox("Shopping Mall", options=["Kanyon", "Mall of Istanbul", "Metrocity", "Forum Istanbul"])

    # Submit button for the form
    submitted = st.form_submit_button("Commit New Record to Databricks")

    if submitted:
        # Create a list of the data in the exact order of the SQL INSERT statement
        new_record = [
            invoice_no,
            customer_id,
            gender,
            age,
            category,
            quantity,
            price,
            payment_method,
            invoice_date.strftime('%Y-%m-%d'), # Format date for SQL
            shopping_mall
        ]
        
        # Display the data being sent (for debugging)
        st.write("--- Data to be committed ---")
        df_display = pd.DataFrame([new_record], columns=[
            'invoice_no', 'customer_id', 'gender', 'age', 'category', 
            'quantity', 'price', 'payment_method', 'invoice_date', 'shopping_mall'
        ])
        st.dataframe(df_display, use_container_width=True)
        st.write("----------------------------")

        # Call the ingestion function
        if append_data_to_databricks(new_record):
            st.balloons()
