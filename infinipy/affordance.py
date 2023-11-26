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
        Initializes the Affordance with prerequisites and consequences.

        :param name: The name of the affordance.
        :param prerequisites: A list where each item is a tuple:
                              - (Statement/RelationalStatement/CompositeStatement/CompositeRelationalStatement, 'source'/'target'): 
                                Condition and directionality.
        :param transformations: A list of tuples, each containing a Transformer or RelationalTransformer and a string 
                             ('source' or 'target') indicating which StateBlock the transformer should be applied to.
        """
        self.name = name
        self.prerequisites = prerequisites
        self.transformations = transformations

    def is_applicable(self, source_block: StateBlock, target_block: Optional[StateBlock] = None , verbose = False) -> bool:
        """
        Checks if the affordance is applicable, considering both the source and target StateBlocks.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action. If None, the source_block is used as target.
        :return: True if all prerequisites are met, False otherwise.
        """

        results = []
        strings_out = []
        for prerequisite in self.prerequisites:
            result,str_out = prerequisite.apply(source_block, target_block)
            results.append(result)
            strings_out.append(str_out)
        #check if any of the result is false and return false
        if not all(results):
            if verbose:
                print("Affordance {} is not applicable, because prerequisite {} is false".format(self.name, strings_out[results.index(False)]))
            return False
        else:
            if verbose:
                print("Affordance {} is applicable".format(self.name))
      
        return True

    def apply(self, source_block: StateBlock, target_block: Optional[StateBlock] = None):
        """
        Applies the consequences to the specified StateBlocks if the affordance is applicable.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action. If None, use source_block as target.
        """
        if self.is_applicable(source_block, target_block):
            for transformer in self.transformations:
                transformer.apply(source_block, target_block)
    
    def consequence_statements(self, source_block: StateBlock, target_block: Optional[StateBlock] = None):
        """
        Applies the consequences to the specified StateBlocks if the affordance is applicable.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action. If None, use source_block as target.
        """
        results = []
        strings_out = []
        for transformer in self.transformations:
            res_list, str_out_list = transformer.apply_consequences(source_block, target_block)
            #add to the list
            results.extend(res_list)
            strings_out.extend(str_out_list)
        return results, strings_out

            

    def __call__(self, source_block: StateBlock, target_block: Optional[StateBlock] = None):
        """
        Allows the instance to be called as a function, which internally calls the apply method.
        """
        self.apply(source_block, target_block)
