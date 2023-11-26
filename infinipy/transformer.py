from typing import Callable, List, Optional, Tuple, Union
from infinipy.stateblock import StateBlock
from infinipy.statement import Statement, CompositeStatement



class Transformer:
    def __init__(self, name: str, 
                 transformation: Callable[[StateBlock, Optional[StateBlock]], None],
                 consequences: Optional[CompositeStatement] = None
                 ):
        """
        Initializes the Transformer with a specific transformation function.

        :param name: The name of the transformer.
        :param transformation: A callable that takes two StateBlock instances (source and target) and modifies the target.
        """
        self.name = name
        self.transformation = transformation
        self.consequences = consequences

    def apply(self, source_block: StateBlock, target_block: Optional[StateBlock] = None):
        """
        Applies the transformation to the target StateBlock based on the source StateBlock.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        """
        if target_block is None:
            return self.transformation(source_block)
        self.transformation(source_block, target_block)

    def apply_consequences(self, source_block: StateBlock, target_block: Optional[StateBlock] = None):
        """
        Applies the consequences of the transformation to the target StateBlock based on the source StateBlock.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        """
        if self.consequences is None:
            raise NotImplementedError("No consequences defined for this transformer.")
        if target_block is None:
            return self.consequences.apply(source_block)
        return self.consequences.apply(source_block, target_block)

    def __call__(self, source_block: StateBlock, target_block: Optional[StateBlock]):
        """
        Allows the instance to be called as a function, which internally calls the apply method.
        """
        self.apply(source_block, target_block)


class CompositeTransformer:
    def __init__(self, transformers: List[Tuple[Transformer,str]]):
        """
        Initializes the CompositeTransformer with a list of Transformer instances.

        :param relational_transformers: A list of Transformer instances and the application method e.g. "source" or "target" or "both".
        """
        self.transformers = transformers

    def apply(self, source_block: StateBlock, target_block: StateBlock):
        """
        Applies the sequence of relational transformations to the source and target StateBlocks.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        """
        for transformer,usage in self.transformers:
            if usage == "source":
                transformer.apply(source_block)
            elif usage == "target":
                transformer.apply(target_block)
            elif usage == "both":
                transformer.apply(source_block, target_block)
    
    def apply_consequences(self, source_block: StateBlock, target_block: StateBlock):
        """
        Applies the sequence of relational transformations to the source and target StateBlocks.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        """
        results = []
        strings_out = []
        for transformer,usage in self.transformers:
            if usage == "source":
                result, string_out = transformer.apply_consequences(source_block)
            elif usage == "target":
                 result, string_out = transformer.apply_consequences(target_block)
            elif usage == "both":
                 result, string_out = transformer.apply_consequences(source_block, target_block)
            results.append(result)
            strings_out.append(string_out)
        return results, strings_out

    def __call__(self, source_block: StateBlock, target_block: StateBlock):
        """
        Allows the instance to be called as a function, which internally calls the apply method.
        """
        self.apply(source_block, target_block)

