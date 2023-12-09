from typing import Callable, Tuple, Optional, List, Dict, Set
from infinipy.stateblock import StateBlock
import itertools



class Statement:
    def __init__(self, 
                 name: str, 
                 description: str, 
                 callable: Callable[[StateBlock, Optional[StateBlock]], bool],
                 usage: str = "both",
                 required_attributes: Optional[Dict[str, List[str]]] = None):
        """
        Initializes the Statement with a specific condition involving two StateBlocks.

        :param name: The name of the statement.
        :param description: A brief description of what the condition checks for.
        :param condition: A callable that takes two StateBlock instances and returns a boolean.
        """
        self.base_name = name
        self.name = name+"_"+usage
        self.description = description
        self.callable = callable
        self.usage = usage
        self.source_required = required_attributes.get('source') if required_attributes else None
        self.target_required = required_attributes.get('target') if required_attributes else None

    
    def check_required_attributes(self, source_block: StateBlock, target_block: Optional[StateBlock]) -> bool:
        """
        Checks if the required attributes are present in the source and target StateBlocks. Collect all the missing from boths and returns a boolean and two lists of missing attributes.

        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
       
        """
        source_missing = []
        target_missing = []
        if self.source_required:
            for attribute in self.source_required:
                if not hasattr(source_block, attribute):
                    source_missing.append(attribute)
        if self.target_required:
            for attribute in self.target_required:
                if not hasattr(target_block, attribute):
                    target_missing.append(attribute)
        if len(source_missing)>0 and len(target_missing)>0:
            return False, source_missing, target_missing
        elif len(source_missing)>0:
            return False, source_missing, None
        elif len(target_missing)>0:
            return False, None, target_missing
        return True, None, None

    def create_statement_fstring(self, statement_result:bool,source_block: StateBlock, target_block: Optional[StateBlock]) -> str:
        """
        Creates a string representation of the statement when the condition is met.

        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
        :return: A string representation of the statement when the condition is met.
        """
        if self.usage == "source":
            return f"The statement {self.name} with description {self.description} applied to the source {source_block.name} is {statement_result}."
        elif self.usage == "target":
            return f"The statement {self.name} with description {self.description} applied to the target {target_block.name} is {statement_result}."
        elif self.usage == "both":
            return f"The statement {self.name} with description {self.description} applied to the source {source_block.name} and the target {target_block.name} is {statement_result}."
       
    
    def create_statement_fstring_missing_attributes(self, source_block:StateBlock, target_block:  Optional[StateBlock], source_missing: Optional[List[str]], target_missing: Optional[List[str]]) -> str:
        """
        Creates a string representation of the statement when the condition is not met because of missing attributes.

        :param source_missing: A list of missing attributes in the source StateBlock.
        :param target_missing: A list of missing attributes in the target StateBlock.
        :return: A string representation of the statement when the condition is not met because of missing attributes.
        """
        if source_missing and target_missing:
            return f"The statement {self.name} {self.description} is not met because the source {source_block.name} is missing the attributes {source_missing} and the target {target_block.name} is missing the attributes {target_missing}."
        elif source_missing:
            return f"The statement {self.name} {self.description} is not met because the source {source_block.name} is missing the attributes {source_missing}."
        elif target_missing:
            return f"The statement {self.name} {self.description} is not met because the target {target_block.name} is missing the attributes {target_missing}."
        else:
            raise ValueError(f"Missing attributes but no missing attributes found for statement {self.name}")

    def create_out_dict(self,result,source_block: StateBlock, target_block: Optional[StateBlock] , source_missing: Optional[List[str]], target_missing: Optional[List[str]]):
        """
        Creates a dictionary representation of the statement when the condition is met.

        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
        :param source_missing: A list of missing attributes in the source StateBlock.
        :param target_missing: A list of missing attributes in the target StateBlock.
        :return: A dictionary representation of the statement when the condition is met.
        """
        return {"statement":self.name,"result":result, "usage":self.usage,"source":source_block.name,"target":target_block.name if target_block else None,"stringout":self.create_statement_fstring(result,source_block, target_block),"source_missing":source_missing,"target_missing":target_missing}

    
    def apply(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> (bool, str):
        """
        Applies the condition to the specified source and target StateBlocks.

        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
        :return: True if the condition is met, False otherwise.
        """
        #check stateblock type
        if not isinstance(source_block, StateBlock):
            raise ValueError(f"Source block {source_block} is not a StateBlock.")
        # Check if the required attributes are present in the source and target StateBlocks
        required_attributes_present, source_missing, target_missing = self.check_required_attributes(source_block, target_block)
        if not required_attributes_present:
            return False, self.create_out_dict(False,source_block, target_block, source_missing, target_missing)
        if self.usage == "source":
            statement_result = self.callable(source_block) 
            return statement_result, self.create_out_dict(statement_result,source_block, target_block, source_missing, target_missing)
        elif self.usage == "target" and target_block is not None:
            statement_result = self.callable(target_block) 
            return statement_result, self.create_out_dict(statement_result,source_block, target_block, source_missing, target_missing)
        elif self.usage == "both" and target_block is not None:
            statement_result = self.callable(source_block, target_block)
            return statement_result, self.create_out_dict(statement_result,source_block, target_block, source_missing, target_missing)
        elif self.usage == "both" and target_block is None:
            raise ValueError(f"Target block is None but usage is both for statement {self.name}")
        elif self.usage == "target" and target_block is None:
            raise ValueError(f"Target block is None but usage is target for statement {self.name}")

    
    def force_true(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> (bool, str):
        return True, self.create_out_dict(True,source_block, target_block, None, None)
    
    def force_false(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> (bool, str):
        return False, self.create_out_dict(False,source_block, target_block, None, None)

    def __call__(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> bool:
        """
        Allows the instance to be called as a function, which internally calls the apply method.

        :param source_block: The StateBlock instance representing the source of the action.
        :param target_block: The StateBlock instance representing the target of the action.
        :return: True if the condition is met, False otherwise.
        """
    
        return self.apply(source_block, target_block)
    



    
class CompositeStatement:
    def __init__(self, substatements: List[Tuple[Statement,bool]]):
        """ Initializes the CompositeStatement with a set of unique conditions. """
        # Convert list of conditions to a set to avoid duplicates
        self.substatements = set(substatements)
        self.statements =[x[0] for x in list(substatements)]
        self.conditions = [x[1] for x in list(substatements)]
        self._check_for_conflicts()
        self.name = self._derive_name()

    
    def _derive_name(self):
        """ Derives the name of the CompositeStatement based on its conditions. """
        return f"CompositeStatement({', '.join([f'{statement.name} {cond}' for statement,cond in self.substatements])})"

    def _check_for_conflicts(self):
        """ Checks for logical conflicts within the conditions of the CompositeStatement. """
        category_sets = {
            'source': {'positive': set(), 'negative': set()},
            'target': {'positive': set(), 'negative': set()},
            'both': {'positive': set(), 'negative': set()}
        }

        for sub,cond in self.substatements:
            statement, condition, usage = sub, cond, sub.usage
            sets = category_sets[usage]
            if condition == True:
                self._add_to_set_and_check_conflict(sets['positive'], sets['negative'], statement)
            elif condition == False:
                self._add_to_set_and_check_conflict(sets['negative'], sets['positive'], statement)

    def _add_to_set_and_check_conflict(self, adding_set: set, checking_set: set, statement: Statement):
        """ Adds a statement to the positive set and checks for conflict with the negative set. """
        if statement in checking_set:
            raise ValueError(f"Conflict detected for '{statement.name}' in CompositeStatement.")
        adding_set.add(statement)



    def create_combined_fstring(self, result_strings: List[str]) -> str:
        combined_string = ""
        for i, string in enumerate(result_strings):
            if i > 0:
                operator = 'AND' if self.conditions[i] else 'AND NOT'
                combined_string += f" {operator} "
            combined_string += string
        return combined_string
        

    def apply(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> dict:
        if not self.substatements:
            return {"result": True, "composite_string": "", "sub_statements": []}

        # Process the first condition separately
        first_statement, first_condition = self.statements[0], self.conditions[0]
        first_result, first_result_dict = first_statement(source_block, target_block)
        composite_result = first_result_dict["result"] == first_condition
        sub_statements = [first_result_dict]
        composite_string = [first_result_dict["stringout"]]

        # Iterate over the remaining conditions
        for statement, condition in zip(self.statements[1:],self.conditions[1:]):
            _, next_result_dict = statement(source_block, target_block)
            sub_statements.append(next_result_dict)
            composite_string.append(next_result_dict["stringout"])


            # Evaluate the composite result based on the condition
            if condition == True:
                composite_result = composite_result and next_result_dict["result"]
            elif condition == False:
                composite_result = composite_result and not next_result_dict["result"]
            else:
                raise ValueError(f"Invalid condition: {condition} for statement {statement.name} in composite statement {self.name}")

        return {
            "result": composite_result,
            "name": self.name,
            "composite_string": self.create_combined_fstring(composite_string),
            "sub_statements": sub_statements,
            "conditions": self.conditions,
            "sub_results": [sub["result"] for sub in sub_statements],
        }
    
    def _force_statement(self, source_block: StateBlock, target_block: Optional[StateBlock], desired_result: bool) -> List[Dict]:
        """
        Generates hypothetical results for each statement in the composite to satisfy a desired global result.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        :param desired_result: The desired global result (True or False).
        :return: A list of dictionaries with hypothetical results satisfying the desired result.
        """
        results = []
        for statement, condition in zip(self.statements, self.conditions):
            # Hypothetically determine the result of each statement
            if condition == True:
                statement_result = desired_result
            elif condition ==  False:
                statement_result = not desired_result

            # Create a hypothetical result dictionary
            result_dict = statement.create_out_dict(statement_result, source_block, target_block, None, None)
            results.append(result_dict)

        return results

    def force_true(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> List[Dict]:
        """
        Generates hypothetical results for each statement in the composite to make the global condition true.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        :return: A list of dictionaries representing hypothetical results that make the global condition true.
        """
        return self._force_statement(source_block, target_block, desired_result=True)

    def force_false(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> List[Dict]:
        """
        Generates hypothetical results for each statement in the composite to make the global condition false.

        :param source_block: The StateBlock representing the source of the action.
        :param target_block: The StateBlock representing the target of the action.
        :return: A list of dictionaries representing hypothetical results that make the global condition false.
        """
        return self._force_statement(source_block, target_block, desired_result=False)
    
    def merge(self, other: 'CompositeStatement'):
        """
        Merge the current CompositeStatement with another CompositeStatement, 
        fails if the two CompositeStatements have conflicting conditions.
        """

        joined_sets = self.substatements.union(other.substatements)
        return self.__class__(list(joined_sets))
       
        
    def is_conflict(self, other: 'CompositeStatement') -> Tuple[bool, List[Tuple[Statement, bool]]]:
        """
        Checks if there is a conflict with another CompositeStatement and returns the list of conflicts.
        """
        conflicts = []
        for sub, cond in self.substatements:
            for o_sub, o_cond in other.substatements:
                if sub == o_sub and cond != o_cond:
                    conflicts.append((sub, cond))
        return (len(conflicts) > 0, conflicts)

    def force_merge(self, other: 'CompositeStatement', force_direction: str = "left"):
        """
        Merge with resolution of conflicts based on force_direction. Returns a new CompositeStatement.
        """


        # Check for conflicts and get the list of conflicting statements
        has_conflict, conflicts = self.is_conflict(other)

        # Resolve conflicts based on force_direction
        resolved_substatements = set(self.substatements)
        for conflict in conflicts:
            if force_direction == "left":
                resolved_substatements.add(conflict)
            else:
                resolved_substatements.discard(conflict)
                resolved_substatements.add((conflict[0], not conflict[1]))

        # Add statements from the other CompositeStatement
        for o_sub, o_cond in other.substatements:
            if not any(sub == o_sub for sub, cond in resolved_substatements):
                resolved_substatements.add((o_sub, o_cond))

        # Re-initialize with resolved substatementsin a new CompositeStatement
        return self.__class__(list(resolved_substatements))
    
    def remove_intersection(self, other: 'CompositeStatement'):
        """
        Remove the intersection of two CompositeStatements.
        """
        intersection = self.substatements.intersection(other.substatements)
        new_substatements = self.substatements.difference(intersection)
        return self.__class__(list(new_substatements)) 

    def falsifies(self, other: 'CompositeStatement', value_self=True, value_other=True) -> bool:
        # Logic to check if `self` falsifies `other`
        # Iterate over each statement in self and other and compare
        for self_sub, self_cond in self.substatements:
            for other_sub, other_cond in other.substatements:
                if self_sub == other_sub and self_cond != other_cond:
                    if (value_self and not self_cond) or (value_other and not other_cond):
                        return True
        return False

    def is_falsified_by(self, other: 'CompositeStatement', value_self=True, value_other=True) -> bool:
        # Logic to check if `self` is falsified by `other`
        # This is essentially the reverse of `falsifies`
        return other.falsifies(self, value_other, value_self)

    def validates(self, other: 'CompositeStatement', value_self=True, value_other=True) -> bool:
        # Logic to check if `self` validates `other`
        # Iterate over each statement in self and other and compare
        for self_sub, self_cond in self.substatements:
            for other_sub, other_cond in other.substatements:
                if self_sub == other_sub and self_cond == other_cond:
                    if (value_self and self_cond) and (value_other and other_cond):
                        return True
        return False

    def is_validated_by(self, other: 'CompositeStatement', value_self=True, value_other=True) -> bool:
        # Logic to check if `self` is validated by `other`
        # This is essentially the reverse of `validates`
        return other.validates(self, value_other, value_self) 
        
    @classmethod
    def from_composite_statements(cls, composite_statements: List['CompositeStatement']):
        """
        Class method to initialize a CompositeStatement from a list of other CompositeStatements.
        It extracts individual statements from each CompositeStatement and combines them.

        :param composite_statements: List of CompositeStatement objects.
        :return: A new CompositeStatement consisting of the combined statements.
        """
        combined_conditions = set()
        for composite in composite_statements:
            # Extract individual statements from each composite statement
            combined_conditions= combined_conditions.union(composite.substatements)
            
          
        # Create a new CompositeStatement with the combined conditions
        list_conditions = list(combined_conditions)
        return cls(list_conditions)

    def __call__(self, source_block: StateBlock, target_block: Optional[StateBlock] = None) -> dict:
        return self.apply(source_block, target_block)