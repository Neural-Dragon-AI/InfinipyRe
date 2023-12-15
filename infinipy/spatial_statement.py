from infinipy.statement import Statement, CompositeStatement
from typing import Dict, List, Tuple, Optional, Union
from infinipy.stateblock import StateBlock

class SpatialGroupStatement:
    def __init__(self, composite_statement: CompositeStatement, condition: str, position: Tuple[int, int]):
        """
        Initializes the SpatialGroupStatement with a composite statement and a condition.

        :param composite_statement: The CompositeStatement to apply.
        :param condition: The condition to evaluate ('any', 'all', 'any_not', 'all_not').
        :param position: The spatial position defining the group.
        """
        self.composite_statement = composite_statement
        self.condition = condition.lower()
        self.position = position
        self.name = f"Spatial_{self._condition_name()}_{composite_statement.name}"

    def _condition_name(self) -> str:
        """ Translates the condition into a readable format for the name. """
        condition_map = {
            'any': 'Any',
            'all': 'All',
            'any_not': 'AnyNot',
            'all_not': 'AllNot'
        }
        return condition_map.get(self.condition, 'Unknown')

    def apply(self, entity_pairs: List[Tuple[StateBlock, Union[StateBlock, None]]]) -> dict:
        """
        Applies the composite statement to each entity pair and evaluates the overall condition.

        :param entity_pairs: List of tuples of source and optional target StateBlocks.
        :return: A dictionary with the result and details of the evaluation.
        """
        results = [self.composite_statement(source, target) for source, target in entity_pairs]
        overall_result = self._evaluate_condition(results)

        return {
            "name": self.name,
            "overall_result": overall_result,
            "individual_results": results,
            "position": self.position
        }

    def _evaluate_condition(self, results: List[dict]) -> bool:
        """ Evaluates the overall condition based on the individual results. """
        if self.condition == 'any':
            return any(result['result'] for result in results)
        elif self.condition == 'all':
            return all(result['result'] for result in results)
        elif self.condition == 'any_not':
            return any(not result['result'] for result in results)
        elif self.condition == 'all_not':
            return all(not result['result'] for result in results)
        else:
            raise ValueError(f"Invalid condition: {self.condition}")

    def __str__(self):
        """ String representation of the SpatialGroupStatement. """
        return f"SpatialGroupStatement(name={self.name}, position={self.position}, condition={self.condition})"
