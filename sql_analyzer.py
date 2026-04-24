"""
SQL Query Analyzer Module

Analyzes SQL query strings and extracts key features:
- Number of joins
- Presence of WHERE clause
- Use of SELECT *
- Use of indexes
"""

import re
from typing import Dict, Any


class SQLAnalyzer:
    """Analyzes SQL queries and extracts key features."""

    def __init__(self):
        """Initialize the SQL analyzer with regex patterns."""
        # Pattern for JOIN keywords (case-insensitive)
        self.join_pattern = re.compile(
            r'\b(INNER\s+JOIN|LEFT\s+JOIN|RIGHT\s+JOIN|FULL\s+JOIN|CROSS\s+JOIN|JOIN)\b',
            re.IGNORECASE
        )
        # Pattern for WHERE clause
        self.where_pattern = re.compile(r'\bWHERE\b', re.IGNORECASE)
        # Pattern for SELECT *
        self.select_star_pattern = re.compile(r'SELECT\s+\*', re.IGNORECASE)
        # Pattern for index mentions (common formats)
        self.index_pattern = re.compile(
            r'(?:USE\s+INDEX|USING\s+INDEX|INDEX\s+HINT|\.idx_|pk_)',
            re.IGNORECASE
        )

    def analyze(self, query: str) -> Dict[str, Any]:
        """
        Analyze a SQL query and extract features.

        Args:
            query (str): SQL query string to analyze

        Returns:
            Dict[str, Any]: Dictionary containing extracted features:
                - num_joins (int): Number of JOIN operations
                - has_where_clause (bool): Whether WHERE clause is present
                - uses_select_star (bool): Whether SELECT * is used
                - indexes_used (list): List of indexes mentioned in query
                - query_length (int): Length of the query
        """
        # Normalize query (remove extra whitespace)
        normalized_query = ' '.join(query.split())

        # Count JOIN operations
        num_joins = len(self.join_pattern.findall(normalized_query))

        # Check for WHERE clause
        has_where_clause = bool(self.where_pattern.search(normalized_query))

        # Check for SELECT *
        uses_select_star = bool(self.select_star_pattern.search(normalized_query))

        # Extract indexes mentioned
        indexes_used = self._extract_indexes(query)

        return {
            'num_joins': num_joins,
            'has_where_clause': has_where_clause,
            'uses_select_star': uses_select_star,
            'indexes_used': indexes_used,
            'query_length': len(normalized_query)
        }

    def _extract_indexes(self, query: str) -> list:
        """
        Extract index names from query string.

        Args:
            query (str): SQL query string

        Returns:
            list: List of index names found in the query
        """
        indexes = []

        # Pattern to find quoted or unquoted index names
        # Looks for patterns like: "table.idx_name" or "table.pk_id"
        index_name_pattern = re.compile(
            r'(?:["\'])?([a-zA-Z0-9_]+(?:\.(?:idx_|pk_)[a-zA-Z0-9_]+)*)(?:["\'])?',
            re.IGNORECASE
        )

        # Check if query contains index hints or mentions
        if re.search(r'(?:USE\s+INDEX|USING\s+INDEX|INDEX\s+HINT)', query, re.IGNORECASE):
            # Extract everything after the index hint
            match = re.search(
                r'(?:USE\s+INDEX|USING\s+INDEX|INDEX\s+HINT)\s*\(\s*([^)]+)\s*\)',
                query,
                re.IGNORECASE
            )
            if match:
                index_str = match.group(1)
                indexes = [idx.strip() for idx in index_str.split(',')]
        else:
            # Look for index-like patterns in the query
            # This matches patterns like "table.idx_column" or "pk_id"
            matches = re.findall(r'[a-zA-Z0-9_]+\.(?:idx_|pk_)[a-zA-Z0-9_]+', query)
            indexes = list(set(matches))  # Remove duplicates

        return indexes

    def analyze_csv_column(self, csv_file: str, query_column: str = 'query') -> list:
        """
        Analyze SQL queries from a CSV file.

        Args:
            csv_file (str): Path to CSV file containing queries
            query_column (str): Name of the column containing SQL queries

        Returns:
            list: List of analysis results for each query
        """
        import csv

        results = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    query = row.get(query_column, '')
                    if query:
                        analysis = self.analyze(query)
                        analysis['query'] = query
                        results.append(analysis)
        except FileNotFoundError:
            print(f"Error: File '{csv_file}' not found.")
        except KeyError:
            print(f"Error: Column '{query_column}' not found in CSV.")

        return results


def analyze_query(query: str) -> Dict[str, Any]:
    """
    Convenience function to analyze a single SQL query.

    Args:
        query (str): SQL query string to analyze

    Returns:
        Dict[str, Any]: Analysis results
    """
    analyzer = SQLAnalyzer()
    return analyzer.analyze(query)


if __name__ == '__main__':
    # Example usage
    analyzer = SQLAnalyzer()

    # Test queries
    test_queries = [
        "SELECT id, name FROM users WHERE id = 42",
        "SELECT * FROM orders WHERE order_date > '2024-01-01' AND order_date < '2024-12-31'",
        "SELECT u.id, u.name, COUNT(o.id) FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id, u.name",
        "SELECT * FROM customers",
        "SELECT p.id, p.name, c.category_name FROM products p INNER JOIN categories c ON p.category_id = c.id WHERE p.price > 100",
    ]

    print("SQL Query Analysis Results\n" + "="*60)
    for query in test_queries:
        result = analyzer.analyze(query)
        print(f"\nQuery: {query}")
        print(f"  Joins: {result['num_joins']}")
        print(f"  Has WHERE: {result['has_where_clause']}")
        print(f"  Uses SELECT *: {result['uses_select_star']}")
        print(f"  Indexes: {result['indexes_used']}")
        print(f"  Query Length: {result['query_length']}")
