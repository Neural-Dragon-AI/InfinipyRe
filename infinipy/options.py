from infinipy.actions import Action
from collections import defaultdict
from typing import Tuple, Optional
from infinipy.statement import CompositeStatement

class Option:
    def __init__(self, starting_dict: Optional[dict] = None):
        """
        Initializes the Option class with empty global prerequisites and consequences.
        These are managed as dictionaries indexed by (source_id, target_id) tuples.
        """
        self.actions = []
        self.global_prerequisites = defaultdict(CompositeStatement) #if starting_dict is None else starting_dict
        self.global_consequences = defaultdict(CompositeStatement) if starting_dict is None else starting_dict

    def append(self, action: Action):
        """
        Appends an action and updates the global prerequisites and consequences.

        :param action: The action to be appended.
        """
        self.actions.append(action)
        self.update_forward(action)

    def prepend(self, action: Action):
        """
        Prepends an action and updates the global prerequisites and consequences.

        :param action: The action to be prepended.
        """
        self.actions.insert(0, action)
        self.update_backward(action)

    def update_forward(self, action: Action):
        """
        Updates the global prerequisites and consequences in a forward direction for a single action.

        :param action: The action to process.
        """
        #first we check that the action does not have conflicting prerequisite with the 
        #current global consequences
        
        for category in ['source', 'target', 'both']:
            key = self._get_key(action, category)
            current_pre = action.pre_dict.get(key, None)
            current_con = action.con_dict.get(key, None)

            global_con = self.global_consequences.get(key,CompositeStatement([]))
            global_pre = self.global_prerequisites.get(key,CompositeStatement([]))
            #check if there are conflicts between the current prerequisites and the global consequences
            if current_pre:
                # print("current_pre",current_pre.name)
                has_conflict,conflicts = global_con.is_conflict(current_pre)
                if has_conflict:
                    return False
                #remove the prerequisite already satisfied by the global consequences
                current_pre_clean = current_pre.remove_intersection(global_con)
                #updates the global prerequisite with the current prerequisites using merge
                # the merge shouldbe safe because we checked for conflicts ex-ante
                
                self.global_prerequisites[key] = global_pre.merge(current_pre_clean)
                # print("global_pre",self.global_prerequisites[key])
            #now update the global consequences with the current consequences with merge_force
            if current_con:
                # print("current_con",current_con.name)
                self.global_consequences[key] = global_con.force_merge(current_con,force_direction="right")
                # print(self.global_consequences[key])
        return True

        

    def update_backward(self, action: Action):
        """
        Updates the global prerequisites and consequences in a backward direction for a single action.

        :param action: The action to process.
        """
        for category in ['source', 'target', 'both']:
            key = self._get_key(action, category)
            current_pre = action.pre_dict.get(key, None)
            current_con = action.con_dict.get(key, None)

            global_con = self.global_consequences.get(key,CompositeStatement([]))
            global_pre = self.global_prerequisites.get(key,CompositeStatement([]))

            #first check that current conseuqences do not conflict with global prerequisites
            if current_con:
                has_conflict,conflicts = global_pre.is_conflict(current_con)
                if has_conflict:
                    return False
              
                #update the global consequences with the current consequences 
                # giving precedence to the global consequences
                self.global_consequences[key] = global_con.force_merge(current_con,force_direction="left")
             
                #remove from the global prereq the prereq already satisfied by the current consequences
                global_pre_clean = global_pre.remove_intersection(current_con)
                # add to the global prereq the current prereq with precedence to the global prereq
                # this way we overwrite current_prereq which are conflicting with the global prereq
                # but are solved by the current consequences, non solved conflcits are catched above
                # by the is_conflict check
                if current_pre:
                    self.global_prerequisites[key] = global_pre_clean.force_merge(current_pre,force_direction="left")
        return True

    def _get_key(self, action: Action, category: str):
        """
        Derives the appropriate key based on the category.

        :param action: The action being processed.
        :param category: The category ('source', 'target', or 'both').
        :return: A tuple representing the key.
        """
        if category == 'both':
            return (action.source_block.id, action.target_block.id)
        elif category == 'source':
            return (action.source_block.id, None)
        elif category == 'target':
            return (None, action.target_block.id)
        else:
            raise ValueError(f"Unknown category: {category}")

    def __repr__(self):
        return f"Option(actions={self.actions})"
