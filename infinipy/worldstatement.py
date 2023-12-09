from typing import List, Tuple, Optional
from infinipy.stateblock import StateBlock
from infinipy.statement import CompositeStatement

from typing import List, Tuple, Optional
from infinipy.stateblock import StateBlock
from infinipy.statement import CompositeStatement

class WorldStatement:
    def __init__(self, statements: List[Tuple[CompositeStatement, Optional[str], Optional[str]]]):
        """
        Initializes a WorldStatement with a list of CompositeStatements and their source and target StateBlocks.

        :param statements: A list of tuples, each containing a CompositeStatement, a source StateBlock, and an optional target StateBlock.
        """
        self.statements = statements
        self.conditions = self.categorize_statements()

    def categorize_statements(self) -> dict:
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

    def _derive_key(self, statement, source_id, target_id):
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

    def falsifies(self, other: 'WorldStatement') -> bool:
        for key in self.conditions.keys():
            if key in other.conditions:
                if self.conditions[key].falsifies(other.conditions[key]):
                    return True
        return False

    def is_falsified_by(self, other: 'WorldStatement') -> bool:
        return other.falsifies(self)

    def validates(self, other: 'WorldStatement') -> bool:
        for key in self.conditions.keys():
            if key in other.conditions:
                if self.conditions[key].validates(other.conditions[key]):
                    return True
        return False

    def is_validated_by(self, other: 'WorldStatement') -> bool:
        return other.validates(self)
    
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
    