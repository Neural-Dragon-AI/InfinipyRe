from typing import Callable, List, Optional, Tuple, Union
from infinipy.stateblock import StateBlock
from infinipy.statement import Statement, CompositeStatement



class Transformer:
    def __init__(self, name: str, 
                 transformation: Callable[[StateBlock, Optional[StateBlock]], None],
                 consequences: Optional[CompositeStatement] = None):
        self.name = name
        self.transformation = transformation
        self.consequences = consequences

    def apply(self, source_block: StateBlock, target_block: Optional[StateBlock] = None, evaluate: bool = False):
        """
        Applies the transformation to the target StateBlock based on the source StateBlock.
        Optionally evaluates the consequences of the transformation.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        :param evaluate: If True, checks the consequences of the transformation.
        """
        if target_block is None:
            self.transformation(source_block)
        else:
            self.transformation(source_block, target_block)

        if evaluate:
            self.apply_consequences(source_block, target_block)

    def apply_consequences(self, source_block: StateBlock, target_block: Optional[StateBlock] = None):
        """
        Applies and evaluates the consequences of the transformation.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        """
        if self.consequences:
            result = self.consequences(source_block, target_block)
            if not result['result']:
                raise ValueError(f"Transformation consequences did not meet the expected outcome. for transformer {self.name}")
        else:
            raise NotImplementedError(f"No consequences defined for this transformer. {self.name}")


    def force_consequence_true(self, source_block: StateBlock, target_block: Optional[StateBlock] = None):
        """
        Forces the consequences of the transformation to be true.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        """
        if self.consequences:
            return self.consequences.force_true(source_block, target_block)
        else:
            raise NotImplementedError(f"No consequences defined for this transformer. {self.name}")

    def force_consequence_false(self, source_block: StateBlock, target_block: Optional[StateBlock] = None):
        """
        Forces the consequences of the transformation to be false.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        """
        if self.consequences:
            return self.consequences.force_false(source_block, target_block)
        else:
            raise NotImplementedError(f"No consequences defined for this transformer {self.name}")

    def __call__(self, source_block: StateBlock, target_block: Optional[StateBlock]=None):
        self.apply(source_block, target_block)


class CompositeTransformer:
    def __init__(self, transformers: List[Tuple[Transformer, str]]):
        #derive name from transformers names
        self.name = f"CompositeTransformer({', '.join([transformer.name for transformer, _ in transformers])})"
        self.transformers = transformers

    def apply(self, source_block: StateBlock, target_block: StateBlock, local_evaluate: bool = False, global_evaluate: bool = False):
        """
        Applies the sequence of transformations to the source and target StateBlocks.
        Optionally evaluates the consequences of each transformation locally and/or globally.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        :param local_evaluate: If True, checks the consequences of each transformation immediately after its application.
        :param global_evaluate: If True, checks the global consequences after all transformations are applied.
        """
        for transformer, usage in self.transformers:
            if usage == "source":
                transformer.apply(source_block, evaluate=local_evaluate)
            elif usage == "target":
                transformer.apply(target_block, evaluate=local_evaluate)
            elif usage == "both":
                transformer.apply(source_block, target_block, evaluate=local_evaluate)

        if global_evaluate:
            # Global consequences evaluation
            global_results = self.apply_consequences(source_block, target_block)
            if not global_results['result']:
                raise ValueError(f"Transformation consequences did not meet the expected outcome for composite {self.name}")
            # Optionally, you can process global_results or raise an exception if any consequence is not met

    def apply_consequences(self, source_block: StateBlock, target_block: StateBlock):
        """
        Applies and evaluates the consequences of the transformations in the composite.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        """
        results = []
        for transformer, _ in self.transformers:
            result = transformer.apply_consequences(source_block, target_block)
            results.append(result)
        return results
        #check if all consequences are met
        
    def force_consequence_true(self, source_block: StateBlock, target_block: StateBlock):
        """
        Forces the consequences of all transformations in the composite to be true.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        """
        results = []
        for transformer, _ in self.transformers:
            result = transformer.force_consequence_true(source_block, target_block)
            results.append(result)
        return results

    def force_consequence_false(self, source_block: StateBlock, target_block: StateBlock):
        """
        Forces the consequences of all transformations in the composite to be false.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        """
        results = []
        for transformer, _ in self.transformers:
            result = transformer.force_consequence_false(source_block, target_block)
            results.append(result)
        return results

    def __call__(self, source_block: StateBlock, target_block: Optional[StateBlock] = None):
        self.apply(source_block, target_block)

