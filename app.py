"""
Web UI for AI Database Query Optimizer using Streamlit
"""

import streamlit as st
import pandas as pd
from main import QueryAnalysisReport

# --- Page Configuration ---
st.set_page_config(
    page_title="AI DB Optimizer",
    page_icon="🧠",
    layout="wide"
)

# --- Load the Backend Model ---
@st.cache_resource
def load_analyzer():
    """Cache the model loading so it doesn't reload on every button click"""
    try:
        return QueryAnalysisReport('model.pkl')
    except FileNotFoundError:
        return None

analyzer = load_analyzer()

# --- UI Header ---
st.title("🧠 AI-Based Database Query Optimizer")
st.markdown("""
Paste your SQL query below to get AI-driven performance predictions and actionable optimization recommendations.
""")

# Check if model exists
if analyzer is None:
    st.error("⚠️ Model file 'model.pkl' not found. Please run `python train_model.py` in your terminal first.")
    st.stop()

# --- Input Section ---
col1, col2 = st.columns([2, 1])

with col1:
    query = st.text_area(
        "SQL Query", 
        height=200, 
        placeholder="SELECT * FROM orders WHERE status = 'pending'..."
    )

with col2:
    st.markdown("### Parameters")
    rows_scanned = st.number_input(
        "Estimated Rows Scanned", 
        min_value=1, 
        value=10000,
        step=1000,
        help="The estimated number of rows the database engine will need to scan."
    )
    
    analyze_button = st.button("🚀 Analyze Query", use_container_width=True, type="primary")

# --- Results Section ---
if analyze_button and query:
    with st.spinner("Analyzing query and running ML prediction..."):
        # Run the backend logic
        report = analyzer.analyze_and_predict(query, float(rows_scanned))
        
        st.divider()
        
        # 1. Top Level Summary & Prediction
        st.subheader("⏱️ Performance Prediction")
        
        pred = report['prediction']
        
        # Color code the metric based on performance
        color = "normal"
        if pred['execution_time_ms'] > 5000:
            color = "inverse"
            
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Predicted Time", f"{pred['execution_time_ms']:,.2f} ms", delta_color=color)
        metric_col2.metric("Category", pred['performance_category'])
        metric_col3.metric("Model Confidence", pred['confidence'])
        
        st.info(f"**Summary:** {report['summary']}")

        st.divider()

        # 2. Recommendations & Analysis Details
        detail_col1, detail_col2 = st.columns(2)
        
        with detail_col1:
            st.subheader("💡 Optimization Recommendations")
            recs = report['recommendations']
            
            if recs:
                for idx, rec in enumerate(recs, 1):
                    st.warning(f"{idx}. {rec}")
            else:
                st.success("✓ Query looks optimal! No recommendations found.")
                
        with detail_col2:
            st.subheader("📊 Query Analysis Features")
            analysis = report['analysis']
            
            # Display features nicely in a table
            features_df = pd.DataFrame([
                {"Feature": "JOINs count", "Value": str(analysis['num_joins'])},
                {"Feature": "Has WHERE clause", "Value": str(analysis['has_where_clause'])},
                {"Feature": "Uses SELECT *", "Value": "Yes ⚠️" if analysis['uses_select_star'] else "No"},
                {"Feature": "Query Length", "Value": f"{analysis['query_length']} chars"},
                {"Feature": "Indexes Mentioned", "Value": ", ".join(analysis['indexes_used']) if analysis['indexes_used'] else "None"}
            ])
            
            st.dataframe(features_df, hide_index=True, use_container_width=True)