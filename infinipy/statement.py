from typing import Callable, Tuple, Optional, List, Dict
from infinipy.stateblock import StateBlock




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
            raise ValueError("Missing attributes but no missing attributes found.")

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
            return False, self.create_statement_fstring_missing_attributes(source_block, target_block,source_missing, target_missing)
        if not target_block:
            statement_result = self.condition(source_block)
            return statement_result, self.create_statement_fstring(statement_result, source_block)
        statement_result = self.condition(source_block, target_block)
        return statement_result, self.create_statement_fstring(statement_result, source_block, target_block)

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
        """
        Initializes the CompositeStatement with a list of tuples.

        :param conditions: A list of tuples in the form 
                                      [(statement1, 'AND', 'source'), ...].
                                      the first element of the tuple is a Statement instance, 
                                      the second element is a string representing the condition ('AND', 'OR', 'AND NOT', 'OR NOT'), 
                                      and the third element is a string representing the StateBlock ('source' or 'target', 'both'.
        """
        self.conditions = conditions

    def apply_statement_with_usage(self, statement: Statement, source_block: StateBlock, target_block: Optional[StateBlock], usage: str) -> (bool,str):
        """
        Applies the condition to the specified source and target StateBlocks.

        :param statement: The Statement instance to be applied.
        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
        :param usage: A string representing the StateBlock ('source' or 'target', 'both'.
        :return: True if the condition is met, False otherwise.
        """
        if usage == 'source':
            return statement(source_block)
        elif usage == 'target':
            return statement(target_block)
        elif usage == 'both':
            return statement(source_block, target_block)
        else:
            raise ValueError(f"Invalid usage: {usage}")
    
    def create_combined_fstring(self, result_strings: List[str]) -> str:
        """
        Creates a combined string representation of the composite statement evaluation process.

        :param result_strings: A list of strings representing the evaluation of individual statements.
        :return: A combined string representation of the composite statement.
        """
        combined_string = ""
        for i, string in enumerate(result_strings):
            if i > 0:
                # Add the logical operator before the current string
                _, operator, _ = self.conditions[i]
                combined_string += f" {operator} "
            combined_string += string
        return combined_string

    def apply(self, source_block: StateBlock, target_block: Optional[StateBlock]= None) -> (bool, str):
        if not self.conditions:
            return True
        
        statement, condition, usage = self.conditions[0]
        current_result, first_string = self.apply_statement_with_usage(statement, source_block, target_block, usage)
        local_results = [current_result]
        out_strings = [first_string]
        for statement, condition, usage in self.conditions[1:]:

            next_result,next_string = self.apply_statement_with_usage(statement, source_block, target_block, usage)
            out_strings.append(next_string)
            local_results.append(next_result)
            if condition == 'AND':
                current_result = current_result and next_result
            elif condition == 'OR':
                current_result = current_result or next_result
            elif condition == 'AND NOT':
                current_result = current_result and not next_result
            elif condition == 'OR NOT':
                current_result = current_result or (not next_result)
            else:
                raise ValueError(f"Invalid condition: {condition}")

        return current_result, self.create_combined_fstring(out_strings)

    def __call__(self, source_block: StateBlock, target_block: StateBlock) -> bool:
        """
        Allows the instance to be called as a function, which internally calls the apply method.

        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
        :return: True if the composite condition is met, False otherwise.
        """
        return self.apply(source_block, target_block)




