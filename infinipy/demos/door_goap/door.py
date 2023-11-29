from infinipy.stateblock import StateBlock
import uuid

from infinipy.statement import Statement,CompositeStatement
from infinipy.transformer import Transformer,CompositeTransformer
from infinipy.affordance import Affordance
from dataclasses import dataclass, field

@dataclass
class Door(StateBlock):
    is_open: bool = False  # Attribute to indicate if the door is open
    is_locked: bool = False  # Attribute to indicate if the door is locked

    def __post_init__(self):
        super().__post_init__()  # Call the post-init of StateBlock
        # Additional initialization can be added here if needed

def is_open_condition(door: StateBlock):
    return door.is_open

def is_closed_condition(door: StateBlock):
    return not door.is_open

def is_locked_condition(door: StateBlock):
    return door.is_locked

def is_unlocked_condition(door: StateBlock):
    return not door.is_locked

statement_is_open = Statement(
    name="IsOpen",
    description="is open",
    condition=is_open_condition
)

statement_is_closed = Statement(
    name="IsClosed",
    description="is closed",
    condition=is_closed_condition
)

statement_is_locked = Statement(
    name="IsLocked",
    description="is locked",
    condition=is_locked_condition
)

statement_is_unlocked = Statement(
    name="IsUnlocked",
    description="is unlocked",
    condition=is_unlocked_condition
)
composite_statement_closed_locked = CompositeStatement([
    (statement_is_closed, "AND", "source"),
    (statement_is_locked, "AND", "source")
])

composite_statement_closed_or_locked = CompositeStatement([
    (statement_is_closed, "OR", "source"),
    (statement_is_locked, "OR", "source")
])

def open_door(door: Door):
    if not door.is_open:
        door.is_open = True


consequence_open_door = CompositeStatement([
    (statement_is_open, "AND", "source"),
    (statement_is_closed, "AND NOT", "source"),
])
prerequisite_open_door = CompositeStatement([
    (statement_is_closed, "AND", "source"),
    (statement_is_open, "AND NOT", "source"),
    (statement_is_unlocked, "AND", "source"),
    (statement_is_locked, "AND NOT", "source")
])


transformer_open_door = CompositeTransformer(
    transformers=[(
        Transformer(
        name="OpenDoor",
        transformation=open_door,
        consequences=consequence_open_door),"source")])

#composite transfo
def close_door(door: Door):
    if door.is_open:
        door.is_open = False


consequence_close_door = CompositeStatement([
    (statement_is_closed, "AND", "source"),
    (statement_is_open, "AND NOT", "source"),
])

prerequisite_close_door = CompositeStatement([
    (statement_is_open, "AND", "source"),
    (statement_is_closed, "AND NOT", "source"),
    (statement_is_unlocked, "AND", "source"),
    (statement_is_locked, "AND NOT", "source"),
])

transformer_close_door = CompositeTransformer(
    transformers=[(Transformer(
    name="CloseDoor",
    transformation=close_door,
    consequences=consequence_close_door
), "source")])

def lock_door(door: Door):
    if not door.is_locked:
        door.is_locked = True



prerequisite_lock_door = CompositeStatement([
    (statement_is_unlocked, "AND", "source"),
    (statement_is_locked, "AND NOT", "source"),

])

consequence_lock_door = CompositeStatement([
    (statement_is_locked, "AND", "source"),
    (statement_is_unlocked, "AND NOT", "source"),
])

transformer_lock_door = CompositeTransformer(
    transformers=[(Transformer(
    name="LockDoor",
    transformation=lock_door,
    consequences=consequence_lock_door
), "source")])


def unlock_door(door: Door):
    if door.is_locked:
        door.is_locked = False


prerequisite_unlock_door = CompositeStatement([
    (statement_is_locked, "AND", "source"),
    (statement_is_unlocked, "AND NOT", "source"),
    
])
consequence_unlock_door = CompositeStatement([
    (statement_is_unlocked, "AND", "source"),
    (statement_is_locked, "AND NOT", "source"),
])

transformer_unlock_door = CompositeTransformer(
    transformers=[(Transformer(
    name="UnlockDoor",
    transformation=unlock_door,
    consequences=consequence_unlock_door
), "source")])


affordance_open_door = Affordance(
    name="OpenDoorAffordance",
    prerequisites=[prerequisite_open_door],
    transformations=[transformer_open_door]
)
affordance_close_door = Affordance(
    name="CloseDoorAffordance",
    prerequisites=[prerequisite_close_door],
    transformations=[transformer_close_door]
)
affordance_lock_door = Affordance(
    name="LockDoorAffordance",
    prerequisites=[prerequisite_lock_door],
    transformations=[transformer_lock_door]
)
affordance_unlock_door = Affordance(
    name="UnlockDoorAffordance",
    prerequisites=[prerequisite_unlock_door],
    transformations=[transformer_unlock_door]
)

