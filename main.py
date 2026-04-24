"""
SQL Query Analyzer and Performance Predictor

Main script that analyzes SQL queries and provides:
1. Query analysis (JOINs, WHERE clause, SELECT *, indexes)
2. Execution time prediction using trained ML model
3. Optimization recommendations
"""

import sys
import argparse
from predict import ExecutionTimePredictor
from query_optimizer import QueryOptimizer
from sql_analyzer import SQLAnalyzer


class QueryAnalysisReport:
    """Generate comprehensive query analysis and prediction reports."""

    def __init__(self, model_path: str = 'model.pkl'):
        """
        Initialize the report generator.

        Args:
            model_path (str): Path to the trained model.pkl file
        """
        self.predictor = ExecutionTimePredictor(model_path)
        self.optimizer = QueryOptimizer()
        self.analyzer = SQLAnalyzer()

    def analyze_and_predict(self, query: str, rows_scanned: float) -> dict:
        """
        Analyze a query and predict execution time with recommendations.

        Args:
            query (str): SQL query string
            rows_scanned (float): Estimated number of rows to be scanned

        Returns:
            dict: Comprehensive analysis report
        """
        # Analyze query
        analysis = self.analyzer.analyze(query)

        # Predict execution time
        predicted_time = self.predictor.predict(query, rows_scanned)

        # Get optimization suggestions
        recommendations = self.optimizer.suggest_optimizations(query)

        # Determine performance category
        performance_category = self._categorize_performance(predicted_time)

        # Build report
        report = {
            'query': query,
            'rows_scanned': rows_scanned,
            'analysis': analysis,
            'prediction': {
                'execution_time_ms': predicted_time,
                'execution_time_seconds': predicted_time / 1000,
                'performance_category': performance_category,
                'confidence': 'High (R² = 0.8722)' if rows_scanned > 100 else 'Moderate'
            },
            'recommendations': recommendations,
            'summary': self._generate_summary(
                analysis,
                predicted_time,
                recommendations
            )
        }

        return report

    def _categorize_performance(self, execution_time_ms: float) -> str:
        """
        Categorize query performance based on execution time.

        Args:
            execution_time_ms (float): Execution time in milliseconds

        Returns:
            str: Performance category
        """
        if execution_time_ms < 100:
            return "⚡ Excellent (< 100ms)"
        elif execution_time_ms < 1000:
            return "✓ Good (100ms - 1s)"
        elif execution_time_ms < 5000:
            return "⚠️  Fair (1s - 5s)"
        elif execution_time_ms < 30000:
            return "🔴 Poor (5s - 30s)"
        else:
            return "❌ Critical (> 30s)"

    def _generate_summary(self, analysis: dict, predicted_time: float, recommendations: list) -> str:
        """
        Generate a concise summary of the analysis.

        Args:
            analysis (dict): Query analysis
            predicted_time (float): Predicted execution time
            recommendations (list): Optimization recommendations

        Returns:
            str: Summary text
        """
        summary_parts = []

        # Performance summary
        if predicted_time < 1000:
            summary_parts.append("Query is expected to perform well")
        elif predicted_time < 10000:
            summary_parts.append("Query performance is acceptable but could be optimized")
        else:
            summary_parts.append("Query is expected to be slow and needs optimization")

        # Complexity summary
        if analysis['num_joins'] == 0:
            summary_parts.append("Simple query with no JOINs")
        elif analysis['num_joins'] <= 2:
            summary_parts.append(f"Moderate complexity with {analysis['num_joins']} JOINs")
        else:
            summary_parts.append(f"Complex query with {analysis['num_joins']} JOINs")

        # Optimization summary
        if len(recommendations) == 0:
            summary_parts.append("No optimization recommendations")
        elif len(recommendations) <= 2:
            summary_parts.append(f"{len(recommendations)} optimization opportunity")
        else:
            summary_parts.append(f"{len(recommendations)} optimization opportunities")

        return ". ".join(summary_parts) + "."

    def print_report(self, report: dict, verbose: bool = True) -> None:
        """
        Print a formatted analysis report.

        Args:
            report (dict): Analysis report from analyze_and_predict
            verbose (bool): Print detailed recommendations
        """
        query = report['query']
        rows = report['rows_scanned']
        analysis = report['analysis']
        prediction = report['prediction']
        recommendations = report['recommendations']

        print("\n" + "="*80)
        print("SQL QUERY ANALYSIS AND PERFORMANCE PREDICTION")
        print("="*80 + "\n")

        # Query section
        print("📋 QUERY:")
        print("-" * 80)
        if len(query) > 100:
            print(query[:100] + "...")
            print(query[100:])
        else:
            print(query)

        # Analysis section
        print("\n📊 QUERY ANALYSIS:")
        print("-" * 80)
        print(f"  JOINs:                    {analysis['num_joins']}")
        print(f"  Has WHERE Clause:         {analysis['has_where_clause']}")
        print(f"  Uses SELECT *:            {analysis['uses_select_star']}")
        print(f"  Indexes Used:             {len(analysis['indexes_used'])} " +
              (f"({', '.join(analysis['indexes_used'][:3])}{'...' if len(analysis['indexes_used']) > 3 else ''})" 
               if analysis['indexes_used'] else "(None mentioned)"))
        print(f"  Query Length:             {analysis['query_length']} characters")
        print(f"  Estimated Rows Scanned:   {rows:,.0f}")

        # Prediction section
        print("\n⏱️  PERFORMANCE PREDICTION:")
        print("-" * 80)
        print(f"  {prediction['performance_category']}")
        print(f"  Predicted Execution Time: {prediction['execution_time_ms']:,.2f} ms " +
              f"({prediction['execution_time_seconds']:.2f} seconds)")
        print(f"  Model Confidence:         {prediction['confidence']}")

        # Summary section
        print("\n📈 SUMMARY:")
        print("-" * 80)
        print(f"  {report['summary']}")

        # Recommendations section
        if recommendations:
            print("\n💡 OPTIMIZATION RECOMMENDATIONS:")
            print("-" * 80)
            print(f"  Found {len(recommendations)} optimization opportunit{'ies' if len(recommendations) != 1 else 'y'}:\n")

            if verbose:
                for i, rec in enumerate(recommendations, 1):
                    # Wrap text at 78 chars
                    wrapped = self._wrap_text(rec, width=75)
                    print(f"  {i}. {wrapped}")
                    print()
            else:
                # Show condensed version (first part of each recommendation)
                for i, rec in enumerate(recommendations[:5], 1):
                    first_part = rec.split('.')[0] + '.'
                    print(f"  {i}. {first_part}")

                if len(recommendations) > 5:
                    print(f"  ... and {len(recommendations) - 5} more recommendations")
        else:
            print("\n✓ No optimization recommendations for this query.")

        print("\n" + "="*80 + "\n")

    @staticmethod
    def _wrap_text(text: str, width: int = 75) -> str:
        """
        Wrap text to specified width.

        Args:
            text (str): Text to wrap
            width (int): Maximum line width

        Returns:
            str: Wrapped text
        """
        lines = []
        current_line = ""

        for word in text.split():
            if len(current_line) + len(word) + 1 <= width:
                current_line += " " + word if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return "\n  ".join(lines)


