# Infinipy Package Demonstration

## Overview

This demonstration showcases the capabilities of the Infinipy package, a powerful toolkit for creating and managing interactive simulations. Infinipy provides a rich set of classes and functions that enable developers to model complex environments and interactions. The demo is a maze navigation game that demonstrates how entities (like characters, walls, floors, and treasures) interact within a system.

## Key Components

### StateBlock

The `StateBlock` class forms the core of the system. It represents an entity within the environment with various attributes like `can_store`, `can_move`, `can_be_stored`, and others, determining the entity's behavior and interactions.

#### Derived Classes:

- `CharacterBlock`: Represents a character in the maze, capable of moving and storing items.
- `FloorBlock`: Represents floor areas on which characters can move.
- `WallBlock`: Represents wall barriers that block movement.
- `TreasureBlock`: Represents treasures that characters can pick up.

### Statement and Affordance

- `Statement` classes (`Statement`, `CompositeStatement`, `RelationalStatement`, and `CompositeRelationalStatement`) define conditions under which certain actions or interactions can take place.
- `Affordance` class represents an action or interaction that an entity can perform, given certain prerequisites are met.

#### Key Affordances:

- `move_to_affordance`: Allows a character to move to a floor block within reach.
- `pick_up_affordance`: Enables a character to pick up a treasure if they have inventory space and the treasure is within reach.

### Transformer

- `Transformer` classes (`Transformer`, `CompositeTransformer`, `RelationalTransformer`, `CompositeRelationalTransformer`) handle the modifications to the state of entities.
- Transformations are applied as consequences of an affordance being executed.

### Simulation Functions

- `create_map_with_room`: Sets up the maze with walls, floors, and treasures.
- `display_grid`: Visual representation of the maze and entities.
- `simulate_movement`: Handles the movement of the character in the maze, including picking up treasures and moving to different floor blocks.

## Simulation Flow

1. The maze is initialized with characters, walls, floors, and treasures.
2. Each turn, the character checks for reachable treasures. If a treasure is within reach and pickable, the character picks it up.
3. If no treasure is picked up, the character moves to a random reachable floor tile.
4. The grid is displayed after each turn to show the updated positions and interactions.

## Conclusion

This demonstration provides a practical example of how the Infinipy package can be used to create an interactive and dynamic environment. It illustrates the package's versatility in handling various types of entities and interactions within a simulated world.
