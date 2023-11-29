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
    def __init__(self, conditions: list[Tuple[Statement, str, str]]):
        """ Initializes the CompositeStatement with a list of conditions. Each condition is a tuple of a Statement, a condition (AND, OR, AND NOT, OR NOT) and a usage (source, target, both)."""
        self.conditions = conditions
        #derive name from conditions using statement.name, their condition and usage 
        # statement are conditions[0][0], conditions[1][0], etc.
        # condition are conditions[0][1], conditions[1][1], etc.
        # usage are conditions[0][2], conditions[1][2], etc.
        self.name = f"CompositeStatement({', '.join([f'{condition[0].name} {condition[1]} {condition[2]}' for condition in conditions])})"

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
            elif condition == 'OR':
                composite_result = composite_result or next_result_dict["result"]
            elif condition == 'AND NOT':
                composite_result = composite_result and not next_result_dict["result"]
            elif condition == 'OR NOT':
                composite_result = composite_result or not next_result_dict["result"]
            else:
                raise ValueError(f"Invalid condition: {condition} for statement {statement.name} in composite statement {self.name}")

        return {
            "result": composite_result,
            "name": self.name,
            "composite_string": self.create_combined_fstring(composite_string),
            "sub_statements": sub_statements
        }
    
    def force_true(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> List[Dict]:
        """
        Finds all combinations of local statement values that make the global composite condition true.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        :return: A list of dictionaries representing combinations that make the global condition true.
        """
        return self._force_statement(source_block, target_block, desired_result=True)

    def force_false(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> List[Dict]:
        """
        Finds all combinations of local statement values that make the global composite condition false.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        :return: A list of dictionaries representing combinations that make the global condition false.
        """
        return self._force_statement(source_block, target_block, desired_result=False)

    def _force_statement(self, source_block: StateBlock, target_block: Optional[StateBlock], desired_result: bool) -> List[Dict]:
        """
        Internal method to find combinations of local statements that satisfy a desired global composite result.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        :param desired_result: The desired global result (True or False).
        :return: A list of dictionaries with combinations satisfying the desired result.
        """
        all_combinations = itertools.product([True, False], repeat=len(self.conditions))
        satisfying_results = []

        for combination in all_combinations:
            temp_results = []
            composite_string = []

            for statement_value, (statement, _, usage) in zip(combination, self.conditions):
                temp_dict = statement.create_out_dict(statement_value, source_block, target_block, None, None)
                temp_results.append(temp_dict)
                composite_string.append(temp_dict["stringout"])

            composite_result = self.evaluate_composite_condition(temp_results)
            if composite_result == desired_result:
                result_dict = {
                    "result": composite_result,
                    "name": self.name,
                    "composite_string": self.create_combined_fstring(composite_string),
                    "sub_statements": temp_results
                }
                satisfying_results.append(result_dict)

        return satisfying_results

    def evaluate_composite_condition(self, temp_results: List[Dict]) -> bool:
        """
        Evaluates the composite condition based on temporary results of individual statements.

        :param temp_results: A list of dictionaries representing temporary results of individual statements.
        :return: True if the composite condition is satisfied, False otherwise.
        """
        composite_result = temp_results[0]['result']
        for temp_dict, (_, condition, _) in zip(temp_results[1:], self.conditions[1:]):
            if condition == 'AND':
                composite_result = composite_result and temp_dict['result']
            elif condition == 'OR':
                composite_result = composite_result or temp_dict['result']
            elif condition == 'AND NOT':
                composite_result = composite_result and not temp_dict['result']
            elif condition == 'OR NOT':
                composite_result = composite_result or not temp_dict['result']
        
        return composite_result

    def __call__(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> dict:
        return self.apply(source_block, target_block)


