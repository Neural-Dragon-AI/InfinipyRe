from infinipy.stateblock import StateBlock
from infinipy.statement import Statement, CompositeStatement, RelationalStatement, CompositeRelationalStatement
from infinipy.transformer import Transformer, CompositeTransformer, RelationalTransformer
from infinipy.statement import bigger_than,equals_to
from infinipy.affordance import Affordance
# Step 1: Setup
import uuid
# Importing necessary classes from the user's code
# The user's code will be assumed to be contained in a separate file named 'game_framework.py' for the sake of this example

# Helper function for creating test StateBlocks
def create_test_state_block(name, hp, size, position):
    return StateBlock(
        id=str(uuid.uuid4()),
        owner_id="test_owner",
        name=name,
        reach=1,
        hitpoints=hp,
        size=size,
        blocks_move=False,
        blocks_los=False,
        can_store=True,
        can_be_stored=False,
        can_act=True,
        can_move=True,
        can_be_moved=False,
        position=position
    )

# Helper function to print the state of a StateBlock
def print_state_block(state_block):
    print(f"StateBlock: {state_block.name}")
    print(f"  - HP: {state_block.hitpoints}")
    print(f"  - Position: {state_block.position}")
    print(f"  - Size: {state_block.size}\n")

test_block = create_test_state_block("test", 10, "large", (0, 0))
print_state_block(test_block)

# Step 2: Basic Affordance Creation
# Creating a simple affordance using basic statements
def test_basic_affordance():
    # Create a test state block
    test_block = create_test_state_block("Test Block", 100, "medium", (0, 0, 0))

    # Define a simple statement (e.g., hitpoints must be greater than 50)
    statement = bigger_than(50, "hitpoints")
    # Define a simple transformer (e.g., reduce hitpoints by 10)
    transformer = Transformer("Reduce HP", lambda block: setattr(block, "hitpoints", block.hitpoints - 10))

    # Create an affordance using the statement and transformer
    affordance = Affordance("Test Affordance", [(statement, 'source')], [(transformer, 'source')])
    print_state_block(test_block)
    # Applying the affordance to the test block
    affordance(test_block)
    print_state_block(test_block)

test_basic_affordance()

# Step 3: Composite Statements in Affordances
# Incorporating composite statements into affordances
def test_composite_affordance():
    # Create a test state block
    test_block = create_test_state_block("Composite Block", 80, "large", (1, 1, 1))

    # Define composite statements
    statement1 = bigger_than(50, "hitpoints")
    statement2 = equals_to("small", "size")
    composite_statement = CompositeStatement([(statement1, 'AND'), (statement2, 'AND NOT')])

    # Define a transformer (e.g., increase hitpoints by 20)
    transformer = Transformer("Increase HP", lambda block: setattr(block, "hitpoints", block.hitpoints + 20))

    # Create an affordance with the composite statement
    affordance = Affordance("Composite Affordance", [(composite_statement, 'source')], [(transformer, 'source')])
    print_state_block(test_block)
    # Applying the affordance to the test block
    affordance(test_block)
    print_state_block(test_block)

test_composite_affordance()

# Step 4: Relational Statements in Affordances
# Using relational statements to define interactions between different entities
def test_relational_affordance():
    # Create two test state blocks
    source_block = create_test_state_block("Source Block", 60, "medium", (2, 2, 2))
    target_block = create_test_state_block("Target Block", 40, "small", (3, 3, 3))

    # Define a relational statement (e.g., source's HP must be greater than target's)
    relational_statement = RelationalStatement("HP Comparison", "Source HP greater than Target HP", 
                                                lambda source, target: source.hitpoints > target.hitpoints)

    # Define a relational transformer (e.g., Swaps the HP of the source and target)
    def swap_hp(source: StateBlock, target: StateBlock):
        source_hp = source.hitpoints
        source.hitpoints = target.hitpoints
        target.hitpoints = source_hp

    relational_transformer = RelationalTransformer("Swap HP", lambda source, target: (swap_hp(source, target)))


    # Create an affordance with the relational statement
    affordance = Affordance("Relational Affordance", [(relational_statement, 'source')], [(relational_transformer, 'source')])
    print_state_block(source_block)
    print_state_block(target_block)
    # Applying the affordance to the test blocks
    affordance(source_block, target_block)
    print_state_block(source_block)
    print_state_block(target_block)

test_relational_affordance()

# Step 5: Composite and Relational Transformers
# Applying complex transformations to entities based on defined affordances

def test_composite_relational_transformers():
    # Step 1: Create StateBlocks
    block_a = create_test_state_block("Block A", 100, "medium", (0, 0, 0))
    block_b = create_test_state_block("Block B", 50, "small", (1, 1, 1))

    # Step 2: Define Simple Transformers
    decrease_hp = Transformer("Decrease HP", lambda block: setattr(block, "hitpoints", block.hitpoints - 10))
    change_size = Transformer("Change Size", lambda block: setattr(block, "size", "small"))

    # Step 3: Create Composite Transformer
    composite_transformer = CompositeTransformer([decrease_hp, change_size])

    # Step 4: Define Relational Transformer
    transfer_hp = RelationalTransformer("Transfer HP", 
                                        lambda source, target: (setattr(source, "hitpoints", source.hitpoints - 5),
                                                                setattr(target, "hitpoints", target.hitpoints + 5)))

    # Step 5: Setup Affordance
    hp_above_30 = bigger_than(30, "hitpoints")
    affordance = Affordance("Complex Interaction", [(hp_above_30, 'source')], [(composite_transformer, 'source'), (transfer_hp, 'source')])
    print_state_block(block_a)
    print_state_block(block_b)
    # Step 6: Apply the Affordance
    affordance(block_a, block_b)

    # Step 7: Print Results
    print_state_block(block_a)
    print_state_block(block_b)

test_composite_relational_transformers()
