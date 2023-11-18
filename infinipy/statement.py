from typing import Callable, Tuple
from stateblock import StateBlock


class Statement:
    def __init__(self, name: str, input_type: type, description: str, condition: Callable[[any], bool]):
        """
        Initializes the Statement with a specific condition.

        :param name: The name of the statement.
        :param input_type: The expected type of the variable the condition will be applied to.
        :param description: A brief description of what the condition checks for.
        :param condition: A callable that takes a variable value and returns a boolean.
        """
        self.name = name
        self.input_type = input_type
        self.description = description
        self.condition = condition

    def apply(self, state_block: StateBlock, variable_name: str) -> bool:
        """
        Applies the condition to the specified variable in the state_block, after validating the data type.

        :param state_block: A StateBlock instance representing the state of an entity.
        :param variable_name: The name of the variable to which the condition will be applied.
        :return: True if the condition is met, False otherwise.
        """
        if not hasattr(state_block, variable_name):
            raise ValueError(f"Variable '{variable_name}' not found in StateBlock.")

        variable_value = getattr(state_block, variable_name)
        if not isinstance(variable_value, self.input_type):
            raise TypeError(f"Expected type {self.input_type.__name__} for variable '{variable_name}', got {type(variable_value).__name__} instead.")

        return self.condition(variable_value)
    
    def __call__(self, state_block: StateBlock, variable_name: str) -> bool:
        """
        Allows the instance to be called as a function, which internally calls the apply method.

        :param state_block: A StateBlock instance representing the state of an entity.
        :param variable_name: The name of the variable to which the condition will be applied.
        :return: True if the condition is met, False otherwise.
        """
        return self.apply(state_block, variable_name)

    

class CompositeStatement:
    def __init__(self, statement_conditions: list[Tuple[Statement, str, str]]):
        """
        Initializes the CompositeStatement with a list of tuples.
        Each tuple contains a Statement instance, the variable name to apply it to, and a condition string ('AND', 'OR', 'NOT').

        :param statement_conditions: A list of tuples in the form [(statement1, 'variable_name1', 'AND'), (statement2, 'variable_name2', 'OR'), ...].
        """
        self.statement_conditions = statement_conditions
        self.name = ' AND '.join([f"({s.name} {cond})" for s, _, cond in statement_conditions])

    def apply(self, state_block: StateBlock) -> bool:
        """
        Applies the composite conditions to the StateBlock.

        :param state_block: A StateBlock instance representing the state of an entity.
        :return: True if the composite condition is met, False otherwise.
        """
        if not self.statement_conditions:
            return True

        statement, variable_name, _ = self.statement_conditions[0]
        current_result = statement.apply(state_block, variable_name)
        for statement, variable_name, condition in self.statement_conditions[1:]:
            if condition == 'AND':
                current_result = current_result and statement.apply(state_block, variable_name)
            elif condition == 'OR':
                current_result = current_result or statement.apply(state_block, variable_name)
            elif condition == 'NOT':
                current_result = not statement.apply(state_block, variable_name)
            else:
                raise ValueError(f"Invalid condition: {condition}")

        return current_result

    def __call__(self, state_block: StateBlock) -> bool:
        """
        Allows the instance to be called as a function, which internally calls the apply method.

        :param state_block: A StateBlock instance representing the state of an entity.
        :return: True if the composite condition is met, False otherwise.
        """
        return self.apply(state_block)

