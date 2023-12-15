
from typing import Dict, Tuple, List
from infinipy.statement import Statement, CompositeStatement
from infinipy.stateblock import StateBlock

class StatementFactory:
    def __init__(self, grid_size: Tuple[int, int]):
        self.grid_size = grid_size
        self.statements_source_registry = {}
        self.statements_target_registry = {}
        self.source_statements_spatial_registry, self.target_statements_spatial_registry = self.generate_spatial_statements()
        self.entity_registry = {}
        self.position_registry = {}

    def get_statement_registry(self):
        return self.statements_target_registry
    
    def add_entity(self, entity: StateBlock):
        self.entity_registry[entity.id] = self.create_composite_statement(entity)
        if entity.position in self.position_registry:
            self.position_registry[entity.position].append(entity.id)
        else:
            self.position_registry[entity.position] = [entity.id]
            
    def registry_to_list(self):
        return [(value,entity_id,entity_id) for entity_id,value in self.entity_registry.items()]
    
    def get_composite_spatial_statements(self):
        composite_dict = {}
        for pos,statement in self.target_statements_spatial_registry.items():
            composite_dict[pos] = CompositeStatement([(statement,True)])
        return composite_dict

    def generate_bool_statements_for_stateblock(self, state_block: StateBlock) -> List[Tuple[Statement, bool]]:
        statements = []

        # Iterate over each boolean attribute of StateBlock and generate statements
        for attr in vars(state_block):
            if isinstance(getattr(state_block, attr), bool):
                statement_name = f"{attr}_is_true"

                # Check and create target statements
                if statement_name not in self.statements_target_registry:
                    self.statements_target_registry[statement_name] = Statement(
                        name=statement_name,
                        description=f"Checks if {attr} is True.",
                        callable=lambda block, attr=attr: getattr(block, attr),
                        usage='target'
                    )
                statements.append((self.statements_target_registry[statement_name], getattr(state_block, attr)))

                # Check and create source statements if can_act is True
                if state_block.can_act and statement_name not in self.statements_source_registry:
                    # print("Creating source statement")
                    self.statements_source_registry[statement_name] = Statement(
                        name=statement_name,
                        description=f"Checks if {attr} is True.",
                        callable=lambda block, attr=attr: getattr(block, attr),
                        usage='source'
                    )
                    statements.append((self.statements_source_registry[statement_name], getattr(state_block, attr)))
        # print("sub_inside",len(statements))
        return statements

    def create_composite_statement(self, state_block: StateBlock) -> CompositeStatement:
        substatements = self.generate_bool_statements_for_stateblock(state_block)
        # print("inside",len(substatements))
        # now add the spatial statements all false, but the one one at the position of the stateblock
        for source_statement,target_statement in zip(self.source_statements_spatial_registry.values(),self.target_statements_spatial_registry.values()):
            if state_block.can_act:
                substatements.append((source_statement,source_statement(state_block)[0]))
            substatements.append((target_statement,target_statement(state_block,state_block)[0]))
        return CompositeStatement(substatements)

    
    def generate_spatial_statements(self) -> Dict[Tuple[int, int], Statement]:
        source_spatial_statements = {}
        target_spatial_statements = {}
        for x in range(self.grid_size[0]):
            for y in range(self.grid_size[1]):
                pos = (x, y)
                statement_name = f"position_at_{pos}"
                source_spatial_statements[pos] = Statement(
                    name=statement_name,
                    description=f"Entity is at position {pos}.",
                    callable=lambda block, pos=pos: block.position == pos,
                    usage='source'
                )
                target_spatial_statements[pos] = Statement(
                    name=statement_name,
                    description=f"Entity is at position {pos}.",
                    callable=lambda block, pos=pos: block.position == pos,
                    usage='target'
                )
        return source_spatial_statements, target_spatial_statements

   