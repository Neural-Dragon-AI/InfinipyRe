import dataclasses
from infinipy.stateblock import StateBlock
from typing import Dict, Set, Tuple, Optional, Union, List

def compare_numbers(num1, num2):
    return abs(num1 - num2)

def compare_tuples(tuple1, tuple2):
    return tuple(abs(a - b) for a, b in zip(tuple1, tuple2))

def compare_lists(list1, list2):
    if len(list1) != len(list2) or not all(isinstance(x, type(list2[0])) for x in list1):
        return {"length_difference": abs(len(list1) - len(list2)), "type_mismatch": True}
    common_elements = sum(1 for x in list1 if x in list2)
    return {"differing_elements": len(list1) - common_elements}
def compare_state_blocks(block1: StateBlock, block2: StateBlock) -> Tuple[Dict, Set[str], Set[str], Set[str], Set[str]]:
    diffs = {}
    fields_block1 = set(dataclasses.fields(block1))
    fields_block2 = set(dataclasses.fields(block2))

    # Identify shared and unique fields
    shared_fields = fields_block1 & fields_block2
    unique_to_block1 = fields_block1 - fields_block2
    unique_to_block2 = fields_block2 - fields_block1
    identical_fields = set()

    for field in shared_fields:
        value1 = getattr(block1, field.name, None)
        value2 = getattr(block2, field.name, None)

        # If values are the same, add to identical_fields
        if value1 == value2:
            identical_fields.add(field.name)
        else:
            value1 = getattr(block1, field.name, None)
            value2 = getattr(block2, field.name, None)

            if type(value1) in [int, float] and type(value1) == type(value2):
                diff = compare_numbers(value1, value2)
                if diff != 0:
                    diffs[field.name] = {"type": "number", "difference": diff}

            elif isinstance(value1, tuple) and isinstance(value2, tuple):
                diff = compare_tuples(value1, value2)
                if any(d != 0 for d in diff):
                    diffs[field.name] = {"type": "tuple", "difference": diff}

            elif isinstance(value1, list) and isinstance(value2, list):
                diff = compare_lists(value1, value2)
                if diff.get("length_difference", 0) != 0 or diff.get("differing_elements", 0) != 0:
                    diffs[field.name] = {"type": "list", "difference": diff}

            elif isinstance(value1, StateBlock):
                diff = compare_state_blocks(value1, value2)
                if diff:
                    diffs[field.name] = {"type": "StateBlock", "difference": diff}

            elif value1 != value2:
                diffs[field.name] = {"type": "other", "difference": (value1, value2)}

    # Convert sets of fields to sets of field names
    shared_field_names = {field.name for field in shared_fields}
    unique_to_block1_names = {field.name for field in unique_to_block1}
    unique_to_block2_names = {field.name for field in unique_to_block2}

    return diffs, shared_field_names, unique_to_block1_names, unique_to_block2_names, identical_fields