class RelationalStatement:
    def __init__(self, name: str, description: str, condition: Callable[[StateBlock, StateBlock, str, str], bool]):
        """
        Initializes the RelationalStatement with a specific condition involving two StateBlocks.

        :param name: The name of the statement.
        :param description: A brief description of what the condition checks for.
        :param condition: A callable that takes two StateBlock instances and two variable names, then returns a boolean.
        """
        self.name = name
        self.description = description
        self.condition = condition

    def apply(self, source_block: StateBlock, target_block: StateBlock, source_variable: str, target_variable: str) -> bool:
        """
        Applies the condition to the specified source and target StateBlocks and their respective variables.

        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
        :param source_variable: The variable name in the source StateBlock to which the condition will be applied.
        :param target_variable: The variable name in the target StateBlock to which the condition will be applied.
        :return: True if the condition is met, False otherwise.
        """
        return self.condition(source_block, target_block, source_variable, target_variable)

    def __call__(self, source_block: StateBlock, target_block: StateBlock, source_variable: str, target_variable: str) -> bool:
        """
        Allows the instance to be called as a function, which internally calls the apply method.

        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
        :param source_variable: The variable name in the source StateBlock to which the condition will be applied.
        :param target_variable: The variable name in the target StateBlock to which the condition will be applied.
        :return: True if the condition is met, False otherwise.
        """
        return self.apply(source_block, target_block, source_variable, target_variable)

    
class CompositeRelationalStatement:
    def __init__(self, relational_conditions: list[Tuple[RelationalStatement, str, str, str]]):
        """
        Initializes the CompositeRelationalStatement with a list of tuples.

        :param relational_conditions: A list of tuples in the form 
                                      [(relational_statement1, 'source_variable1', 'target_variable1', 'AND'), ...].
        """
        self.relational_conditions = relational_conditions

    def apply(self, source_block: StateBlock, target_block: StateBlock) -> bool:
        if not self.relational_conditions:
            return True

        statement, source_variable, target_variable, condition = self.relational_conditions[0]
        current_result = statement.apply(source_block, target_block, source_variable, target_variable)
        for statement, source_variable, target_variable, condition in self.relational_conditions[1:]:
            next_result = statement.apply(source_block, target_block, source_variable, target_variable)
            if condition == 'AND':
                current_result = current_result and next_result
            elif condition == 'OR':
                current_result = current_result or next_result
            elif condition == 'NOT':
                current_result = not next_result
            else:
                raise ValueError(f"Invalid condition: {condition}")

        return current_result

    def __call__(self, source_block: StateBlock, target_block: StateBlock) -> bool:
        """
        Allows the instance to be called as a function, which internally calls the apply method.

        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
        :return: True if the composite condition is met, False otherwise.
        """
        return self.apply(source_block, target_block)



# Redefining the generic conditions to be used for initializing Statement objects

def bigger_than(target_value: int) -> Statement:
    condition = lambda x: x > target_value
    return Statement("bigger_than",int, f"Checks if value is greater than {target_value}", condition)

def between(min_val: int, max_val: int) -> Statement:
    condition = lambda x: min_val <= x <= max_val
    return Statement("between",int, f"Checks if value is between {min_val} and {max_val}", condition)

def positive() -> Statement:
    condition = lambda x: x > 0
    return Statement("positive",int, "Checks if a numeric attribute is positive", condition)

def contains_string(substring: str) -> Statement:
    condition = lambda x: substring in x
    return Statement("contains_string",str, f"Checks if string contains '{substring}'", condition)

def equals_to(value: any) -> Statement:
    condition = lambda x: x == value
    return Statement("equals_to",type(value), f"Checks if value equals {value}", condition)

def less_than(target_value: int) -> Statement:
    condition = lambda x: x < target_value
    return Statement("less_than",int, f"Checks if value is less than {target_value}", condition)

def non_empty() -> Statement:
    condition = bool
    return Statement("non_empty",any, "Checks if the attribute is not empty or None", condition)

def divisible_by(divisor: int) -> Statement:
    condition = lambda x: x % divisor == 0
    return Statement("divisible_by",int, f"Checks if value is divisible by {divisor}", condition)

def is_type(type_check: type) -> Statement:
    condition = lambda x: isinstance(x, type_check)
    return Statement("is_type_condition",type, f"Checks if the attribute is of type {type_check.__name__}", condition)

def has_attribute(attribute_name: str) -> Statement:
    condition = lambda x: hasattr(x, attribute_name)
    return Statement("has_attribute",str, f"Checks if the attribute has the attribute '{attribute_name}'", condition)