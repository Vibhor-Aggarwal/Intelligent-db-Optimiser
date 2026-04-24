"""
SQL Query Optimization Suggester

Analyzes SQL queries and provides optimization recommendations for:
- SELECT * usage
- Index suggestions
- JOIN optimization
- Query structure improvements
"""

import re
from typing import List, Dict, Any
from sql_analyzer import SQLAnalyzer


class QueryOptimizer:
    """Analyzes SQL queries and suggests optimizations."""

    def __init__(self):
        """Initialize the optimizer with the SQL analyzer."""
        self.analyzer = SQLAnalyzer()
        self.recommendations = []

    def suggest_optimizations(self, query: str) -> List[str]:
        """
        Analyze a query and return optimization recommendations.

        Args:
            query (str): SQL query string to analyze

        Returns:
            List[str]: List of optimization recommendations
        """
        self.recommendations = []

        # Get query analysis
        analysis = self.analyzer.analyze(query)

        # Check for SELECT * usage
        self._check_select_star(query)

        # Check WHERE clause and suggest indexes
        self._check_where_clause_indexes(query)

        # Check for excessive JOINs
        self._check_joins(analysis, query)

        # Check for other common issues
        self._check_subqueries(query)
        self._check_like_patterns(query)
        self._check_order_by(query)
        self._check_aggregation(query)

        return self.recommendations

    def _check_select_star(self, query: str) -> None:
        """
        Check for SELECT * and recommend specific columns.

        Args:
            query (str): SQL query string
        """
        if re.search(r'SELECT\s+\*', query, re.IGNORECASE):
            # Extract table names to provide specific suggestion
            tables = self._extract_tables(query)
            table_str = ', '.join(tables) if tables else 'your tables'

            self.recommendations.append(
                f"⚠️  Replace 'SELECT *' with specific columns from {table_str} "
                f"to reduce network traffic and improve query performance. "
                f"Example: SELECT id, name, email FROM {table_str.split(', ')[0]}"
            )

    def _check_where_clause_indexes(self, query: str) -> None:
        """
        Check WHERE clause and suggest indexes on filter columns.

        Args:
            query (str): SQL query string
        """
        # Extract WHERE clause
        where_match = re.search(r'WHERE\s+([^;]+?)(?:GROUP BY|ORDER BY|LIMIT|$)', query, re.IGNORECASE)

        if where_match:
            where_clause = where_match.group(1)

            # Extract column names used in WHERE (simple patterns)
            # Look for patterns like: column = value, column > value, column LIKE value
            columns = re.findall(
                r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:=|!=|<>|<|>|<=|>=|LIKE|IN|BETWEEN)',
                where_clause,
                re.IGNORECASE
            )

            if columns:
                unique_columns = list(set(columns))
                cols_str = ', '.join(unique_columns[:3])  # Limit to 3 for readability

                if len(unique_columns) > 3:
                    cols_str += ', ...'

                self.recommendations.append(
                    f"📊 Create indexes on WHERE clause columns: {cols_str}. "
                    f"Indexes on these columns will significantly speed up filtering: "
                    f"e.g., CREATE INDEX idx_{unique_columns[0]} ON table_name({unique_columns[0]})"
                )

            # Check for missing indexes in query
            if not re.search(r'(?:USE\s+INDEX|USING\s+INDEX|\.idx_|pk_)', query, re.IGNORECASE):
                self.recommendations.append(
                    f"🔍 No indexes are currently being used in this query. "
                    f"Ensure indexes exist on filtered columns and verify the query optimizer is using them."
                )

    def _check_joins(self, analysis: Dict[str, Any], query: str) -> None:
        """
        Check for excessive JOINs and suggest optimization.

        Args:
            analysis (Dict): Query analysis from SQLAnalyzer
            query (str): SQL query string
        """
        num_joins = analysis['num_joins']

        if num_joins >= 4:
            self.recommendations.append(
                f"⛓️  Query has {num_joins} JOINs. Consider breaking this into multiple smaller queries "
                f"or using materialized views to improve readability and potentially performance. "
                f"Deep JOIN chains can lead to inefficient execution plans."
            )
        elif num_joins >= 2:
            self.recommendations.append(
                f"⛓️  Query has {num_joins} JOINs. Verify that all JOINs are necessary and that "
                f"join conditions use indexed columns. Consider if some JOINs could be replaced "
                f"with application-level lookups if the secondary tables are small."
            )

        # Check for missing join conditions
        if num_joins > 0:
            self._check_join_conditions(query)

    def _check_join_conditions(self, query: str) -> None:
        """
        Check if JOIN conditions are on indexed columns.

        Args:
            query (str): SQL query string
        """
        # Extract join conditions
        join_conditions = re.findall(
            r'(?:INNER|LEFT|RIGHT|FULL|CROSS)?\s+JOIN\s+[a-zA-Z0-9_]+\s+[a-zA-Z0-9_]*\s+ON\s+([^)]+)',
            query,
            re.IGNORECASE
        )

        if join_conditions:
            conditions_str = '; '.join(join_conditions[:2])
            if len(join_conditions) > 2:
                conditions_str += '; ...'

            self.recommendations.append(
                f"🔑 JOIN conditions found: {conditions_str}. "
                f"Ensure both sides of JOIN conditions have indexes for optimal performance."
            )

    def _check_subqueries(self, query: str) -> None:
        """
        Check for potentially inefficient subqueries.

        Args:
            query (str): SQL query string
        """
        # Look for nested subqueries
        subquery_count = len(re.findall(r'SELECT\s+', query, re.IGNORECASE)) - 1

        if subquery_count > 0:
            self.recommendations.append(
                f"🔄 Query contains {subquery_count} subquery(ies). Consider using JOINs or CTEs (Common Table Expressions) "
                f"instead of subqueries for better performance. Example: WITH cte AS (SELECT ...) SELECT ... FROM cte"
            )

        # Check for correlated subqueries
        if re.search(r'WHERE\s+.*\(SELECT.*WHERE.*\)', query, re.IGNORECASE | re.DOTALL):
            self.recommendations.append(
                f"⚡ This query may contain a correlated subquery, which can be very slow. "
                f"Consider rewriting with JOINs or window functions for better performance."
            )

    def _check_like_patterns(self, query: str) -> None:
        """
        Check for LIKE patterns that prevent index usage.

        Args:
            query (str): SQL query string
        """
        # Check for leading wildcards in LIKE
        if re.search(r"LIKE\s+'%[^']+", query, re.IGNORECASE):
            self.recommendations.append(
                f"🔎 Query uses LIKE pattern with leading wildcard (e.g., LIKE '%term'). "
                f"This prevents index usage. Consider full-text search or restructuring the query. "
                f"If possible, use LIKE 'term%' to allow index usage."
            )

    def _check_order_by(self, query: str) -> None:
        """
        Check for ORDER BY without LIMIT and sorting opportunities.

        Args:
            query (str): SQL query string
        """
        has_order_by = re.search(r'ORDER\s+BY', query, re.IGNORECASE)
        has_limit = re.search(r'LIMIT\s+\d+', query, re.IGNORECASE)

        if has_order_by and not has_limit:
            # Extract ORDER BY columns
            order_match = re.search(r'ORDER\s+BY\s+([^;]+?)(?:LIMIT|$)', query, re.IGNORECASE)
            if order_match:
                order_cols = order_match.group(1).strip()
                self.recommendations.append(
                    f"📈 Query uses ORDER BY ({order_cols}) without LIMIT. "
                    f"If you don't need all rows, consider adding LIMIT to reduce execution time. "
                    f"Create an index on ORDER BY columns if sorting large datasets."
                )

        if has_order_by:
            # Extract columns from ORDER BY
            order_match = re.search(r'ORDER\s+BY\s+([^;]+?)(?:LIMIT|$)', query, re.IGNORECASE)
            if order_match:
                order_cols = order_match.group(1).strip()
                cols = [c.split()[0] for c in order_cols.split(',')]
                cols_str = ', '.join(cols[:2])

                self.recommendations.append(
                    f"📊 Create an index on ORDER BY columns ({cols_str}) "
                    f"to avoid expensive sorting operations."
                )

    def _check_aggregation(self, query: str) -> None:
        """
        Check for aggregation functions and GROUP BY optimization.

        Args:
            query (str): SQL query string
        """
        has_group_by = re.search(r'GROUP\s+BY', query, re.IGNORECASE)
        has_agg = re.search(r'(?:COUNT|SUM|AVG|MAX|MIN|GROUP_CONCAT)\s*\(', query, re.IGNORECASE)

        if has_group_by and has_agg:
            # Extract GROUP BY columns
            group_match = re.search(r'GROUP\s+BY\s+([^;]+?)(?:HAVING|ORDER|LIMIT|$)', query, re.IGNORECASE)
            if group_match:
                group_cols = group_match.group(1).strip()
                cols = [c.split()[0] for c in group_cols.split(',')]
                cols_str = ', '.join(cols[:2])

                self.recommendations.append(
                    f"📊 Create a composite index on GROUP BY columns ({cols_str}) "
                    f"to optimize aggregation queries. This can significantly reduce execution time."
                )

    def _extract_tables(self, query: str) -> List[str]:
        """
        Extract table names from a query.

        Args:
            query (str): SQL query string

        Returns:
            List[str]: List of table names
        """
        # Simple pattern matching for FROM and JOIN clauses
        # Matches: FROM table_name, JOIN table_name, etc.
        pattern = r'(?:FROM|JOIN)\s+([a-zA-Z0-9_]+)'
        matches = re.findall(pattern, query, re.IGNORECASE)
        return matches

    def get_optimization_summary(self, query: str) -> Dict[str, Any]:
        """
        Get a comprehensive optimization report for a query.

        Args:
            query (str): SQL query string

        Returns:
            Dict[str, Any]: Summary including analysis and recommendations
        """
        analysis = self.analyzer.analyze(query)
        recommendations = self.suggest_optimizations(query)

        return {
            'query': query,
            'analysis': {
                'num_joins': analysis['num_joins'],
                'has_where_clause': analysis['has_where_clause'],
                'uses_select_star': analysis['uses_select_star'],
                'indexes_used': analysis['indexes_used'],
                'query_length': analysis['query_length']
            },
            'recommendations': recommendations,
            'optimization_priority': len(recommendations),
            'tables': self._extract_tables(query)
        }


