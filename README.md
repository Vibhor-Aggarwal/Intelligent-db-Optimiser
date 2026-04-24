# AI-Based Intelligent Database Query Optimization System

An end-to-end Python toolkit that analyzes SQL queries, predicts execution times using Machine Learning, and provides actionable, rule-based optimization recommendations.

## 🚀 Features
* **ML Performance Prediction:** Uses a Random Forest Regressor to predict query execution time in milliseconds based on query complexity and rows scanned.
* **Intelligent Optimization:** Rule engine that detects missing indexes, excessive JOINs, `SELECT *` inefficiencies, and sub-optimal aggregations.
* **Batch Processing:** Automatically analyze hundreds of queries from a CSV log file overnight.
* **Interactive CLI:** Paste a query directly into the terminal to get instant feedback.

## 💻 Quick Start

**1. Install Dependencies**
\`\`\`bash
pip install scikit-learn numpy pandas
\`\`\`

**2. Train the Model** (Required first step to generate `model.pkl`)
\`\`\`bash
python train_model.py
\`\`\`

**3. Run the Analyzer** (Interactive mode)
\`\`\`bash
python main.py
\`\`\`

## 🛠️ Usage Examples

**Analyze a specific query via CLI:**
\`\`\`bash
python main.py "SELECT * FROM orders WHERE status = 'pending'" -r 50000
\`\`\`

**Run a batch analysis on a log file:**
\`\`\`bash
python batch_optimizer.py
\`\`\`
*(Generates a detailed `optimization_report.json`)*

## 🧠 Under the Hood: The ML Model

The predictive engine uses a **Random Forest Regressor** trained on historical query performance data.

* **Performance:** Test R² Score: `0.8722` (87% variance explained)
* **Features Extracted:**
  * `rows_scanned` (Highest importance - 63%)
  * `num_joins`
  * `has_where_clause`
  * `uses_select_star`
  * `num_indexes`
  * `query_length`

## 📂 Project Structure

* `main.py`: Interactive CLI and entry point.
* `train_model.py`: ML pipeline for training the execution time predictor.
* `predict.py`: Model deployment script.
* `sql_analyzer.py`: Regex-based feature extraction from raw SQL text.
* `query_optimizer.py`: The rule-based recommendation engine.
* `batch_optimizer.py`: Processes bulk queries from CSV files.