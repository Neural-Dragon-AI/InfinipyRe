from typing import Callable, Tuple, Optional, List, Dict
from infinipy.stateblock import StateBlock
import itertools



class Statement:
    def __init__(self, 
                 name: str, 
                 description: str, 
                 condition: Callable[[StateBlock, Optional[StateBlock]], bool],
                 required_attributes: Optional[Dict[str, List[str]]] = None):
        """
        Initializes the Statement with a specific condition involving two StateBlocks.

        :param name: The name of the statement.
        :param description: A brief description of what the condition checks for.
        :param condition: A callable that takes two StateBlock instances and returns a boolean.
        """
        self.name = name
        self.description = description
        self.condition = condition
        self.source_required = required_attributes.get('source') if required_attributes else None
        self.target_required = required_attributes.get('target') if required_attributes else None

    
    def check_required_attributes(self, source_block: StateBlock, target_block: Optional[StateBlock]) -> bool:
        """
        Checks if the required attributes are present in the source and target StateBlocks. Collect all the missing from boths and returns a boolean and two lists of missing attributes.

        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
       
        """
        source_missing = []
        target_missing = []
        if self.source_required:
            for attribute in self.source_required:
                if attribute not in source_block.attributes:
                    source_missing.append(attribute)
        if self.target_required:
            for attribute in self.target_required:
                if attribute not in target_block.attributes:
                    target_missing.append(attribute)
        if len(source_missing)>0 and len(target_missing)>0:
            return False, source_missing, target_missing
        elif len(source_missing)>0:
            return False, source_missing, None
        elif len(target_missing)>0:
            return False, None, target_missing
        return True, None, None

    def create_statement_fstring(self, statement_result:bool,source_block: StateBlock, target_block: Optional[StateBlock]) -> str:
        """
        Creates a string representation of the statement when the condition is met.

        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
        :return: A string representation of the statement when the condition is met.
        """
        if target_block is None:
         return f"The statement {source_block.name} {self.description} is {statement_result}."
        return f"The statement {source_block.name} {self.description} to {target_block.name} is {statement_result}."
    
    def create_statement_fstring_missing_attributes(self, source_block:StateBlock, target_block:  Optional[StateBlock], source_missing: Optional[List[str]], target_missing: Optional[List[str]]) -> str:
        """
        Creates a string representation of the statement when the condition is not met because of missing attributes.

        :param source_missing: A list of missing attributes in the source StateBlock.
        :param target_missing: A list of missing attributes in the target StateBlock.
        :return: A string representation of the statement when the condition is not met because of missing attributes.
        """
        if source_missing and target_missing:
            return f"The statement {self.name} {self.description} is not met because the source {source_block.name} is missing the attributes {source_missing} and the target {target_block.name} is missing the attributes {target_missing}."
        elif source_missing:
            return f"The statement {self.name} {self.description} is not met because the source {source_block.name} is missing the attributes {source_missing}."
        elif target_missing:
            return f"The statement {self.name} {self.description} is not met because the target {target_block.name} is missing the attributes {target_missing}."
        else:
            raise ValueError(f"Missing attributes but no missing attributes found for statement {self.name}")

    def create_out_dict(self,result,source_block: StateBlock, target_block: Optional[StateBlock] , source_missing: Optional[List[str]], target_missing: Optional[List[str]]):
        """
        Creates a dictionary representation of the statement when the condition is met.

        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
        :param source_missing: A list of missing attributes in the source StateBlock.
        :param target_missing: A list of missing attributes in the target StateBlock.
        :return: A dictionary representation of the statement when the condition is met.
        """
        return {"result":result,"source":source_block.name,"target":target_block.name if target_block else None,"statement":self.name,"stringout":self.create_statement_fstring(result,source_block, target_block),"source_missing":source_missing,"target_missing":target_missing}

    
    def apply(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> (bool, str):
        """
        Applies the condition to the specified source and target StateBlocks.

        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
        :return: True if the condition is met, False otherwise.
        """
        # Check if the required attributes are present in the source and target StateBlocks
        required_attributes_present, source_missing, target_missing = self.check_required_attributes(source_block, target_block)
        if not required_attributes_present:
            return False, self.create_out_dict(False,source_block, target_block, source_missing, target_missing)
        if not target_block:
            statement_result = self.condition(source_block)
            return statement_result, self.create_out_dict(statement_result,source_block, target_block, source_missing, target_missing)
        statement_result = self.condition(source_block, target_block)
        return statement_result, self.create_out_dict(statement_result,source_block, target_block, source_missing, target_missing)
    
    def force_true(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> (bool, str):
        return True, self.create_out_dict(True,source_block, target_block, None, None)
    
    def force_false(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> (bool, str):
        return False, self.create_out_dict(False,source_block, target_block, None, None)

    def __call__(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> bool:
        """
        Allows the instance to be called as a function, which internally calls the apply method.

        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
        :return: True if the condition is met, False otherwise.
        """
    
        return self.apply(source_block, target_block)
    



    
class CompositeStatement:
    def __init__(self, conditions: List[Tuple[Statement, str, str]]):
        """ Initializes the CompositeStatement with a set of unique conditions. """
        # Convert list of conditions to a set to avoid duplicates
        self.conditions = set(conditions)
        self._check_for_conflicts()
        self.name = self._derive_name()
    
    @classmethod
    def from_composite_statements(cls, composite_statements: List['CompositeStatement']):
        """
        Class method to initialize a CompositeStatement from a list of other CompositeStatements.
        It extracts individual statements from each CompositeStatement and combines them.

        :param composite_statements: List of CompositeStatement objects.
        :return: A new CompositeStatement consisting of the combined statements.
        """
        combined_conditions = set()
        for composite in composite_statements:
            # Extract individual statements from each composite statement
            for condition in composite.conditions:
                combined_conditions.add(condition)

        # Create a new CompositeStatement with the combined conditions
        return cls(list(combined_conditions))

    def _derive_name(self):
        """ Derives the name of the CompositeStatement based on its conditions. """
        return f"CompositeStatement({', '.join([f'{cond[0].name} {cond[1]} {cond[2]}' for cond in self.conditions])})"

    def _check_for_conflicts(self):
        """ Checks for logical conflicts within the conditions of the CompositeStatement. """
        category_sets = {
            'source': {'positive': set(), 'negative': set()},
            'target': {'positive': set(), 'negative': set()},
            'both': {'positive': set(), 'negative': set()}
        }

        for statement, condition, usage in self.conditions:
            sets = category_sets[usage]
            if condition == 'AND':
                self._add_to_set_and_check_conflict(sets['positive'], sets['negative'], statement)
            elif condition == 'AND NOT':
                self._add_to_set_and_check_conflict(sets['negative'], sets['positive'], statement)

    def _add_to_set_and_check_conflict(self, positive_set, negative_set, statement):
        """ Adds a statement to the positive set and checks for conflict with the negative set. """
        if statement in negative_set:
            raise ValueError(f"Conflict detected for '{statement.name}' in CompositeStatement.")
        positive_set.add(statement)

    def apply_statement_with_usage(self, statement: Statement, usage: str, source_block: StateBlock, target_block: Optional[StateBlock]) -> dict:
        """
        Apply the given statement based on the specified usage.
        """
        if usage == 'source':
            return statement(source_block)
        elif usage == 'target':
            return statement(target_block)
        elif usage == 'both':
            return statement(source_block, target_block)
        else:
            raise ValueError(f"Invalid usage: {usage} for statement {statement.name} in composite statement {self.name}")


    def create_combined_fstring(self, result_strings: List[str]) -> str:
        combined_string = ""
        for i, string in enumerate(result_strings):
            if i > 0:
                _, operator, _ = self.conditions[i]
                combined_string += f" {operator} "
            combined_string += string
        return combined_string
        

    def apply(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> dict:
        if not self.conditions:
            return {"result": True, "composite_string": "", "sub_statements": []}

        # Process the first condition separately
        first_statement, first_condition, first_usage = self.conditions[0]
        _, first_result_dict = self.apply_statement_with_usage(first_statement, first_usage, source_block, target_block)
        composite_result = first_result_dict["result"]
        sub_statements = [first_result_dict]
        composite_string = [first_result_dict["stringout"]]

        # Iterate over the remaining conditions
        for statement, condition, usage in self.conditions[1:]:
            _, next_result_dict = self.apply_statement_with_usage(statement, usage, source_block, target_block)
            sub_statements.append(next_result_dict)
            composite_string.append(next_result_dict["stringout"])


            # Evaluate the composite result based on the condition
            if condition == 'AND':
                composite_result = composite_result and next_result_dict["result"]
            elif condition == 'AND NOT':
                composite_result = composite_result and not next_result_dict["result"]
            else:
                raise ValueError(f"Invalid condition: {condition} for statement {statement.name} in composite statement {self.name}")

        return {
            "result": composite_result,
            "name": self.name,
            "composite_string": self.create_combined_fstring(composite_string),
            "sub_statements": sub_statements
        }
    
    def _force_statement(self, source_block: StateBlock, target_block: Optional[StateBlock], desired_result: bool) -> List[Dict]:
        """
        Generates hypothetical results for each statement in the composite to satisfy a desired global result.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        :param desired_result: The desired global result (True or False).
        :return: A list of dictionaries with hypothetical results satisfying the desired result.
        """
        results = []
        for statement, condition, usage in self.conditions:
            # Hypothetically determine the result of each statement
            if condition == 'AND':
                statement_result = desired_result
            elif condition == 'AND NOT':
                statement_result = not desired_result

            # Create a hypothetical result dictionary
            result_dict = statement.create_out_dict(statement_result, source_block, target_block, None, None)
            results.append(result_dict)

        return results

    def force_true(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> List[Dict]:
        """
        Generates hypothetical results for each statement in the composite to make the global condition true.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        :return: A list of dictionaries representing hypothetical results that make the global condition true.
        """
        return self._force_statement(source_block, target_block, desired_result=True)

    def force_false(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> List[Dict]:
        """
        Generates hypothetical results for each statement in the composite to make the global condition false.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        :return: A list of dictionaries representing hypothetical results that make the global condition false.
        """
        return self._force_statement(source_block, target_block, desired_result=False)
    
    def concatenate(self, other: 'CompositeStatement', operator: str = 'AND'):
        """
        Concatenates the current CompositeStatement with another CompositeStatement.
        """
        if operator not in ['AND', 'AND NOT']:
            raise ValueError(f"Invalid operator: {operator} for concatenation.")
        elif operator == 'AND':
            return CompositeStatement(self.conditions + other.conditions)
        elif operator == 'AND NOT':
            new_operators = ['AND NOT' if condition == 'AND' else 'AND' for _, condition, _ in other.conditions]
            new_conditions = [(statement, new_operator, usage) for (statement, _, usage), new_operator in zip(other.conditions, new_operators)]
            return CompositeStatement(self.conditions + new_conditions)

    def __call__(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> dict:
        return self.apply(source_block, target_block)

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