def print_door_status(door: Door):
    if door.is_open:
        print("The door is open")
    else:
        print("The door is closed")
    if door.is_locked:
        print("The door is locked")
    else:
        print("The door is unlocked")



def main():
    door = Door(
    id=str(uuid.uuid4()),
    owner_id="door_owner",  # Identifier of the door's owner or location
    name="Door",
    blocks_move=True,  # A closed door blocks movement
    blocks_los=False,  # A door doesn't generally block line of sight
    can_store=False,
    can_be_stored=False,
    can_act=False,
    can_move=False,
    can_be_moved=False,
    position=(0, 0, 0),  # Position of the door in the environment
    is_open=False,  # Custom attribute indicating if the door is open
    is_locked=True  # Custom attribute indicating if the door is locked
)


        #1 start with a closed and unlocked door

    print_door_status(door)
    # try to open the door but door is locked
    print("the door can be opened",affordance_open_door.is_applicable(door))
    # unlock the door
    print("the door can be unlocked",affordance_unlock_door.is_applicable(door))
    affordance_unlock_door.apply(door)
    print_door_status(door)
    # ry if the door can be opened now
    print("the door can be opened",affordance_open_door.is_applicable(door))
    # open the door
    affordance_open_door.apply(door)
    print_door_status(door)
    #try to lock the door
    print("the door can be locked",affordance_lock_door.is_applicable(door))
    #lock the door
    affordance_lock_door.apply(door)
    print_door_status(door)
    #try to close the door
    print("the door can be closed",affordance_close_door.is_applicable(door))
    #the door can be unlocked
    print("the door can be unlocked",affordance_unlock_door.is_applicable(door))
    #unlock the door
    affordance_unlock_door.apply(door)
    print_door_status(door)
    #the door can be closed
    print("the door can be closed",affordance_close_door.is_applicable(door))
    #close the door
    affordance_close_door.apply(door)
    print_door_status(door)

    #lock the door
    affordance_lock_door.apply(door)
    print_door_status(door)

    #now plan how to open it 
    goal = (statement_is_open,door)
    print("the goal is",goal[0].name)
    print("the state of the goal is currently",goal[0](goal[1])[0])
    #need to find which actions if applied to door will make the goal true and whether it is possible to apply them
    affordances = [affordance_open_door,affordance_close_door,affordance_lock_door,affordance_unlock_door]
    prerequisites = [prerequisite_open_door,prerequisite_close_door,prerequisite_lock_door,prerequisite_unlock_door]
    consequences = [consequence_open_door,consequence_close_door,consequence_lock_door,consequence_unlock_door]
    reach_goal =[]
    for affordance in affordances:
        force_true = affordance.force_consequence_true(door)
        sub_statements = force_true[0][0][0]["sub_statements"]
        for substate in sub_statements:
            if substate["statement"] == goal[0].name and substate["result"] == True:
                print(f"the action {affordance.name} will make the goal true")
                #check if the action is applicable
                if affordance.is_applicable(door):
                    print(f"the action {affordance.name} is applicable")
                else:
                    print(f"the action {affordance.name} is not applicable, because of the following statements: {affordance.why_not_applicable(door)}")
                    reach_goal.append(affordance)
                    new_goal_name = reach_goal[0].why_not_applicable(door)[0][0]
                    print("setting subgoal",new_goal_name,"to",True)
                    for statement in prerequisites:
                        if statement.name == new_goal_name:
                            print("found the statement object corresponding to ",statement.name)
                            new_goal = (statement,door)
                            eval_new_goal = new_goal[0](new_goal[1])
                            eval_true_new_goal = new_goal[0].force_true(new_goal[1])[0]
                            print("checking across the substatements which are not true")
                            for substatement in zip(eval_new_goal["sub_statements"],eval_true_new_goal["sub_statements"]):
                                if substatement[0]["result"] != substatement[1]["result"]:
                                    print(f"the statement {substatement[0]['statement']} is  {substatement[0]['result']} , but it needs to be {substatement[1]['result']} in order to apply the action {reach_goal[0].name}")
                                    second_goal_name= (substatement[0]['statement'], substatement[1]["result"])
                                    print("setting subgoal",second_goal_name,"to",substatement[1]["result"])
                                    for affordance in affordances:
                                        force_true = affordance.force_consequence_true(door)
                                        sub_statements = force_true[0][0][0]["sub_statements"]
                                        for substate in sub_statements:
                                            if substate["statement"] == second_goal_name[0] and substate["result"] == second_goal_name[1]:
                                                print(f"the action {affordance.name} will make the goal true")
                                                #check if the action is applicable
                                                if affordance.is_applicable(door):
                                                    print(f"the action {affordance.name} is applicable")
                                                else:
                                                    print(f"the action {affordance.name} is not applicable, because of the following statements: {affordance.why_not_applicable(door)}")
                                                    reach_goal.append(affordance)
                    
# print(force_true[0][0][0]["sub_statements"])
if __name__ == "__main__":
    main()
