from stateblock import StateBlock
from statement import Statement, CompositeStatement, RelationalStatement, CompositeRelationalStatement
from transformer import Transformer, CompositeTransformer, RelationalTransformer
from typing import List, Tuple, Union, Callable

class Affordance:
    def __init__(
        self, 
        name: str, 
        prerequisites: List[Tuple[Union[CompositeStatement, CompositeRelationalStatement], str]], 
        consequences: List[Tuple[Transformer, str]]
    ):
        """
        Initializes the Affordance with prerequisites and consequences.

        :param name: The name of the affordance.
        :param prerequisites: A list where each item is a tuple:
                              - (CompositeStatement/CompositeRelationalStatement, 'source'/'target'): 
                                Condition and directionality.
        :param consequences: A list of tuples, each containing a Transformer and a string ('source' or 'target') 
                             indicating which StateBlock the transformer should be applied to.
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
        for prerequisite, directionality in self.prerequisites:
            primary_block, secondary_block = (source_block, target_block) if directionality == 'source' else (target_block, source_block)
            
            if isinstance(prerequisite, CompositeStatement):
                if not prerequisite(primary_block):
                    return False
            elif isinstance(prerequisite, CompositeRelationalStatement):
                if not prerequisite(primary_block, secondary_block):
                    return False
            else:
                raise ValueError("Invalid prerequisite type",type(prerequisite))

        return True

    def apply(self, source_block: StateBlock, target_block: StateBlock):
        """
        Applies the consequences to the specified StateBlocks if the affordance is applicable.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        """
        if self.is_applicable(source_block, target_block):
            for consequence, directionality in self.consequences:
                if isinstance(consequence, Transformer):
                    block_to_transform = source_block if directionality == 'source' else target_block
                    consequence(block_to_transform)
                elif isinstance(consequence, RelationalTransformer):
                    if directionality == 'source':
                        consequence(source_block, target_block)
                    elif directionality == 'target':
                        consequence(target_block, source_block)
                    else:
                        raise ValueError("Invalid directionality", directionality)
                else:
                    raise ValueError("Invalid transformer type", type(consequence))