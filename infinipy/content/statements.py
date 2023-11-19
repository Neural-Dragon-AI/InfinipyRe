from typing import Callable, Any
from infinipy.stateblock import StateBlock
from infinipy.statement import Statement

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
