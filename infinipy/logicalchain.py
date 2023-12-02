from infinipy.statement import Statement, CompositeStatement
from typing import List, Tuple, Set, Dict, Optional

def join_prerequisite_with_consequence(prerequisite: CompositeStatement, consequence: CompositeStatement) -> CompositeStatement:
    """
    Joins a prerequisite CompositeStatement with a consequence CompositeStatement.

    :param prerequisite: The CompositeStatement representing the prerequisites.
    :param consequence: The CompositeStatement representing the consequences.
    :return: A new CompositeStatement representing the state after applying the consequence to the prerequisite.
    """
    # Extract individual statements from both prerequisite and consequence
    prerequisite_statements = {statement for condition in prerequisite.conditions for statement in condition}
    consequence_statements = {statement for condition in consequence.conditions for statement in condition}

    # Create a set to store the joined statements
    joined_statements = set()

    # Add all consequence statements to the joined set
    joined_statements.update(consequence_statements)

    # Add statements from the prerequisite that aren't mentioned in the consequence
    for statement in prerequisite_statements:
        if statement not in consequence_statements:
            joined_statements.add(statement)

    return CompositeStatement(list(joined_statements))




class LogicalChain:
    def __init__(self, sequence: List[Tuple[CompositeStatement, CompositeStatement]]):
        """
        Initializes the LogicalChain with a sequence of actions.

        :param sequence: A list of tuples, each containing a prerequisite (CompositeStatement) and a consequence (CompositeStatement).
        """
        self.sequence = sequence

    def process_prerequisite_and_check_conflicts(self, current_consequence: CompositeStatement, next_prerequisite: CompositeStatement) -> Tuple[CompositeStatement, List[str]]:
        """
        Processes the next prerequisite with the current consequence, checking for conflicts and identifying unsatisfied prerequisites.

        :param current_consequence: The current consequence as a CompositeStatement.
        :param next_prerequisite: The next prerequisite as a CompositeStatement.
        :return: A tuple containing a CompositeStatement of unsatisfied prerequisites and a list of conflict descriptions.
        """
        conflicts = []
        unsatisfied = []

        for statement_prerequisite, condition_prerequisite, usage_prerequisite in next_prerequisite.conditions:
            conflict_found = False
            for statement_consequence, condition_consequence, usage_consequence in current_consequence.conditions:
                if (statement_consequence == statement_prerequisite and usage_consequence == usage_prerequisite):
                    if condition_consequence != condition_prerequisite:
                        conflicts.append(f"Conflict found in '{statement_consequence.name}' with usage '{usage_consequence}' - Consequence: '{condition_consequence}', Prerequisite: '{condition_prerequisite}'")
                        conflict_found = True
                        break
            if not conflict_found and (statement_prerequisite, condition_prerequisite, usage_prerequisite) not in current_consequence.conditions:
                unsatisfied.append((statement_prerequisite, condition_prerequisite, usage_prerequisite))

        return CompositeStatement(unsatisfied), conflicts

    def process_chain(self) -> Tuple[List[CompositeStatement], List[CompositeStatement]]:
        """
        Processes the sequence of actions to determine the evolving global prerequisites and consequences.

        :return: A tuple of two lists, each list containing CompositeStatements. The first list represents the 
                 global prerequisites at each step, and the second list represents the state after applying each 
                 consequence, propagating the state forward.
        """
        if not self.sequence:
            raise ValueError("Sequence is empty")

        global_prerequisites = []
        global_consequences = []

        global_state = self.sequence[0][0]  # Initialize with the first prerequisite
        global_prerequisites.append(global_state)

        for i in range(len(self.sequence)):
            current_prerequisite, current_consequence = self.sequence[i]

            # Apply the current consequence to the global state
            global_state = join_prerequisite_with_consequence(global_state, current_consequence)
            global_consequences.append(global_state)

            # Prepare for the next iteration
            if i + 1 < len(self.sequence):
                next_prerequisite = self.sequence[i + 1][0]

                # Process the prerequisite and check for conflicts
                unsatisfied_prerequisites, conflicts = self.process_prerequisite_and_check_conflicts(global_state, next_prerequisite)
                if conflicts:
                    conflict_str = ', '.join(conflicts)
                    raise ValueError(f"Conflicts detected: {conflict_str}")

                global_prerequisites.append(unsatisfied_prerequisites)

        return global_prerequisites, global_consequences


