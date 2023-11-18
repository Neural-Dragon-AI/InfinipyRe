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

    def apply(self, state_block: StateBlock) -> bool:
        """
        Applies the condition to the specified variable in the state_block, after validating the data type.

        :param state_block: A StateBlock instance representing the state of an entity.
       
        :return: True if the condition is met, False otherwise.
        """

        return self.condition(state_block)
    
    def __call__(self, state_block: StateBlock) -> bool:
        """
        Allows the instance to be called as a function, which internally calls the apply method.

        :param state_block: A StateBlock instance representing the state of an entity.
        :param variable_name: The name of the variable to which the condition will be applied.
        :return: True if the condition is met, False otherwise.
        """
        return self.apply(state_block)

def bigger_than(target_value: int, attribute_name: str) -> Statement:
    condition = lambda state_block: getattr(state_block, attribute_name) > target_value
    return Statement(f"{attribute_name}_bigger_than_{target_value}", int, f"Checks if {attribute_name} is greater than {target_value}", condition)

def between(min_val: int, max_val: int, attribute_name: str) -> Statement:
    condition = lambda state_block: min_val <= getattr(state_block, attribute_name) <= max_val
    return Statement(f"{attribute_name}_between_{min_val}_and_{max_val}", int, f"Checks if {attribute_name} is between {min_val} and {max_val}", condition)

def positive(attribute_name: str) -> Statement:
    condition = lambda state_block: getattr(state_block, attribute_name) > 0
    return Statement(f"{attribute_name}_is_positive", int, "Checks if a numeric attribute is positive", condition)

def contains_string(substring: str, attribute_name: str) -> Statement:
    condition = lambda state_block: substring in getattr(state_block, attribute_name)
    return Statement(f"{attribute_name}_contains_{substring}", str, f"Checks if {attribute_name} contains '{substring}'", condition)

def equals_to(value: any, attribute_name: str) -> Statement:
    condition = lambda state_block: getattr(state_block, attribute_name) == value
    return Statement(f"{attribute_name}_equals_{value}", type(value), f"Checks if {attribute_name} equals {value}", condition)

def less_than(target_value: int, attribute_name: str) -> Statement:
    condition = lambda state_block: getattr(state_block, attribute_name) < target_value
    return Statement(f"{attribute_name}_less_than_{target_value}", int, f"Checks if {attribute_name} is less than {target_value}", condition)

def non_empty(attribute_name: str) -> Statement:
    condition = lambda state_block: bool(getattr(state_block, attribute_name))
    return Statement(f"{attribute_name}_is_non_empty", any, f"Checks if {attribute_name} is not empty or None", condition)

def divisible_by(divisor: int, attribute_name: str) -> Statement:
    condition = lambda state_block: getattr(state_block, attribute_name) % divisor == 0
    return Statement(f"{attribute_name}_divisible_by_{divisor}", int, f"Checks if {attribute_name} is divisible by {divisor}", condition)

def is_type(type_check: type, attribute_name: str) -> Statement:
    condition = lambda state_block: isinstance(getattr(state_block, attribute_name), type_check)
    return Statement(f"{attribute_name}_is_type_{type_check.__name__}", type, f"Checks if {attribute_name} is of type {type_check.__name__}", condition)

def has_attribute(attribute_name: str) -> Statement:
    condition = lambda state_block: hasattr(state_block, attribute_name)
    return Statement(f"has_attribute_{attribute_name}", str, f"Checks if the state block has the attribute '{attribute_name}'", condition)

def is_true(attribute_name: str) -> Statement:
    condition = lambda state_block: getattr(state_block, attribute_name) == True
    return Statement(f"{attribute_name}_is_true", str, f"Checks if the attribute '{attribute_name}' is True", condition)


class CompositeStatement:
    def __init__(self, statements: list[Tuple[Statement, str]]):
        """
        Initializes the CompositeStatement with a list of tuples.
        Each tuple contains a Statement instance and a condition string ('AND', 'OR', 'AND NOT', 'OR NOT').

        :param statements: A list of tuples in the form 
        [(statement1, 'AND'), (statement2, 'OR'), ...].
        """
        self.statements = statements
        self.name = ' AND '.join([f"({s.name} {cond})" for s, cond in statements])

    def apply(self, state_block: StateBlock) -> bool:
        """
        Applies the composite conditions to the StateBlock.

        :param state_block: A StateBlock instance representing the state of an entity.
        :return: True if the composite condition is met, False otherwise.
        """
        if not self.statements:
            return True

        statement, _ = self.statements[0]
        current_result = statement(state_block)
        for statement, condition in self.statements[1:]:
            if condition == 'AND':
                current_result = current_result and statement(state_block)
            elif condition == 'OR':
                current_result = current_result or statement(state_block)
            elif condition == 'AND NOT':
                current_result = current_result and not statement(state_block)
            elif condition == 'OR NOT':
                current_result = current_result or (not statement(state_block))
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
    def __init__(self, name: str, description: str, condition: Callable[[StateBlock, StateBlock], bool]):
        """
        Initializes the RelationalStatement with a specific condition involving two StateBlocks.

        :param name: The name of the statement.
        :param description: A brief description of what the condition checks for.
        :param condition: A callable that takes two StateBlock instances and returns a boolean.
        """
        self.name = name
        self.description = description
        self.condition = condition

    def apply(self, source_block: StateBlock, target_block: StateBlock) -> bool:
        """
        Applies the condition to the specified source and target StateBlocks.

        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
        :return: True if the condition is met, False otherwise.
        """
        return self.condition(source_block, target_block)

    def __call__(self, source_block: StateBlock, target_block: StateBlock) -> bool:
        """
        Allows the instance to be called as a function, which internally calls the apply method.

        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
        :return: True if the condition is met, False otherwise.
        """
        return self.apply(source_block, target_block)


    
class CompositeRelationalStatement:
    def __init__(self, relational_conditions: list[Tuple[RelationalStatement, str]]):
        """
        Initializes the CompositeRelationalStatement with a list of tuples.

        :param relational_conditions: A list of tuples in the form 
                                      [(relational_statement1, 'AND'), ...].
        """
        self.relational_conditions = relational_conditions

    def apply(self, source_block: StateBlock, target_block: StateBlock) -> bool:
        if not self.relational_conditions:
            return True

        statement, condition = self.relational_conditions[0]
        current_result = statement.apply(source_block, target_block)
        for statement, condition in self.relational_conditions[1:]:
            next_result = statement.apply(source_block, target_block)
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

        return current_result

    def __call__(self, source_block: StateBlock, target_block: StateBlock) -> bool:
        """
        Allows the instance to be called as a function, which internally calls the apply method.

        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
        :return: True if the composite condition is met, False otherwise.
        """
        return self.apply(source_block, target_block)




