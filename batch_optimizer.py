"""
Batch Query Optimization Analyzer

Analyzes all queries in a CSV file and generates optimization report.
"""

import csv
import json
from query_optimizer import QueryOptimizer


class BatchQueryAnalyzer:
    """Analyze multiple queries from CSV and generate reports."""

    def __init__(self, csv_file: str, query_column: str = 'query'):
        """
        Initialize the batch analyzer.

        Args:
            csv_file (str): Path to CSV file with query logs
            query_column (str): Name of the column containing queries
        """
        self.csv_file = csv_file
        self.query_column = query_column
        self.optimizer = QueryOptimizer()
        self.results = []

    def analyze_all(self) -> list:
        """
        Analyze all queries in the CSV file.

        Returns:
            list: List of analysis results
        """
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, 1):
                    query = row.get(self.query_column, '')
                    if query:
                        summary = self.optimizer.get_optimization_summary(query)
                        summary['row_number'] = i
                        self.results.append(summary)
        except FileNotFoundError:
            print(f"Error: File '{self.csv_file}' not found.")
            return []

        return self.results

    def get_high_priority_queries(self, min_recommendations: int = 2) -> list:
        """
        Get queries with the most optimization opportunities.

        Args:
            min_recommendations (int): Minimum number of recommendations to include

        Returns:
            list: Sorted list of high-priority queries
        """
        high_priority = [
            r for r in self.results
            if r['optimization_priority'] >= min_recommendations
        ]
        return sorted(high_priority, key=lambda x: x['optimization_priority'], reverse=True)

    def print_summary(self) -> None:
        """Print a summary of analysis results."""
        if not self.results:
            print("No results to display.")
            return

        print(f"\n{'='*80}")
        print(f"Query Optimization Analysis Summary")
        print(f"{'='*80}\n")

        print(f"Total Queries Analyzed: {len(self.results)}")

        # Count by optimization priority
        priority_counts = {}
        for result in self.results:
            priority = result['optimization_priority']
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        print(f"\nQueries by Optimization Priority:")
        for priority in sorted(priority_counts.keys(), reverse=True):
            count = priority_counts[priority]
            print(f"  {priority} recommendations: {count} query(ies)")

        # Show top optimization opportunities
        high_priority = self.get_high_priority_queries(min_recommendations=2)
        if high_priority:
            print(f"\n{'='*80}")
            print(f"Top Optimization Opportunities ({len(high_priority)} queries)")
            print(f"{'='*80}\n")

            for i, result in enumerate(high_priority[:5], 1):  # Show top 5
                query = result['query']
                recs = result['recommendations']
                print(f"{i}. Row #{result['row_number']}")
                print(f"   Query: {query[:75]}{'...' if len(query) > 75 else ''}")
                print(f"   Recommendations: {len(recs)}")
                for rec in recs[:2]:  # Show first 2 recommendations
                    print(f"     • {rec[:90]}...")
                print()

    def export_report(self, output_file: str = 'optimization_report.json') -> None:
        """
        Export analysis results to JSON file.

        Args:
            output_file (str): Path to output JSON file
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"Report exported to {output_file}")

    def print_detailed_report(self, max_queries: int = None) -> None:
        """
        Print a detailed report for each query.

        Args:
            max_queries (int): Maximum number of queries to print (None for all)
        """
        results_to_show = self.results if max_queries is None else self.results[:max_queries]

        print(f"\n{'='*80}")
        print(f"Detailed Query Optimization Report")
        print(f"{'='*80}\n")

        for i, result in enumerate(results_to_show, 1):
            query = result['query']
            analysis = result['analysis']
            recs = result['recommendations']

            print(f"{i}. Query (Row #{result['row_number']})")
            print(f"   {query}")
            print(f"\n   Analysis:")
            print(f"     • JOINs: {analysis['num_joins']}")
            print(f"     • WHERE Clause: {analysis['has_where_clause']}")
            print(f"     • SELECT *: {analysis['uses_select_star']}")
            print(f"     • Tables: {', '.join(result['tables'])}")

            if recs:
                print(f"\n   Recommendations ({len(recs)}):")
                for rec in recs:
                    print(f"     • {rec}")
            else:
                print(f"\n   ✓ No optimization recommendations.")

            print()


def main():
    """Main function for batch analysis."""
    print("Batch Query Optimization Analyzer\n")

    # Analyze queries
    analyzer = BatchQueryAnalyzer('sql_query_logs.csv')
    results = analyzer.analyze_all()

    if results:
        # Print summary
        analyzer.print_summary()

        # Export detailed report
        analyzer.export_report('optimization_report.json')
        print(f"\n✓ Detailed report saved to optimization_report.json")

        # Print detailed report for queries with 3+ recommendations
        high_priority = analyzer.get_high_priority_queries(min_recommendations=3)
        if high_priority:
            print(f"\n{'='*80}")
            print(f"Top Queries Needing Optimization ({len(high_priority)} queries with 3+ recommendations)")
            print(f"{'='*80}\n")

            for i, result in enumerate(high_priority, 1):
                query = result['query']
                recs = result['recommendations']
                print(f"{i}. Query: {query[:70]}...")
                print(f"   Priority Level: {len(recs)} recommendations")
                print(f"   Key Issues:")
                for rec in recs[:3]:
                    # Extract emoji and first part of recommendation
                    parts = rec.split('.')
                    print(f"     {parts[0]}.")
                print()


if __name__ == '__main__':
    main()