def get_user_input() -> tuple:
    """
    Interactively get SQL query and rows scanned from user.

    Returns:
        tuple: (query, rows_scanned)
    """
    print("\n" + "="*80)
    print("SQL QUERY ANALYZER - Interactive Mode")
    print("="*80 + "\n")

    # Get query
    print("Enter your SQL query (press Enter twice when done):")
    print("-" * 80)
    lines = []
    while True:
        line = input()
        if line == "":
            if lines:
                break
            else:
                print("Please enter a query.")
                continue
        lines.append(line)

    query = " ".join(lines)

    # Get rows scanned
    print("\nEstimated rows that will be scanned by this query:")
    while True:
        try:
            rows_scanned = float(input("Rows scanned: "))
            if rows_scanned < 0:
                print("Rows scanned must be non-negative.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")

    return query, rows_scanned


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Analyze SQL queries and predict execution time with optimization suggestions'
    )
    parser.add_argument(
        'query',
        nargs='?',
        help='SQL query to analyze (if not provided, interactive mode is used)'
    )
    parser.add_argument(
        '-r', '--rows',
        type=float,
        default=1000,
        help='Estimated rows scanned by the query (default: 1000)'
    )
    parser.add_argument(
        '-m', '--model',
        default='model.pkl',
        help='Path to trained model file (default: model.pkl)'
    )
    parser.add_argument(
        '-c', '--condensed',
        action='store_true',
        help='Print condensed output (less detail on recommendations)'
    )

    args = parser.parse_args()

    # Get query and rows
    if args.query:
        query = args.query
        rows_scanned = args.rows
    else:
        query, rows_scanned = get_user_input()

    # Initialize report generator
    try:
        report_gen = QueryAnalysisReport(args.model)
    except FileNotFoundError:
        print(f"\nError: Model file '{args.model}' not found.")
        print("Please ensure the model has been trained by running: python train_model.py")
        sys.exit(1)

    # Generate report
    report = report_gen.analyze_and_predict(query, rows_scanned)

    # Print report
    report_gen.print_report(report, verbose=not args.condensed)


if __name__ == '__main__':
    main()