def optimize_query(query: str) -> List[str]:
    """
    Convenience function to get optimization recommendations for a query.

    Args:
        query (str): SQL query string

    Returns:
        List[str]: List of optimization recommendations
    """
    optimizer = QueryOptimizer()
    return optimizer.suggest_optimizations(query)


if __name__ == '__main__':
    # Example usage
    optimizer = QueryOptimizer()

    # Test queries with various issues
    test_queries = [
        "SELECT * FROM orders WHERE order_date > '2024-01-01'",
        "SELECT * FROM customers",
        "SELECT u.id, u.name FROM users u LEFT JOIN orders o ON u.id = o.user_id LEFT JOIN products p ON o.product_id = p.id LEFT JOIN categories c ON p.category_id = c.id",
        "SELECT * FROM employees WHERE name LIKE '%john%'",
        "SELECT department, COUNT(*) FROM employees WHERE salary > 50000 GROUP BY department ORDER BY COUNT(*)",
        "SELECT * FROM orders WHERE order_id IN (SELECT order_id FROM order_items WHERE quantity > 5)",
    ]

    print("SQL Query Optimization Recommendations\n" + "="*70)

    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query[:70]}{'...' if len(query) > 70 else ''}\n")

        summary = optimizer.get_optimization_summary(query)

        print(f"Analysis:")
        print(f"  JOINs: {summary['analysis']['num_joins']}")
        print(f"  Has WHERE: {summary['analysis']['has_where_clause']}")
        print(f"  Uses SELECT *: {summary['analysis']['uses_select_star']}")
        print(f"  Tables: {', '.join(summary['tables'])}")

        if summary['recommendations']:
            print(f"\nRecommendations ({len(summary['recommendations'])}):")
            for rec in summary['recommendations']:
                print(f"  • {rec}")
        else:
            print(f"\n✓ No optimization recommendations for this query.")

        print()
