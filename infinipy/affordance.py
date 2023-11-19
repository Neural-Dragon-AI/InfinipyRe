from typing import Callable, List, Tuple, Union, Optional
from infinipy.stateblock import StateBlock
from infinipy.statement import Statement, CompositeStatement, RelationalStatement, CompositeRelationalStatement
from infinipy.transformer import Transformer, CompositeTransformer, RelationalTransformer,CompositeRelationalTransformer

class Affordance:
    def __init__(
        self, 
        name: str, 
        prerequisites: List[Tuple[Union[Statement, RelationalStatement, CompositeStatement, CompositeRelationalStatement], str]], 
        consequences: List[Tuple[Union[Transformer, RelationalTransformer, CompositeTransformer,CompositeRelationalTransformer], str]]
    ):
        """
        Initializes the Affordance with prerequisites and consequences.

        :param name: The name of the affordance.
        :param prerequisites: A list where each item is a tuple:
                              - (Statement/RelationalStatement/CompositeStatement/CompositeRelationalStatement, 'source'/'target'): 
                                Condition and directionality.
        :param consequences: A list of tuples, each containing a Transformer or RelationalTransformer and a string 
                             ('source' or 'target') indicating which StateBlock the transformer should be applied to.
        """
        self.name = name
        self.prerequisites = prerequisites
        self.consequences = consequences

    def is_applicable(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> bool:
        """
        Checks if the affordance is applicable, considering both the source and target StateBlocks.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action. If None, the source_block is used as target.
        :return: True if all prerequisites are met, False otherwise.
        """
        if target_block is None:
            target_block = source_block

        for prerequisite, directionality in self.prerequisites:
            primary_block, secondary_block = (source_block, target_block) if directionality == 'source' else (target_block, source_block)

            if isinstance(prerequisite, (Statement, CompositeStatement)):
                if not prerequisite(primary_block):
                    return False
            elif isinstance(prerequisite, (RelationalStatement, CompositeRelationalStatement)):
                if not prerequisite(primary_block, secondary_block):
                    return False
            else:
                raise ValueError("Invalid prerequisite type", type(prerequisite))

        return True

    def apply(self, source_block: StateBlock, target_block: Optional[StateBlock] = None):
        """
        Applies the consequences to the specified StateBlocks if the affordance is applicable.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action. If None, use source_block as target.
        """
        if self.is_applicable(source_block, target_block):
            if target_block is None:
                target_block = source_block

            for consequence, directionality in self.consequences:
                primary_block, secondary_block = (source_block, target_block) if directionality == 'source' else (target_block, source_block)
                

                if isinstance(consequence, RelationalTransformer) or isinstance(consequence, CompositeRelationalTransformer):
                    # Apply RelationalTransformer to both source and target
                    consequence.apply(primary_block, secondary_block)
                elif isinstance(consequence, Transformer) or isinstance(consequence, CompositeTransformer):
                    # Apply Transformer to the primary block
                    consequence.apply(primary_block)

    def __call__(self, source_block: StateBlock, target_block: Optional[StateBlock] = None):
        """
        Allows the instance to be called as a function, which internally calls the apply method.
        """
        self.apply(source_block, target_block)
