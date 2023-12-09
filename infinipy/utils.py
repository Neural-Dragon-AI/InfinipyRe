from infinipy.statement import CompositeStatement
from infinipy.stateblock import StateBlock
from typing import Tuple, Optional, List

#compares two composite statements, each with a usage, the output is a dictionary with the results for the four tuples:
# AND, AND
# AND, AND NOT
# AND NOT, AND
# AND NOT, AND NOT
def compare_composite_statements(statement_1: Tuple[CompositeStatement, str], statement_2: Tuple[CompositeStatement, str], source: StateBlock, target: Optional[StateBlock] = None):
    """ Compares two composite statements using their force_true, each with a usage, the output is a dictionary with the results for the four tuples. """

    def force_statement(statement: CompositeStatement, force_method: str):
        if force_method == 'AND':
            return statement.force_true(source, target)
        elif force_method == 'AND NOT':
            return statement.force_false(source, target)
        else:
            raise ValueError(f"Invalid force method: {force_method}")

    def categorize_statements(force_results_1, force_results_2):
        consistent, inconsistent, independent = [], [], []

        # Map statement names to their results for easier comparison
        results_map_2 = {result['name']: result for result in force_results_2}

        for result_1 in force_results_1:
            name_1 = result_1['name']
            if name_1 in results_map_2:
                result_2 = results_map_2[name_1]
                if result_1['result'] == result_2['result']:
                    consistent.append(name_1)
                else:
                    inconsistent.append(name_1)
            else:
                independent.append(name_1)

        # Check for statements in the second set that are not in the first set
        names_set_1 = set(result['name'] for result in force_results_1)
        for name_2 in results_map_2:
            if name_2 not in names_set_1:
                independent.append(name_2)

        return consistent, inconsistent, independent

    # Force statements with the specified methods
    force_results_1_and = force_statement(statement_1[0], 'AND')
    force_results_1_and_not = force_statement(statement_1[0], 'AND NOT')
    force_results_2_and = force_statement(statement_2[0], 'AND')
    force_results_2_and_not = force_statement(statement_2[0], 'AND NOT')

    # Comparing the combinations of forced results
    results = {
        'AND, AND': categorize_statements(force_results_1_and, force_results_2_and),
        'AND, AND NOT': categorize_statements(force_results_1_and, force_results_2_and_not),
        'AND NOT, AND': categorize_statements(force_results_1_and_not, force_results_2_and),
        'AND NOT, AND NOT': categorize_statements(force_results_1_and_not, force_results_2_and_not),
    }

    return results