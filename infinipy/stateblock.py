from dataclasses import dataclass, field
import dataclasses
import uuid
from typing import Tuple, List, Optional, TYPE_CHECKING

# Updating the StateBlock class to include methods for dumping the schema and current types as dictionaries

@dataclass
class StateBlock:
    id: str
    owner_id: str
    name: str
    blocks_move: bool
    blocks_los: bool
    can_store: bool
    can_be_stored: bool
    can_act: bool
    can_move: bool
    can_be_moved: bool
    position: Tuple[int, int, int]
    inventory: List['StateBlock'] = field(default_factory=list)  # Default value arguments
    inventory_size: int = 10  # Default value argument
    stored_in: Optional['StateBlock'] = None  # Default value argument
    def __post_init__(self):
        # Ensuring the 'id' is a valid UUID string
        try:
            uuid_obj = uuid.UUID(self.id, version=4)
        except ValueError:
            self.id = str(uuid.uuid4())
        else:
            if uuid_obj.hex != self.id.replace('-', ''):
                self.id = str(uuid.uuid4())

        
    @property
    def position(self):
        # If the item is stored in another entity, return the position of that entity
        if self.stored_in:
            return self.stored_in.position
        return self._position
    
    @position.setter
    def position(self, value: Tuple[int, int, int]):
        self._position = value

    def add_to_inventory(self, item: 'StateBlock'):
        """
        Adds an item to the inventory.
        """
        if len(self.inventory) < self.inventory_size:
            item.stored_in = self
            self.inventory.append(item)
            
    
    def remove_from_inventory(self, item: 'StateBlock'):
        """
        Removes an item from the inventory.
        """
        if item in self.inventory:
            self.inventory.remove(item)
            item.stored_in = None
    
    @classmethod
    def to_schema(cls):
        # Return a dictionary representing the schema of the StateBlock
        return {field.name: str(field.type) for field in dataclasses.fields(cls)}
    
    def to_types(self):
        # Return a dictionary representing the current types of the StateBlock attributes
        # with special handling for iterables to get the subtype
        types_dict = {}
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if isinstance(value, tuple):
                types_dict[field.name] = f"Tuple[{', '.join(str(type(subvalue).__name__) for subvalue in value)}]"
            else:
                types_dict[field.name] = type(value).__name__
        return types_dict

