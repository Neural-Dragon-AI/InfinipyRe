from infinipy.actions import Action
from collections import defaultdict
from typing import Tuple, Optional
from infinipy.statement import CompositeStatement
from infinipy.worldstatement import WorldStatement

class Option:
    def __init__(self, starting_consequences: Optional[WorldStatement] = None,starting_prerequisites:  Optional[WorldStatement] = None, clamp_starting_consequences: bool = False):
        """
        Initializes the Option class from WorldStatements with empty global prerequisites and consequences.
        If starting_world is not None, it is used as the starting point for the global prerequisites.
        This implies that actions that are appended to the sequence must have prerequisites that are not falsified by the starting_world.
        If ending_world is not None, it is used as the starting point for the global consequences and only actions that lead to compatible consequences can be appended.
        These are managed as WorldStatements which contain dictionaries indexed by (source_id, target_id) tuples. and Tuples with Comp
        """
        self.actions = []
        self.clamp_starting_consequences = clamp_starting_consequences
        self.global_consequences = starting_consequences if starting_consequences is not None else WorldStatement([])
        #global prerequisites are initialized with the  starting_prerequiistes if non None 
        starting_prerequisites = starting_consequences if starting_prerequisites is None and starting_consequences is not None else starting_prerequisites
        self.global_prerequisites = starting_prerequisites if starting_prerequisites is not None else WorldStatement([])
        

    def print_conditions(self):
        """
        Prints nicely formatted conditions using f-strings
        """
        print(f"Global Prerequisites:")
        self.global_prerequisites.print_conditions()
        print(f"Global Consequences:")
        self.global_consequences.print_conditions()

    def append(self, action: Action,allows_extra_pre: bool = False):
        """
        Appends an action and updates the global prerequisites and consequences.

        :param action: The action to be appended.
        """
        
        if self.update_forward(action,allows_extra_pre):
            self.actions.append(action)
            return True
        return False

    def prepend(self, action: Action,must_satisfy_pre: bool = False):
        """
        Prepends an action and updates the global prerequisites and consequences.

        :param action: The action to be prepended.
        """
        if self.update_backward(action,must_satisfy_pre):
            self.actions.insert(0, action)
            return True
        return False

    def update_forward(self, action: Action, allows_extra_pre: bool = False):
        """
        Updates the global prerequisites and consequences in a forward direction for a single action.

        :param action: The action to process.
        """
        
        #extract the action pre and consequence and convert to WorldStatement
        action_pre = WorldStatement.from_dict(action.pre_dict)
        action_con = WorldStatement.from_dict(action.con_dict)
        #first we check that the action does not have conflicting prerequisite with the current consquences
        # that is that the consequense not falsify the prereq
        #in that case it is not possible to append the action
        if self.global_consequences.falsifies(action_pre):
            print(f"The action {action.name} cannot be appended because the global consequences falsify the action prereq")
            return False
        #now we check if the action adds additional prereq that are not already in the global prereq
        # and if allows_extra_pre is False we return False
        if not self.global_consequences.validates(action_pre):
            #some of the prereq are not satisfied by the global consequences
            unsatisfied_pre = action_pre.remove_intersection(self.global_consequences)
            if not allows_extra_pre:
                print(f"The action {action.name} cannot be apppended because it adds additional prereq that are not satisfied by the global consequences and allows_extra_pre is False")
                print("Unsatisfied prereq:")
                unsatisfied_pre.print_conditions()
                return False

            #we update the global prereq with the unsatisfied prereq
            self.global_prerequisites = self.global_prerequisites.merge(unsatisfied_pre)

        #we update the global consequences with the action consequences with merge_force
        self.global_consequences = self.global_consequences.force_merge(action_con,force_direction="right")
        return True

        

    def update_backward(self, action: Action, must_satisfy_pre: bool = False):
        """
        Updates the global prerequisites and consequences in a backward direction for a single action.

        :param action: The action to process.
        """
        #extract the action pre and consequence and convert to WorldStatement
        action_pre = WorldStatement.from_dict(action.pre_dict)
        action_con = WorldStatement.from_dict(action.con_dict)

        #case 1 the action consequences are not conflicting with the current state of the world
        # the current state of the world is the global_prerequisite if actions are already present
        # otherwise it is the global_consequences if no actions are present 
        # if there is no consequence and no action it is an empty WorldStatement
        global_pre = self.global_prerequisites

        if action_con.falsifies(global_pre):
            print(f"The action {action.name} cannot be prepended because the action consequences falsify the global prereq")
            return False
        
        
        #now we check if the action consequence fully satisfies the global prereq 
        #or some prereq of the previous state are not satisfied by the action consequence
        #in that case we need to update the global prereq or return false based on must_satisfy_pre
        if not action_con.validates(global_pre):
            #some of the prereq are not satisfied by the global consequences
            unsatisfied_pre = global_pre.remove_intersection(action_con)
            if must_satisfy_pre:
                print(f"The action {action.name} cannot be prepended because the action consequences do not fully satisfy the global prereq and must_satisfy_pre is True")
                print("Unsatisfied prereq:")
                unsatisfied_pre.print_conditions()
                return False

            #we update the global pre by removing the prereq already satisfied by the action consequences
            # we do it by combining the unsatisfied_pre with the new action pre, this should be a safe operation
            # because the pre-req of the action that could conflict with the global prereq are either
            # non conflicting any more because the consequence removed the previously conflicting prereq
            # or detected as conflicting in action_con.validates(global_pre) and therefore not present in unsatisfied_pre
            # tldr if a prereq was conflicting only before the action consequence it means that the actions consequence that changed its values is now binding and therefore the prereq is not conflicting any more because it does not exist
            # if the prereq was conflicting before the action consequence and is still conflicting after the action consequence due to transitivyty of the prereq than it would have been detected as conflicting in action_con.validates(global_pre) and therefore not present in unsatisfied_pre
            self.global_prerequisites = unsatisfied_pre.merge(action_pre)
        else:
            self.global_prerequisites = action_pre
        #now we update the global consequences with the action consequences with merge_force giving precedence to the global consequences
        # because the future has precedence over the past
        self.global_consequences = self.global_consequences.force_merge(action_con,force_direction="left")
        return True

    def __repr__(self):
        return f"Option(actions={self.actions})"
