# InfinipyRe
 Infinitely growing game engine

## Overview
This framework offers a sophisticated approach to managing stateful objects, suitable for a variety of applications including simulations, interactive systems, and complex decision-making environments. Its design emphasizes modularity, flexibility, and the capacity to model complex interactions and behaviors in a clear and manageable way.

## Key Components
The framework is built around several core classes:

1. **StateBlock**: Represents any stateful object with a set of attributes and states.
2. **Statement & CompositeStatement**: Define conditions to evaluate against `StateBlock` attributes.
3. **RelationalStatement & CompositeRelationalStatement**: Extend the capabilities of `Statement` for interactions between multiple `StateBlock` instances.
4. **Transformer & CompositeTransformer**: Define actions or transformations that modify the state of a `StateBlock`.
5. **Affordance**: A high-level concept representing an action or capability, combining prerequisites (conditions) and consequences (transformations).

## Design Philosophy
### Modularity and Emergent Behavior
The design of this framework facilitates emergent modularity - the ability to create complex behaviors and interactions from simple, modular components. By combining different Statements, Transformers, and Affordances, users can construct intricate systems that exhibit sophisticated behaviors emerging from basic rules and interactions.

### Affordances
Affordances are central to this framework, embodying the potential actions or interactions an object can have in a given context. They encapsulate the idea that the capabilities of an object (or an agent within a simulation) are not just a property of the object itself, but also of its relationship to the environment and other objects. This concept allows for dynamic and context-sensitive behavior modeling.

### Natural Language to Simulation
One of the key strengths of this framework is its potential to bridge natural language reasoning and simulation. The clear structure of StateBlocks and the logic-driven design of Affordances and Statements make it possible to map natural language descriptions of states and actions directly to their computational counterparts. This capability opens avenues for creating simulations and interactive systems based on narrative descriptions or real-world scenarios described in natural language.

## Usage
To integrate this framework into your project:
1. Define `StateBlock` instances to represent your entities or objects.
2. Create `Statements` and `Transformers` to encapsulate conditions and actions.
3. Use `Affordances` to define what actions are possible under which conditions.
4. Combine these elements to model complex interactions and behaviors in your system.

## Potential Applications
This framework is versatile and can be applied in various domains, such as:
- **Simulation Modeling**: For creating dynamic models of real-world systems.
- **Game Development**: To design complex game mechanics and interactions.
- **Decision Support Systems**: Where modeling of various scenarios and outcomes is needed.
- **Automated Reasoning**: Especially in converting descriptive, natural language inputs into executable logic.

By offering a structured yet flexible approach to defining and managing interactions and states, this framework provides a powerful toolset for developers and researchers in various fields.
