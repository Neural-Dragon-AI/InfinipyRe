from typing import Callable, Tuple
from stateblock import StateBlock
from statement import Statement, CompositeStatement
from transformer import Transformer, CompositeTransformer

class Affordance:
    def __init__(self, name: str, prerequisites: list[Tuple[Statement, str]], consequences: list[Transformer]):
        """
        Initializes the Affordance with prerequisites and consequences.

        :param name: The name of the affordance.
        :param prerequisites: A list of tuples, each containing a Statement and a string ('source' or 'target') 
                              indicating to which StateBlock the statement applies.
        :param consequences: A list of Transformers that define the changes to the StateBlock if the affordance is applied.
        """
        self.name = name
        self.prerequisites = prerequisites
        self.consequences = consequences

    def is_applicable(self, source_block: StateBlock, target_block: StateBlock) -> bool:
        """
        Checks if the affordance is applicable, considering both the source and target StateBlocks.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        :return: True if all prerequisites are met, False otherwise.
        """
        for prerequisite, block_type in self.prerequisites:
            if block_type == "source":
                if not prerequisite(source_block):
                    return False
            elif block_type == "target":
                if not prerequisite(target_block):
                    return False
            else:
                raise ValueError(f"Invalid block type: {block_type}")

        return True

    def apply(self, source_block: StateBlock, target_block: StateBlock):
        """
        Applies the consequences to the source and/or target StateBlocks if the affordance is applicable.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        """
        if self.is_applicable(source_block, target_block):
            for consequence in self.consequences:
                consequence(source_block)
                consequence(target_block)
