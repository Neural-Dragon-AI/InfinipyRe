from typing import List, Tuple, Optional, Dict
from infinipy.stateblock import StateBlock
from infinipy.statement import CompositeStatement

from typing import List, Tuple, Optional
from infinipy.stateblock import StateBlock
from infinipy.statement import CompositeStatement, Statement
from infinipy.actions import Action

class WorldStatement:
    def __init__(self, statements: List[Tuple[CompositeStatement, Optional[str], Optional[str]]]):
        """
        Initializes a WorldStatement with a list of CompositeStatements and their source and target StateBlocks.

        :param statements: A list of tuples, each containing a CompositeStatement, a source StateBlock, and an optional target StateBlock.
        """
        self.statements = statements
        self.conditions = self.categorize_statements()

    def print_conditions(self):
        """
        Prints nicely formatted conditions using f-strings
        """
        for key, value in self.conditions.items():
            print(f"{key}: {value.name}")

    def categorize_statements(self) -> Dict[Tuple[Optional[str], Optional[str]], CompositeStatement]:
        """
        Categorizes the statements into separate dictionaries based on their source and target StateBlocks.

        :return: A dictionary with keys as tuples of StateBlock ids (source_id, target_id) and values as CompositeStatements.
        """
        conditions_dict = {}
        for comp_statement, source_block_id, target_block_id in self.statements:
            for statement, cond in comp_statement.substatements:
                key = self._derive_key(statement, source_block_id, target_block_id)

                if key not in conditions_dict:
                    conditions_dict[key] = []

                conditions_dict[key].append((statement, cond))

        # Create CompositeStatements for each key
        for key, value in conditions_dict.items():
            conditions_dict[key] = CompositeStatement(value)

        return conditions_dict

    def _derive_key(self, statement:Statement, source_id:str, target_id:str):
        """
        Derives the appropriate key for the conditions dictionary.

        :param statement: The individual statement being processed.
        :param source_id: The ID of the source StateBlock.
        :param target_id: The ID of the target StateBlock.
        :return: A tuple representing the key.
        """
        if statement.usage == "source":
            return (source_id, None)
        elif statement.usage == "target":
            return (None, target_id)
        elif statement.usage == "both":
            return (source_id, target_id)
        else:
            raise ValueError(f"Unknown usage category: {statement.usage}")
        
    def remove_intersection(self, other: 'WorldStatement') -> 'WorldStatement':
        """
        Removes statements in the current WorldStatement that are also in another WorldStatement.

        :param other: The other WorldStatement to compare against.
        :return: A new WorldStatement object.
        """
        merged_statements = []
        for key in self.conditions.keys():
            if key in other.conditions:
                merged_statements.append((self.conditions[key].remove_intersection(other.conditions[key]), key[0], key[1]))
            else:
                merged_statements.append((self.conditions[key], key[0], key[1]))
        return WorldStatement(merged_statements)
        
    def merge(self, other: 'WorldStatement') -> 'WorldStatement':
        """
        Merges the current WorldStatement with another WorldStatement, giving precedence to the current WorldStatement.
        It works by iterating through all the statements in both WorldStatements and 
        a) if the statement is in both WorldStatements, it merges the statements with the current WorldStatement precedence
        b) if the statement is only in one WorldStatement, it adds the statement to the merged WorldStatement

        :param other: The other WorldStatement to merge with.
        :return: A new WorldStatement object.
        """
        merged_statements = []
        for key in self.conditions.keys():
            if key in other.conditions:
                merged_statements.append((self.conditions[key].merge(other.conditions[key]), key[0], key[1]))
            else:
                merged_statements.append((self.conditions[key], key[0], key[1]))
        for key in other.conditions.keys():
            if key not in self.conditions:
                merged_statements.append((other.conditions[key], key[0], key[1]))
        return WorldStatement(merged_statements)
        
    def force_merge(self, other: 'WorldStatement', force_direction: str = "left") -> 'WorldStatement':
        """
        Merges the current WorldStatement with another WorldStatement, giving precedence to the force direction.
        It works by iterating through all the statements in both WorldStatements and 
        a) if the statement is in both WorldStatements, it merges the statements with the force_direction precedence
        b) if the statement is only in one WorldStatement, it adds the statement to the merged WorldStatement

        :param other: The other WorldStatement to merge with.
        :param force_direction: The direction to force the merge. Can be "left" or "right".
        :return: A new WorldStatement object.
        """
        merged_statements = []
        for key in self.conditions.keys():
            if key in other.conditions:
                merged_statements.append((self.conditions[key].force_merge(other.conditions[key], force_direction), key[0], key[1]))
            else:
                merged_statements.append((self.conditions[key], key[0], key[1]))
        for key in other.conditions.keys():
            if key not in self.conditions:
                merged_statements.append((other.conditions[key], key[0], key[1]))
        return WorldStatement(merged_statements)

    def falsifies(self, other: 'WorldStatement') -> bool:
        for key in self.conditions.keys():
            if key in other.conditions:
                if self.conditions[key].falsifies(other.conditions[key]):
                    return True
        return False

    def is_falsified_by(self, other: 'WorldStatement') -> bool:
        return other.falsifies(self)

    def validates(self, other: 'WorldStatement') -> bool:
        conditions_to_satisfy = len(other.conditions)
        for key in self.conditions.keys():
            if key in other.conditions:
                if self.conditions[key].validates(other.conditions[key]):
                    conditions_to_satisfy -= 1
        if conditions_to_satisfy == 0:
            return True
        return False

    def is_validated_by(self, other: 'WorldStatement') -> bool:
        return other.validates(self)
    
    def count_conflicts(self, other: 'WorldStatement') -> int:
        """
        Counts the number of conflicting statements between this WorldStatement and another.

        :param other: Another WorldStatement to compare against.
        :return: The number of conflicting statements.
        """
        conflicts = 0
        not_found = 0
        for key, self_comp_statement in self.conditions.items():
            other_comp_statement = other.conditions.get(key)
            if other_comp_statement:
                for self_substatement, self_value in self_comp_statement.substatements:
                    for other_substatement, other_value in other_comp_statement.substatements:
                        if self_substatement == other_substatement and self_value != other_value:
                            conflicts += 1
            else:
                not_found += 1
        return conflicts, not_found
    
    def allows_action(self, action: Action, reverse = False) -> bool:
        """
        Checks if the current world state validates the prerequisites of the given action.

        :param action: The action to check.
        :return: True if the prerequisites are validated by the current world state, False otherwise.
        """
        if reverse:
            # print("reverse",action.name)
            post_action_world_statement = WorldStatement.from_dict(action.con_dict)
            return not self.is_falsified_by(post_action_world_statement)
        action_pre_world_statement = WorldStatement.from_dict(action.pre_dict)
        return self.validates(action_pre_world_statement)

    def available_actions(self, actions: List[Action],reverse=False) -> List[Action]:
        """
        Determines which actions from a given list are available based on the current world state.

        :param actions: List of Action objects.
        :return: List of Actions that are available in the current world state.
        """
        if reverse:
            # print("reverse")
            return [action for action in actions if self.allows_action(action,reverse=True)]
        return [action for action in actions if self.allows_action(action)]
    
    @classmethod
    def from_dict(cls, consequence_prereq_dict: dict) -> 'WorldStatement':
        """
        Class method to initialize a WorldStatement from a dictionary of consequences or prerequisites.

        :param consequence_prereq_dict: A dictionary where keys are tuples of StateBlock IDs (source_id, target_id)
                                        and values are CompositeStatements.
        :return: An initialized WorldStatement object.
        """
        statements = []
        for key, composite_statement in consequence_prereq_dict.items():
            source_id, target_id = key
            statements.append((composite_statement, source_id, target_id))

        return cls(statements)
    