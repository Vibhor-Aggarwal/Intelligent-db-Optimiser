"""
Model Deployment and Prediction Example

Demonstrates how to load the trained model and make predictions.
"""

import pickle
import numpy as np
from sql_analyzer import SQLAnalyzer


class ExecutionTimePredictor:
    """Load and use the trained execution time prediction model."""

    def __init__(self, model_path: str):
        """
        Load a trained model from disk.

        Args:
            model_path (str): Path to the saved model.pkl file
        """
        with open(model_path, 'rb') as f:
            data = pickle.load(f)

        self.model = data['model']
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
        self.model_type = data['model_type']
        self.analyzer = SQLAnalyzer()

    def predict(self, query: str, rows_scanned: float) -> float:
        """
        Predict execution time for a SQL query.

        Args:
            query (str): SQL query string
            rows_scanned (float): Number of rows scanned

        Returns:
            float: Predicted execution time in milliseconds
        """
        # Analyze query
        query_analysis = self.analyzer.analyze(query)

        # Build feature vector
        features = {
            'num_joins': query_analysis['num_joins'],
            'has_where_clause': int(query_analysis['has_where_clause']),
            'uses_select_star': int(query_analysis['uses_select_star']),
            'num_indexes': len(query_analysis['indexes_used']),
            'query_length': query_analysis['query_length'],
            'rows_scanned': rows_scanned,
        }

        # Convert to array and scale
        X = np.array([[features[name] for name in self.feature_names]])
        X_scaled = self.scaler.transform(X)

        # Predict and ensure non-negative
        prediction = self.model.predict(X_scaled)[0]
        return max(prediction, 0)

    def predict_batch(self, queries: list) -> list:
        """
        Predict execution times for multiple queries.

        Args:
            queries (list): List of tuples (query_string, rows_scanned)

        Returns:
            list: List of predicted execution times
        """
        predictions = []
        for query, rows_scanned in queries:
            pred_time = self.predict(query, rows_scanned)
            predictions.append({
                'query': query,
                'rows_scanned': rows_scanned,
                'predicted_execution_time_ms': pred_time
            })
        return predictions


def main():
    """Demonstrate model usage."""
    print("SQL Query Execution Time Predictor - Model Deployment\n")
    print("="*70)

    # Load model
    predictor = ExecutionTimePredictor('model.pkl')
    print(f"✓ Model loaded successfully")
    print(f"  Model Type: {predictor.model_type}")
    print(f"  Features: {', '.join(predictor.feature_names)}")

    # Example predictions
    print(f"\n{'='*70}")
    print("Example Predictions\n")

    test_queries = [
        ("SELECT id, name, email FROM users WHERE id = 42", 1),
        ("SELECT * FROM orders WHERE order_date > '2024-01-01'", 145000),
        ("SELECT COUNT(*) FROM transactions WHERE user_id = 5", 8500),
        ("SELECT * FROM products WHERE category = 'Electronics' ORDER BY price DESC", 85000),
        ("SELECT u.id, u.name, COUNT(o.id) FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id", 1250000),
        ("SELECT * FROM customers", 800000),
        ("SELECT * FROM audit_logs", 5000000),
    ]

    results = predictor.predict_batch(test_queries)

    for i, result in enumerate(results, 1):
        query = result['query']
        rows = result['rows_scanned']
        pred_time = result['predicted_execution_time_ms']

        # Categorize performance
        if pred_time < 100:
            category = "⚡ Fast"
        elif pred_time < 1000:
            category = "✓ Normal"
        elif pred_time < 10000:
            category = "⚠ Slow"
        else:
            category = "🔴 Very Slow"

        print(f"{i}. {category}")
        print(f"   Query: {query[:65]}{'...' if len(query) > 65 else ''}")
        print(f"   Rows Scanned: {rows:,}")
        print(f"   Predicted Time: {pred_time:,.2f} ms ({pred_time/1000:.2f} seconds)")
        print()


if __name__ == '__main__':
    main()
