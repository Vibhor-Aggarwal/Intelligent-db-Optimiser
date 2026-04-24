"""
SQL Query Execution Time Prediction Model

Trains a machine learning model to predict SQL query execution time
based on features extracted from the query and metadata.
"""

import csv
import pickle
import numpy as np
from sql_analyzer import SQLAnalyzer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error


class QueryExecutionTimePredictor:
    """Train and manage a model for predicting SQL query execution times."""

    def __init__(self, model_type='random_forest'):
        """
        Initialize the predictor with a model.

        Args:
            model_type (str): Type of model - 'random_forest' or 'linear'
        """
        self.analyzer = SQLAnalyzer()
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.model_type = model_type

    def load_csv_data(self, csv_file: str) -> tuple:
        """
        Load data from CSV and extract features.

        Args:
            csv_file (str): Path to CSV file with query logs

        Returns:
            tuple: (features_list, target_list, raw_data_list)
        """
        features_list = []
        target_list = []
        raw_data = []

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    query = row.get('query', '')
                    execution_time = float(row.get('execution_time', 0))
                    rows_scanned = float(row.get('rows_scanned', 0))

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

                    features_list.append(features)
                    target_list.append(execution_time)
                    raw_data.append({
                        'query': query,
                        'execution_time': execution_time,
                        'features': features
                    })

        except FileNotFoundError:
            print(f"Error: File '{csv_file}' not found.")
            return None, None, None

        return features_list, target_list, raw_data

    def prepare_data(self, features_list: list) -> np.ndarray:
        """
        Convert feature dictionaries to numpy array.

        Args:
            features_list (list): List of feature dictionaries

        Returns:
            np.ndarray: Feature matrix
        """
        # Define consistent feature order
        self.feature_names = [
            'num_joins',
            'has_where_clause',
            'uses_select_star',
            'num_indexes',
            'query_length',
            'rows_scanned'
        ]

        X = np.array([[f[name] for name in self.feature_names] for f in features_list])
        return X

    def train(self, csv_file: str, test_size: float = 0.2, random_state: int = 42) -> dict:
        """
        Train the model on the dataset.

        Args:
            csv_file (str): Path to CSV file with query logs
            test_size (float): Proportion of data to use for testing
            random_state (int): Random seed for reproducibility

        Returns:
            dict: Training statistics and metrics
        """
        print(f"Loading data from {csv_file}...")
        features_list, target_list, raw_data = self.load_csv_data(csv_file)

        if features_list is None:
            return None

        print(f"Loaded {len(features_list)} queries")

        # Prepare data
        X = self.prepare_data(features_list)
        y = np.array(target_list)

        print(f"\nFeatures: {self.feature_names}")
        print(f"Feature matrix shape: {X.shape}")
        print(f"Target shape: {y.shape}")

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        print(f"\nTrain set size: {len(X_train)}, Test set size: {len(X_test)}")

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        if self.model_type == 'random_forest':
            print(f"\nTraining RandomForestRegressor...")
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=random_state,
                n_jobs=-1
            )
        else:
            print(f"\nTraining LinearRegression...")
            self.model = LinearRegression()

        self.model.fit(X_train_scaled, y_train)

        # Evaluate
        y_train_pred = self.model.predict(X_train_scaled)
        y_test_pred = self.model.predict(X_test_scaled)

        train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)

        stats = {
            'model_type': self.model_type,
            'train_rmse': train_rmse,
            'test_rmse': test_rmse,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'train_mae': train_mae,
            'test_mae': test_mae,
            'num_samples': len(features_list),
            'num_features': len(self.feature_names)
        }

        print(f"\n{'='*60}")
        print(f"Training Results ({self.model_type})")
        print(f"{'='*60}")
        print(f"Training RMSE:   {train_rmse:.2f}")
        print(f"Testing RMSE:    {test_rmse:.2f}")
        print(f"Training R²:     {train_r2:.4f}")
        print(f"Testing R²:      {test_r2:.4f}")
        print(f"Training MAE:    {train_mae:.2f}")
        print(f"Testing MAE:     {test_mae:.2f}")

        # Feature importance for RandomForest
        if self.model_type == 'random_forest':
            print(f"\n{'Feature Importance'}")
            print(f"{'-'*40}")
            for name, importance in zip(self.feature_names, self.model.feature_importances_):
                print(f"  {name:20s}: {importance:.4f}")

        return stats

    def save_model(self, filepath: str) -> None:
        """
        Save the trained model and scaler to disk.

        Args:
            filepath (str): Path to save the model
        """
        if self.model is None:
            print("Error: No model has been trained yet.")
            return

        data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'model_type': self.model_type
        }

        with open(filepath, 'wb') as f:
            pickle.dump(data, f)

        print(f"\nModel saved to {filepath}")

    def load_model(self, filepath: str) -> None:
        """
        Load a trained model from disk.

        Args:
            filepath (str): Path to the saved model
        """
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)

            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_names = data['feature_names']
            self.model_type = data['model_type']
            print(f"Model loaded from {filepath}")
        except FileNotFoundError:
            print(f"Error: File '{filepath}' not found.")

    def predict(self, query: str, rows_scanned: float) -> float:
        """
        Predict execution time for a query.

        Args:
            query (str): SQL query string
            rows_scanned (float): Number of rows scanned

        Returns:
            float: Predicted execution time in milliseconds
        """
        if self.model is None:
            print("Error: No model loaded. Train or load a model first.")
            return None

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

        # Convert to array
        X = np.array([[features[name] for name in self.feature_names]])

        # Scale and predict
        X_scaled = self.scaler.transform(X)
        prediction = self.model.predict(X_scaled)[0]

        return max(prediction, 0)  # Ensure non-negative prediction


def main():
    """Main function for training and saving the model."""
    print("SQL Query Execution Time Predictor\n")

    # Create predictor
    predictor = QueryExecutionTimePredictor(model_type='random_forest')

    # Train model
    stats = predictor.train('sql_query_logs.csv', test_size=0.2)

    if stats:
        # Save model
        predictor.save_model('model.pkl')

        # Test predictions on a few queries
        print(f"\n{'='*60}")
        print("Sample Predictions")
        print(f"{'='*60}")

        test_queries = [
            ("SELECT id, name FROM users WHERE id = 42", 100),
            ("SELECT * FROM orders", 500000),
            ("SELECT u.id, u.name FROM users u LEFT JOIN orders o ON u.id = o.user_id", 150000),
        ]

        for query, rows in test_queries:
            pred_time = predictor.predict(query, rows)
            print(f"\nQuery: {query[:60]}...")
            print(f"  Rows Scanned: {rows}")
            print(f"  Predicted Execution Time: {pred_time:.2f} ms")


if __name__ == '__main__':
    main()
