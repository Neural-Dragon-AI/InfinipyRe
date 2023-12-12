from typing import Dict, List, Union
from dataclasses import fields
from infinipy.stateblock import StateBlock
from infinipy.statement import Statement

def create_bool_statements_from_stateblock(state_block: StateBlock) -> Dict[str, Statement]:
    statements = {}
    for field in fields(state_block):
        # Check if the field is a boolean attribute
        if isinstance(getattr(state_block, field.name), bool):
            # Define the condition function for the Statement
            condition_func = lambda block, attr=field.name: getattr(block, attr)

            # Create a Statement for the boolean attribute
            statement = Statement(
                name=f"Is_{field.name.capitalize()}Condition",
                description=f"Is_True_Condition for {field.name}",
                callable=condition_func,
                usage="target"
            )

            # Add the statement to the dictionary
            statements[field.name] = statement

    return statements

def create_matching_statements_from_stateblock(template_block: StateBlock) -> Dict[str, Statement]:
    statements = {}
    for field in fields(template_block):
        # Check if the field is a string attribute
        if isinstance(getattr(template_block, field.name), str):
            # Define the condition function for the Statement
            # It checks if the target's attribute value matches the template block's attribute value
            condition_func = lambda target, template=template_block, attr=field.name: getattr(target, attr) == getattr(template, attr)

            # Create a Statement for the string attribute
            statement = Statement(
                name=f"{field.name.capitalize()}MatchCondition",
                description=f"Condition where {field.name} of target matches {field.name} of the template block",
                callable=condition_func,
                usage="target"  # Indicates that this condition requires a target
            )

            # Add the statement to the dictionary
            statements[field.name] = statement

    return statements