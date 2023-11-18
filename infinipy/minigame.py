# Assuming the classes you've defined are already imported
from typing import Callable, List, Tuple, Union
from affordance import Affordance
from stateblock import StateBlock
from statement import Statement, CompositeStatement, RelationalStatement, CompositeRelationalStatement, bigger_than, positive
from transformer import Transformer
# Defining the StateBlocks for the wizards

class WizardBlock(StateBlock):
    def __init__(self, mana: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mana = mana

# Defining the WizardBlock instances for the wizards
wizard1 = WizardBlock(id="1", owner_id="player1", name="Wizard1", position=(0, 0, 0), 
                      reach=1, hitpoints=100, mana=50, size="medium", 
                      blocks_move=False, blocks_los=False, 
                      can_store=False, can_be_stored=False, 
                      can_act=True, can_move=True, can_be_moved=False)

wizard2 = WizardBlock(id="2", owner_id="player2", name="Wizard2", position=(10, 0, 0), 
                      reach=1, hitpoints=100, mana=50, size="medium", 
                      blocks_move=False, blocks_los=False, 
                      can_store=False, can_be_stored=False, 
                      can_act=True, can_move=True, can_be_moved=False)

# The rest of the implementation remains the same


# Defining Conditions and Transformers
attack_condition = bigger_than(10)  # Requires more than 10 mana to attack
move_condition = positive()  # Can always move (for simplicity)

def attack_transformation(target_block):
    target_block.hitpoints -= 20  # Reduces 20 hitpoints from the target

def move_transformation(source_block):
    # Move to a new position (simplified as incrementing x coordinate)
    x, y, z = source_block.position
    source_block.position = (x + 1, y, z)

attack_transformer = Transformer("Attack", attack_transformation)
move_transformer = Transformer("Move", move_transformation)

# Defining Affordances
cast_spell = Affordance(
    name="CastSpell", 
    prerequisites=[(CompositeStatement([(attack_condition, "mana", "AND")]), "source")], 
    consequences=[(attack_transformer, "target")]
)

move = Affordance(
    name="Move", 
    prerequisites=[(CompositeStatement([(move_condition, "position", "AND")]), "source")], 
    consequences=[(move_transformer, "source")]
)

# Assuming all the necessary classes and instances are already defined

round_counter = 1
while wizard1.hitpoints > 0 and wizard2.hitpoints > 0:
    print(f"--- Round {round_counter} ---")

    # Wizard1's turn
    print("Wizard1's turn:")
    if cast_spell.is_applicable(wizard1, wizard2):
        cast_spell.apply(wizard1, wizard2)
        print(f"Wizard1 casts a spell! Wizard2's hitpoints are now {wizard2.hitpoints}.")
    else:
        move.apply(wizard1)
        print(f"Wizard1 moves to position {wizard1.position}.")

    # Check if Wizard2 is defeated
    if wizard2.hitpoints <= 0:
        break

    # Wizard2's turn
    print("Wizard2's turn:")
    if cast_spell.is_applicable(wizard2, wizard1):
        cast_spell.apply(wizard2, wizard1)
        print(f"Wizard2 casts a spell! Wizard1's hitpoints are now {wizard1.hitpoints}.")
    else:
        move.apply(wizard2)
        print(f"Wizard2 moves to position {wizard2.position}.")

    # Check if Wizard1 is defeated
    if wizard1.hitpoints <= 0:
        break

    round_counter += 1

# Determine winner
winner = "Wizard1" if wizard2.hitpoints <= 0 else "Wizard2"
print(f"--- Game Over ---")
print(f"{winner} wins the duel!")
