from typing import Callable, List, Tuple, Union, Optional
from infinipy.stateblock import StateBlock
from infinipy.statement import Statement, CompositeStatement
from infinipy.transformer import Transformer, CompositeTransformer

class Affordance:
    def __init__(
        self, 
        name: str, 
        prerequisites: List[CompositeStatement], 
        transformations: List[CompositeTransformer]
    ):
        """
        Initializes the Affordance with prerequisites and transformations.

        :param name: The name of the affordance.
        :param prerequisites: A list of CompositeStatement objects representing the conditions that must be met for the affordance to be applicable.
        :param transformations: A list of CompositeTransformer objects representing the transformations to be applied if the affordance is applicable.
        """
        self.name = name
        self.prerequisites = prerequisites
        self.transformations = transformations

    def is_applicable(self, source_block: StateBlock, target_block: Optional[StateBlock] = None, verbose=False) -> bool:
        """
        Checks if the affordance is applicable, considering both the source and target StateBlocks.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action, if any.
        :param verbose: If True, provides detailed output regarding the applicability check.
        :return: True if all prerequisites are met, False otherwise.
        """
        for prerequisite in self.prerequisites:
            result = prerequisite(source_block, target_block)['result']
            if not result:
                if verbose:
                    print(f"Affordance {self.name} is not applicable due to failed prerequisite.")
                return False
        if verbose:
            print(f"Affordance {self.name} is applicable.")
        return True
    
    def why_not_applicable(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> List[str]:
        """ explain why the affordance is not applicable """
        reasons = []
        for prerequisite in self.prerequisites:
            result = prerequisite(source_block, target_block)['result']
            if not result:
                reasons.append((prerequisite.name,result))
        return reasons

    def apply(self, source_block: StateBlock, target_block: Optional[StateBlock] = None, local_evaluate=False, global_evaluate=False):
        """
        Applies the transformations to the specified StateBlocks if the affordance is applicable. 
        Optionally evaluates the consequences of each transformation locally and/or globally.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action, if any.
        :param local_evaluate: If True, evaluates the consequences of each transformation immediately after its application.
        :param global_evaluate: If True, evaluates the global consequences after all transformations are applied.
        """
        if self.is_applicable(source_block, target_block):
            for transformer in self.transformations:
                transformer.apply(source_block, target_block, local_evaluate=local_evaluate, global_evaluate=global_evaluate)
        if global_evaluate:
            global_results = self.evaluate_global_consequences(source_block, target_block)
            if not global_results['result']:
                raise ValueError(f"Global consequences did not meet the expected outcome. for affordance {self.name}")

    def consequence_statements(self, source_block: StateBlock, target_block: Optional[StateBlock] = None):
        """
        Gathers and returns the consequences of the transformations applied by the affordance.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action, if any.
        :return: A list of results representing the consequences of each applied transformation.
        """
        results = []
        for transformer in self.transformations:
            result = transformer.apply_consequences(source_block, target_block)
            results.append(result)
        return results

    def force_consequence_true(self, source_block: StateBlock, target_block: Optional[StateBlock] = None):
        """
        Forces the consequences of all transformations in the affordance to be true.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action, if any.
        :return: A list of results representing the forced true consequences of each applied transformation.
        """
        results = []
        for transformer in self.transformations:
            result = transformer.force_consequence_true(source_block, target_block)
            results.append(result)
        return results

    def force_consequence_false(self, source_block: StateBlock, target_block: Optional[StateBlock] = None):
        """
        Forces the consequences of all transformations in the affordance to be false.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action, if any.
        :return: A list of results representing the forced false consequences of each applied transformation.
        """
        results = []
        for transformer in self.transformations:
            result = transformer.force_consequence_false(source_block, target_block)
            results.append(result)
        return results

    def __call__(self, source_block: StateBlock, target_block: Optional[StateBlock] = None):
        """
        Allows the instance to be called as a function, which internally calls the apply method.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action, if any.
        """
        self.apply(source_block, target_block)
