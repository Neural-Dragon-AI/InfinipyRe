from typing import Callable, List
from stateblock import StateBlock

class Transformer:
    def __init__(self, name: str, transformation: Callable[[StateBlock], None]):
        """
        Initializes the Transformer with a specific transformation function.

        :param name: The name of the transformer.
        :param transformation: A callable that takes a StateBlock and modifies it.
        """
        self.name = name
        self.transformation = transformation

    def apply(self, state_block: StateBlock):
        """
        Applies the transformation to the StateBlock.

        :param state_block: A StateBlock instance representing the state of an entity.
        """
        self.transformation(state_block)

    def __call__(self, state_block: StateBlock):
        """
        Allows the instance to be called as a function, which internally calls the apply method.
        """
        self.apply(state_block)


class CompositeTransformer:
    def __init__(self, transformers: List[Transformer]):
        """
        Initializes the CompositeTransformer with a list of Transformer instances.

        :param transformers: A list of Transformer instances.
        """
        self.transformers = transformers

    def apply(self, state_block: StateBlock):
        """
        Applies the sequence of transformations to the StateBlock.

        :param state_block: A StateBlock instance representing the state of an entity.
        """
        for transformer in self.transformers:
            transformer.apply(state_block)

    def __call__(self, state_block: StateBlock):
        """
        Allows the instance to be called as a function, which internally calls the apply method.
        """
        self.apply(state_block)

class RelationalTransformer:
    def __init__(self, name: str, transformation: Callable[[StateBlock, StateBlock], None]):
        """
        Initializes the RelationalTransformer with a specific transformation function.

        :param name: The name of the transformer.
        :param transformation: A callable that takes two StateBlock instances (source and target) and modifies the target.
        """
        self.name = name
        self.transformation = transformation

    def apply(self, source_block: StateBlock, target_block: StateBlock):
        """
        Applies the transformation to the target StateBlock based on the source StateBlock.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        """
        self.transformation(source_block, target_block)

    def __call__(self, source_block: StateBlock, target_block: StateBlock):
        """
        Allows the instance to be called as a function, which internally calls the apply method.
        """
        self.apply(source_block, target_block)
