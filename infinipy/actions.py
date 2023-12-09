from typing import List, Optional, Tuple
from infinipy.stateblock import StateBlock
from infinipy.statement import CompositeStatement

class Action:
    def __init__(self, name: str, prerequisites: List[CompositeStatement,], consequences: List[CompositeStatement],
                 source_block: StateBlock, target_block: Optional[StateBlock] = None):
        """
        Initializes an Action with prerequisites and consequences.

        :param name: The name of the action.
        :param prerequisites: A list of CompositeStatements representing the prerequisites for the action.
        :param consequences: A list of CompositeStatements representing the consequences of the action.
        """
        self.name = name
        self.prerequisites = CompositeStatement.from_composite_statements(prerequisites)
        self.consequences = CompositeStatement.from_composite_statements(consequences)
        # update the consequences with the prerequisites that are not already in the consequences
        self.consequences = self.prerequisites.force_merge(self.consequences, force_direction="right")
        self.source_block = source_block
        self.target_block = target_block
        self.pre_dict, self.con_dict = self.categorize_statements()
    
    def categorize_statements(self):
        """
        Categorizes the prerequisites and consequences into separate dictionaries (pre_dict and con_dict)
        each value of the dictionary is a CompositeStatement that combines the substatements in the original 
        CompositeStatement that have the same usage.

        :return: A tuple of two dictionaries (pre_dict, con_dict) with categorized statements.
        """
        pre_dict = {
            (self.source_block.id, None): [],
            (None, self.target_block.id): [],
            (self.source_block.id, self.target_block.id): []
        }
        con_dict = {
            (self.source_block.id, None): [],
            (None, self.target_block.id): [],
            (self.source_block.id, self.target_block.id): []
        }

        for statement, value in self.prerequisites.substatements:
            key = self._get_key_from_usage(statement.usage)
            pre_dict[key].append(CompositeStatement([(statement, value)]))

        for statement, value in self.consequences.substatements:
            key = self._get_key_from_usage(statement.usage)
            con_dict[key].append(CompositeStatement([(statement, value)]))
        to_pop = []
        for key,values in pre_dict.items():
            if len(values) > 0:
                pre_dict[key] = CompositeStatement.from_composite_statements(values)
            else:
                #pop empty list
                to_pop.append(key)
        for key in to_pop:
            pre_dict.pop(key)
        to_pop = []

        for key,values in con_dict.items():
            if len(values) > 0:
                con_dict[key] = CompositeStatement.from_composite_statements(values)
            else:
                #pop empty list
                to_pop.append(key)
        for key in to_pop:
            con_dict.pop(key)
        return pre_dict, con_dict

    def _get_key_from_usage(self, usage):
        """
        Derives the appropriate key based on the usage category.

        :param usage: The usage category ('source', 'target', or 'both').
        :return: A tuple representing the key.
        """
        if usage == 'source':
            return (self.source_block.id, None)
        elif usage == 'target':
            return (None, self.target_block.id)
        elif usage == 'both':
            return (self.source_block.id, self.target_block.id)
        else:
            raise ValueError(f"Unknown usage category: {usage}")

    def check_prerequisites(self) -> dict:
        """
        Checks if the prerequisites for the action are met.

        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
        :return: A dictionary indicating whether the prerequisites are met and the details of each prerequisite.
        """
        return self.prerequisites(self.source_block, self.target_block)

    def check_consequences(self) -> dict:
        """
        Applies the consequences of the action.

        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
        :return: A dictionary indicating the effects of the action and the details of each consequence.
        """
        return self.consequences(self.source_block, self.target_block)
    
    def force_consequences(self) -> dict:
        """
        Applies the consequences of the action without checking the prerequisites.

        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
        :return: A dictionary indicating the effects of the action and the details of each consequence.
        """
        return self.consequences.force_true(self.source_block, self.target_block)

    def __repr__(self):
        return f"Action(name={self.name}, prerequisites={self.prerequisites}, consequences={self.consequences}, source_block={self.source_block}, target_block={self.target_block})"
