from typing import Dict, List, Tuple, Optional, Callable, Union, TYPE_CHECKING
from infinipy.stateblock import StateBlock
from infinipy.statement import Statement, CompositeStatement, RelationalStatement, CompositeRelationalStatement
from infinipy.transformer import Transformer, CompositeTransformer, RelationalTransformer, CompositeRelationalTransformer
from infinipy.affordance import Affordance
import math
import random
import heapq
import time


class GridMap:
    def __init__(self, map_size: Optional[Tuple[int, int]] = None, name='gridmap'):
        self.entities: Dict[Tuple[int, int, int], List[StateBlock]] = {}
        self.map_size: Optional[Tuple[int, int]] = map_size
        self.blocks_move: Dict[Tuple[int, int, int], bool] = {}
        self.blocks_los: Dict[Tuple[int, int, int], bool] = {}
        self.creation_time = time.time()
        self.human_readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.creation_time))
        self.name = f"{name}_{self.human_readable_time}"

    def _add_entity_to_position(self, entity: StateBlock, position: Tuple[int, int, int]) -> None:
        self.entities.setdefault(position, []).append(entity)
        entity.position = position
        self._update_blocks_mappings(position, entity)

    def _remove_entity_from_position(self, entity: StateBlock, position: Tuple[int, int, int]) -> None:
        if position in self.entities and entity in self.entities[position]:
            print(f"Removing {entity} from {position}")
            self.entities[position].remove(entity)
            if not self.entities[position]:
                del self.entities[position]
        elif position in self.entities and entity not in self.entities[position]:
            print(f"Entity {entity} not found at {position}, while removing")
        elif position not in self.entities:
            print(f"Position {position} not found while removing")

    def add_entity(self, entity: StateBlock, position: Tuple[int, int, int]) -> None:
        if self.map_size and not self.is_within_bounds(position):
            raise ValueError("Position out of bounds")
        self._add_entity_to_position(entity, position)
        for item in entity.inventory:
            self._add_entity_to_position(item, position)

    def remove_entity(self, entity: StateBlock) -> None:
        position = entity.position
        self._remove_entity_from_position(entity, position)
        for item in entity.inventory:
            self._remove_entity_from_position(item, position)
        self._resync_blocks_at_position(position)

    def move_entity(self, entity: StateBlock, new_position: Tuple[int, int, int]) -> None:
        if self.map_size and not self.is_within_bounds(new_position):
            raise ValueError("New position out of bounds")
        print(f"attemting to move {entity} to {new_position} from {entity.position}")
        old_position = entity.position
        self.remove_entity(entity)
        self.add_entity(entity, new_position)
    
    def get_entities_at_position(self, position: Tuple[int, int, int]) -> List[StateBlock]:
        entities = self.entities.get(position, [])
        all_entities = []
        for entity in entities:
            all_entities.append(entity)
            all_entities.extend(entity.inventory)
        return all_entities

    def execute_affordance(self, affordance: Affordance, source: StateBlock, target: StateBlock) -> None:
        if affordance.is_applicable(source, target):
            # Store the original states and positions before applying the affordance
            original_states = self._capture_entity_states(source, target)

            # Apply the affordance
            affordance.apply(source, target)

            # Synchronize the grid map with any changes resulting from the affordance
            self._synchronize_affordance_effects(source, target, original_states)
    
    def affordance_applicable_at_position(self, affordance: Affordance, source: StateBlock, position: Tuple[int, int, int]) -> bool:
        if not self.is_within_bounds(position):
            return False
        targets = [entity for entity in self.get_entities_at_position(position) if entity != source]
        for target in targets:
            if affordance.is_applicable(source, target):
                return True, target
        return False, None

    def _capture_entity_states(self, source: StateBlock, target: StateBlock):
        # Capture the original states of the source and target entities
        return {
            "source_original_position": source.position,
            "source_stored_in": source.stored_in,
            "target_original_position": target.position,
            "target_stored_in": target.stored_in
        }

    def _synchronize_affordance_effects(self, source: StateBlock, target: StateBlock, original_states):
        # Check for changes in the stored_in status of source and target
        if source.stored_in != original_states["source_stored_in"]:
            print("Source stored in status changed")
            self._update_entity_storage_status(source, original_states["source_original_position"])
        elif source.position != original_states["source_original_position"] and source.stored_in is None:
            print("Source position changed")
            self._remove_entity_from_position(source, original_states["source_original_position"])
            for item in source.inventory:
                self._remove_entity_from_position(item, original_states["source_original_position"])
            self.add_entity(source,source.position)
            
        if target.stored_in != original_states["target_stored_in"]:
            print("Target stored in status changed")
            self._update_entity_storage_status(target, original_states["target_original_position"])
        # Check for changes in the position of source and target
        elif target.position != original_states["target_original_position"] and source.stored_in is None:
            print("Target position changed")
            self._remove_entity_from_position(target, original_states["target_original_position"])
            for item in target.inventory:
                self._remove_entity_from_position(item, original_states["target_original_position"])
            self.add_entity(target, target.position)


    def _update_entity_storage_status(self, entity: StateBlock, original_position: Tuple[int, int, int]):
        if entity.stored_in is None:
            # Entity was removed from inventory, place it on the grid at its current position
            self.add_entity(entity, entity.position)
        else:
            # Entity was added to an inventory, remove it from the grid at old position
            # and add it at current storage position, further movements will be automatically handled by the grid
            self._remove_entity_from_position(entity, original_position)
            self._add_entity_to_position(entity, entity.stored_in.position)


    # Rest of the class remains unchanged
    def _update_blocks_mappings(self, position: Tuple[int, int, int], entity: StateBlock) -> None:
        self.blocks_move[position] = self.blocks_move.get(position, False) or entity.blocks_move
        self.blocks_los[position] = self.blocks_los.get(position, False) or entity.blocks_los
    
    def _resync_blocks_at_position(self, position: Tuple[int, int, int]) -> None:
        self.blocks_move[position] = any(entity.blocks_move for entity in self.get_entities_at_position(position))
        self.blocks_los[position] = any(entity.blocks_los for entity in self.get_entities_at_position(position))
    
    def resync_all_blocks(self) -> None:
        self.blocks_move.clear()
        self.blocks_los.clear()
        for position, entities in self.entities.items():
            for entity in entities:
                self._update_blocks_mappings(position, entity)

    def find_entities_by_statement(self, statement: Statement, target: Optional[Statement]=None) -> List[StateBlock]:
        all_entities = []
        for entity_list in self.entities.values():
            for entity in entity_list:
                if isinstance(statement, (RelationalStatement, CompositeRelationalStatement)) and statement.apply(entity, target):
                    all_entities.append(entity)
                elif isinstance(statement, (Statement, CompositeStatement)) and statement.apply(entity):
                    all_entities.append(entity)
                all_entities.extend([item for item in entity.inventory if statement.apply(item)])
        return all_entities
    
    def check_statement_at_position(self, position: Tuple[int, int, int], statement: Statement, mode: str = "all") -> Union[bool, Tuple[bool, List[StateBlock]]]:
        entities_at_position = self.get_entities_at_position(position)
        matching_entities = []

        for entity in entities_at_position:
            if statement.apply(entity):
                if mode == "first":
                    return True, [entity]
                matching_entities.append(entity)

        return len(matching_entities) > 0, matching_entities if mode == "all" else None
    

    
    def is_within_bounds(self, position: Tuple[int, int, int]) -> bool:
        if not self.map_size:
            raise ValueError("Map size not set")
        x, y, _ = position
        max_x, max_y = self.map_size
        return 0 <= x < max_x and 0 <= y < max_y
    

    def get_adjacent_positions(self, position: Tuple[int, int, int], range_val: int = 1, include_diagonals: bool = False, consider_z: bool = False) -> List[Tuple[int, int, int]]:
        x, y, z = position
        adjacent_positions = []

        # Determine the bounds for the loops
        x_min, y_min, z_min = max(x - range_val, 0), max(y - range_val, 0), z - range_val if consider_z else z
        x_max, y_max, z_max = min(x + range_val, self.map_size[0] - 1 if self.map_size else x + range_val), \
                            min(y + range_val, self.map_size[1] - 1 if self.map_size else y + range_val), \
                            z + range_val if consider_z else z

        for dx in range(x_min - x, x_max - x + 1):
            for dy in range(y_min - y, y_max - y + 1):
                for dz in (range(z_min - z, z_max - z + 1) if consider_z else [0]):
                    if dx == 0 and dy == 0 and dz == 0:
                        continue  # Skip the original position
                    if not include_diagonals and abs(dx) + abs(dy) > 1:
                        continue  # Skip diagonals if not included
                    new_position = (x + dx, y + dy, z + dz)
                    adjacent_positions.append(new_position)

        return adjacent_positions
    

    def neighbors(self, position: Tuple[int, int, int], check_blocks_move = True) -> List[Tuple[int, int, int]]:
        x, y, z = position
        candidates = [
            (x - 1, y, z), (x + 1, y, z), 
            (x, y - 1, z), (x, y + 1, z),
            (x - 1, y - 1, z), (x - 1, y + 1, z),
            (x + 1, y - 1, z), (x + 1, y + 1, z),
            # Include vertical neighbors if needed
        ]
        
        valid_neighbors = []
        for pos in candidates:
            condition = self.is_within_bounds(pos) and not self.blocks_move[pos] if check_blocks_move else self.is_within_bounds(pos)
            if condition:
                valid_neighbors.append(pos)

        return valid_neighbors
    
    def cast_light(self, origin: Tuple[int, int, int], max_radius: int, angle: float) -> List[Tuple[int, int, int]]:
        x0, y0, z0 = origin
        # Assuming the angle and max_radius only affect x and y for simplicity
        x1 = x0 + int(max_radius * math.cos(angle))
        y1 = y0 + int(max_radius * math.sin(angle))

        dx, dy = abs(x1 - x0), abs(y1 - y0)
        x, y, z = x0, y0, z0
        n = 1 + dx + dy
        x_inc = 1 if x1 > x0 else -1
        y_inc = 1 if y1 > y0 else -1
        error = dx - dy
        dx *= 2
        dy *= 2

        line_points = []
        first_iteration = True
        for _ in range(n):
            if self.is_within_bounds((x, y, z)):
                line_points.append((x, y, z))
                if not first_iteration and self.blocks_los.get((x, y, z), False):
                    break
            first_iteration = False

            if error > 0:
                x += x_inc
                error -= dy
            else:
                y += y_inc
                error += dx

        return line_points
    
    def line(self, start: Tuple[int, int, int], end: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
        dx, dy = end[0] - start[0], end[1] - start[1]
        distance = math.sqrt(dx * dx + dy * dy)
        angle = math.atan2(dy, dx)
        return self.cast_light(start, math.ceil(distance), angle)
    
    def line_of_sight(self, start: Tuple[int, int, int], end: Tuple[int, int, int]) -> bool:
        line_points = self.line(start, end)
        
        # Skip the starting point and iterate through the rest of the points
        for point in line_points[1:]:
            if self.blocks_los.get(point, False):
                return False

        return True
    
    def shadow_casting(self, origin: Tuple[int, int, int], max_radius: int = None) -> List[Tuple[int, int, int]]:
        max_radius = max_radius or max(self.map_size)
        visible_cells = [origin]

        step_size = 0.5  # Decrease the step size for better accuracy
        for angle in range(int(360 / step_size)):  # Adjust the loop range based on the new step size
            visible_cells.extend(self.cast_light(origin, max_radius, math.radians(angle * step_size)))
        #takes only unique values of visible cells
        visible_cells = list(set(visible_cells))
        return visible_cells
    
    def a_star(self, start: Tuple[int, int, int], goal: Tuple[int, int, int]) -> Optional[List[Tuple[int, int, int]]]:
        if not (isinstance(start, tuple) and isinstance(goal, tuple)):
            raise TypeError("Start and goal must be tuples")

        open_set = [(0, start)]  # The open set is a list of tuples (priority, position)
        came_from: Dict[Tuple[int, int, int], Tuple[int, int, int]] = {}
        g_score: Dict[Tuple[int, int, int], int] = {start: 0}
        f_score: Dict[Tuple[int, int, int], int] = {start: self.heuristic(start, goal)}

        while open_set:
            current = heapq.heappop(open_set)[1]
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            for neighbor in self.neighbors(current):
                tentative_g_score = g_score[current] + 1  # Assuming uniform cost
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    if (f_score[neighbor], neighbor) not in open_set:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None  # No path found
    
    def heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def dijkstra(self, start: Tuple[int, int, int], max_distance: int) -> Dict[Tuple[int, int, int], int]:
        if not isinstance(start, tuple):
            raise TypeError("Start must be a tuple")

        distances: Dict[Tuple[int, int, int], int] = {start: 0}
        unvisited = [(0, start)]  # The unvisited set is a list of tuples (distance, position)

        while unvisited:
            current_distance, current_position = heapq.heappop(unvisited)
            if current_distance > max_distance:
                continue

            for neighbor in self.neighbors(current_position):
                new_distance = current_distance + 1  # Assuming uniform cost between nodes
                if neighbor not in distances or new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    heapq.heappush(unvisited, (new_distance, neighbor))

        return distances
    
    def get_all_entities(self) -> List[StateBlock]:
        all_entities = []
        for entity_list in self.entities.values():
            for entity in entity_list:
                all_entities.append(entity)
                all_entities.extend(entity.inventory)
        return all_entities
    
    def print_entities(self):
        print("Printing entities for gridmap: "+self.name)
        time_since_creation = time.time() - self.creation_time
        print("Time since creation: "+str(time_since_creation))
        for key,entity_list in self.entities.items():
        # print(key,len(entity_list))
            for entity in entity_list:
                print(entity.name, entity.position)

# class GridMap:
#     def __init__(self, map_size: Optional[Tuple[int, int]] = None, name = 'gridmap'):
#         self.entities: Dict[Tuple[int, int, int], List[StateBlock]] = {}
#         self.map_size: Optional[Tuple[int, int]] = map_size
#         self.blocks_move: Dict[Tuple[int, int, int], bool] = {}
#         self.blocks_los: Dict[Tuple[int, int, int], bool] = {}
#         self.creation_time = time.time()
#         #convert time to human readable format ignoring decimals
#         self.human_readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.creation_time))
#         self.name = name+"_"+str(self.human_readable_time)
    
#     def _update_blocks_mappings(self, position: Tuple[int, int, int], entity: StateBlock) -> None:
#         self.blocks_move[position] = self.blocks_move.get(position, False) or entity.blocks_move
#         self.blocks_los[position] = self.blocks_los.get(position, False) or entity.blocks_los
    
#     def _resync_blocks_at_position(self, position: Tuple[int, int, int]) -> None:
#         self.blocks_move[position] = any(entity.blocks_move for entity in self.get_entities_at_position(position))
#         self.blocks_los[position] = any(entity.blocks_los for entity in self.get_entities_at_position(position))
    
#     def resync_all_blocks(self) -> None:
#         self.blocks_move.clear()
#         self.blocks_los.clear()
#         for position, entities in self.entities.items():
#             for entity in entities:
#                 self._update_blocks_mappings(position, entity)

#     def add_entity(self, entity: StateBlock, position: Tuple[int, int, int]) -> None:
#         if self.map_size and not self.is_within_bounds(position):
#             raise ValueError("Position out of bounds")
        
#         self.entities.setdefault(position, []).append(entity)
#         # print(self.entities)
#         entity.position = position
#         for item in entity.inventory:
#             self._update_stored_item_position(item, position)
#         self._update_blocks_mappings(position, entity)

#     def remove_entity(self, entity: StateBlock) -> None:
#         position = entity.position
#         if position in self.entities:
#             self.entities[position].remove(entity)
#             if not self.entities[position]:
#                 del self.entities[position]
#         for item in entity.inventory:
#             self._remove_stored_item(item)
#         self._resync_blocks_at_position(position)

#     def move_entity(self, entity: StateBlock, new_position: Tuple[int, int, int]) -> None:
#         if self.map_size and not self.is_within_bounds(new_position):
#             raise ValueError("New position out of bounds")
#         old_position = entity.position
#         self.remove_entity(entity)
#         self.add_entity(entity, new_position)
#         for item in entity.inventory:
#             self._update_stored_item_position(item, new_position)
#         self._resync_blocks_at_position(old_position)
#         self._update_blocks_mappings(new_position, entity)

#     def get_entities_at_position(self, position: Tuple[int, int, int]) -> List[StateBlock]:
#         entities = self.entities.get(position, [])
#         all_entities = []
#         for entity in entities:
#             all_entities.append(entity)
#             all_entities.extend(entity.inventory)
#         return all_entities

#     def find_entities_by_statement(self, statement: Statement, target: Optional[Statement]=None) -> List[StateBlock]:
#         all_entities = []
#         for entity_list in self.entities.values():
#             for entity in entity_list:
#                 if isinstance(statement, (RelationalStatement, CompositeRelationalStatement)) and statement.apply(entity, target):
#                     all_entities.append(entity)
#                 elif isinstance(statement, (Statement, CompositeStatement)) and statement.apply(entity):
#                     all_entities.append(entity)
#                 all_entities.extend([item for item in entity.inventory if statement.apply(item)])
#         return all_entities
    
#     def check_statement_at_position(self, position: Tuple[int, int, int], statement: Statement, mode: str = "all") -> Union[bool, Tuple[bool, List[StateBlock]]]:
#         entities_at_position = self.get_entities_at_position(position)
#         matching_entities = []

#         for entity in entities_at_position:
#             if statement.apply(entity):
#                 if mode == "first":
#                     return True, [entity]
#                 matching_entities.append(entity)

#         return len(matching_entities) > 0, matching_entities if mode == "all" else None

#     def _update_stored_item_position(self, item: StateBlock, position: Tuple[int, int, int]) -> None:
#         if item.stored_in:
#             # Check if the item is already part of the grid as inventory of another entity
#             if item not in self.entities.get(position, []):
#                 self.entities.setdefault(position, []).append(item)
#             item.position = position


#     def _remove_stored_item(self, item: StateBlock) -> None:
#         if item.position in self.entities:
#             self.entities[item.position].remove(item)
#             if not self.entities[item.position]:
#                 del self.entities[item.position]

#     def sync_positions(self) -> None:
#         for position, entities in list(self.entities.items()):
#             for entity in entities:
#                 if entity.position != position:
#                     print("Syncing position for entity: "+entity.name)
#                     if entity.stored_in:
#                         print("The entity is stored in another entity but have not been updated yet")
#                         self._update_stored_item_position(entity, entity.stored_in.position)
#                     else:
#                         print("Old position: "+str(position))
#                         print("New position: "+str(entity.position))
#                         self.move_entity(entity, entity.position)
#                 for item in entity.inventory:
#                     self._update_stored_item_position(item, entity.position)




#     def execute_affordance(self, affordance: Affordance, source: StateBlock, target: StateBlock) -> None:
#         if affordance.is_applicable(source, target):
#             # Apply the affordance, which may change the positions or states of the entities
#             affordance.apply(source, target)

#             self.sync_positions()



#     def is_within_bounds(self, position: Tuple[int, int, int]) -> bool:
#         if not self.map_size:
#             raise ValueError("Map size not set")
#         x, y, _ = position
#         max_x, max_y = self.map_size
#         return 0 <= x < max_x and 0 <= y < max_y
    

#     def get_adjacent_positions(self, position: Tuple[int, int, int], range_val: int = 1, include_diagonals: bool = False, consider_z: bool = False) -> List[Tuple[int, int, int]]:
#         x, y, z = position
#         adjacent_positions = []

#         # Determine the bounds for the loops
#         x_min, y_min, z_min = max(x - range_val, 0), max(y - range_val, 0), z - range_val if consider_z else z
#         x_max, y_max, z_max = min(x + range_val, self.map_size[0] - 1 if self.map_size else x + range_val), \
#                             min(y + range_val, self.map_size[1] - 1 if self.map_size else y + range_val), \
#                             z + range_val if consider_z else z

#         for dx in range(x_min - x, x_max - x + 1):
#             for dy in range(y_min - y, y_max - y + 1):
#                 for dz in (range(z_min - z, z_max - z + 1) if consider_z else [0]):
#                     if dx == 0 and dy == 0 and dz == 0:
#                         continue  # Skip the original position
#                     if not include_diagonals and abs(dx) + abs(dy) > 1:
#                         continue  # Skip diagonals if not included
#                     new_position = (x + dx, y + dy, z + dz)
#                     adjacent_positions.append(new_position)

#         return adjacent_positions
    

#     def neighbors(self, position: Tuple[int, int, int], check_blocks_move = True) -> List[Tuple[int, int, int]]:
#         x, y, z = position
#         candidates = [
#             (x - 1, y, z), (x + 1, y, z), 
#             (x, y - 1, z), (x, y + 1, z),
#             (x - 1, y - 1, z), (x - 1, y + 1, z),
#             (x + 1, y - 1, z), (x + 1, y + 1, z),
#             # Include vertical neighbors if needed
#         ]
#         condition = self.is_within_bounds(pos) and not self.blocks_move[pos] if check_blocks_move else self.is_within_bounds(pos)
#         valid_neighbors = []
#         for pos in candidates:
#             if condition:
#                 valid_neighbors.append(pos)

#         return valid_neighbors
    
#     def cast_light(self, origin: Tuple[int, int, int], max_radius: int, angle: float) -> List[Tuple[int, int, int]]:
#         x0, y0, z0 = origin
#         # Assuming the angle and max_radius only affect x and y for simplicity
#         x1 = x0 + int(max_radius * math.cos(angle))
#         y1 = y0 + int(max_radius * math.sin(angle))

#         dx, dy = abs(x1 - x0), abs(y1 - y0)
#         x, y, z = x0, y0, z0
#         n = 1 + dx + dy
#         x_inc = 1 if x1 > x0 else -1
#         y_inc = 1 if y1 > y0 else -1
#         error = dx - dy
#         dx *= 2
#         dy *= 2

#         line_points = []
#         first_iteration = True
#         for _ in range(n):
#             if self.is_within_bounds((x, y, z)):
#                 line_points.append((x, y, z))
#                 if not first_iteration and self.blocks_los.get((x, y, z), False):
#                     break
#             first_iteration = False

#             if error > 0:
#                 x += x_inc
#                 error -= dy
#             else:
#                 y += y_inc
#                 error += dx

#         return line_points
    
#     def line(self, start: Tuple[int, int, int], end: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
#         dx, dy = end[0] - start[0], end[1] - start[1]
#         distance = math.sqrt(dx * dx + dy * dy)
#         angle = math.atan2(dy, dx)
#         return self.cast_light(start, math.ceil(distance), angle)
    
#     def line_of_sight(self, start: Tuple[int, int, int], end: Tuple[int, int, int]) -> bool:
#         line_points = self.line(start, end)
        
#         # Skip the starting point and iterate through the rest of the points
#         for point in line_points[1:]:
#             if self.blocks_los.get(point, False):
#                 return False

#         return True
    
#     def shadow_casting(self, origin: Tuple[int, int, int], max_radius: int = None) -> List[Tuple[int, int, int]]:
#         max_radius = max_radius or max(self.map_size)
#         visible_cells = [origin]

#         step_size = 0.5  # Decrease the step size for better accuracy
#         for angle in range(int(360 / step_size)):  # Adjust the loop range based on the new step size
#             visible_cells.extend(self.cast_light(origin, max_radius, math.radians(angle * step_size)))

#         return visible_cells
    
#     def a_star(self, start: Tuple[int, int, int], goal: Tuple[int, int, int]) -> Optional[List[Tuple[int, int, int]]]:
#         if not (isinstance(start, tuple) and isinstance(goal, tuple)):
#             raise TypeError("Start and goal must be tuples")

#         open_set = [(0, start)]  # The open set is a list of tuples (priority, position)
#         came_from: Dict[Tuple[int, int, int], Tuple[int, int, int]] = {}
#         g_score: Dict[Tuple[int, int, int], int] = {start: 0}
#         f_score: Dict[Tuple[int, int, int], int] = {start: self.heuristic(start, goal)}

#         while open_set:
#             current = heapq.heappop(open_set)[1]
#             if current == goal:
#                 path = []
#                 while current in came_from:
#                     path.append(current)
#                     current = came_from[current]
#                 path.reverse()
#                 return path

#             for neighbor in self.neighbors(current):
#                 tentative_g_score = g_score[current] + 1  # Assuming uniform cost
#                 if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
#                     came_from[neighbor] = current
#                     g_score[neighbor] = tentative_g_score
#                     f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
#                     if (f_score[neighbor], neighbor) not in open_set:
#                         heapq.heappush(open_set, (f_score[neighbor], neighbor))

#         return None  # No path found
    
#     def dijkstra(self, start: Tuple[int, int, int], max_distance: int) -> Dict[Tuple[int, int, int], int]:
#         if not isinstance(start, tuple):
#             raise TypeError("Start must be a tuple")

#         distances: Dict[Tuple[int, int, int], int] = {start: 0}
#         unvisited = [(0, start)]  # The unvisited set is a list of tuples (distance, position)

#         while unvisited:
#             current_distance, current_position = heapq.heappop(unvisited)
#             if current_distance > max_distance:
#                 continue

#             for neighbor in self.neighbors(current_position):
#                 new_distance = current_distance + 1  # Assuming uniform cost between nodes
#                 if neighbor not in distances or new_distance < distances[neighbor]:
#                     distances[neighbor] = new_distance
#                     heapq.heappush(unvisited, (new_distance, neighbor))

#         return distances
    
#     def get_all_entities(self) -> List[StateBlock]:
#         all_entities = []
#         for entity_list in self.entities.values():
#             for entity in entity_list:
#                 all_entities.append(entity)
#                 all_entities.extend(entity.inventory)
#         return all_entities
    
#     def print_entities(self):
#         print("Printing entities for gridmap: "+self.name)
#         time_since_creation = time.time() - self.creation_time
#         print("Time since creation: "+str(time_since_creation))
#         for key,entity_list in self.entities.items():
#         # print(key,len(entity_list))
#             for entity in entity_list:
#                 print(entity.name, entity.position)