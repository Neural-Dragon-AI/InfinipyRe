from typing import Dict, List, Tuple, Optional, Callable, Union, TYPE_CHECKING
from infinipy.stateblock import StateBlock
from infinipy.statement import Statement, CompositeStatement, RelationalStatement, CompositeRelationalStatement
from infinipy.transformer import Transformer, CompositeTransformer, RelationalTransformer, CompositeRelationalTransformer
from infinipy.affordance import Affordance
import math
import random
import heapq

class GridMap:
    def __init__(self, map_size: Optional[Tuple[int, int]] = None):
        self.entities: Dict[Tuple[int, int, int], List[StateBlock]] = {}
        self.map_size: Optional[Tuple[int, int]] = map_size
        self.blocks_move: Dict[Tuple[int, int, int], bool] = {}
        self.blocks_los: Dict[Tuple[int, int, int], bool] = {}
    
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

    def add_entity(self, entity: StateBlock, position: Tuple[int, int, int]) -> None:
        if self.map_size and not self.is_within_bounds(position):
            raise ValueError("Position out of bounds")
        
        self.entities.setdefault(position, []).append(entity)
        entity.position = position
        for item in entity.inventory:
            self._update_stored_item_position(item, position)
        self._update_blocks_mappings(position, entity)

    def remove_entity(self, entity: StateBlock) -> None:
        position = entity.position
        if position in self.entities:
            self.entities[position].remove(entity)
            if not self.entities[position]:
                del self.entities[position]
        for item in entity.inventory:
            self._remove_stored_item(item)
        self._resync_blocks_at_position(position)

    def move_entity(self, entity: StateBlock, new_position: Tuple[int, int, int]) -> None:
        if self.map_size and not self.is_within_bounds(new_position):
            raise ValueError("New position out of bounds")
        old_position = entity.position
        self.remove_entity(entity)
        self.add_entity(entity, new_position)
        for item in entity.inventory:
            self._update_stored_item_position(item, new_position)
        self._resync_blocks_at_position(old_position)
        self._update_blocks_mappings(new_position, entity)

    def get_entities_at_position(self, position: Tuple[int, int, int]) -> List[StateBlock]:
        entities = self.entities.get(position, [])
        all_entities = []
        for entity in entities:
            all_entities.append(entity)
            all_entities.extend(entity.inventory)
        return all_entities

    def find_entities_by_statement(self, statement: Statement, target: Optional[Statement]) -> List[StateBlock]:
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

    def _update_stored_item_position(self, item: StateBlock, position: Tuple[int, int, int]) -> None:
        if item.stored_in:
            self.entities.setdefault(position, []).append(item)
            item.position = position

    def _remove_stored_item(self, item: StateBlock) -> None:
        if item.position in self.entities:
            self.entities[item.position].remove(item)
            if not self.entities[item.position]:
                del self.entities[item.position]

    def sync_positions(self) -> None:
        for position, entities in list(self.entities.items()):
            for entity in entities:
                if entity.position != position:
                    self.move_entity(entity, entity.position)
                for item in entity.inventory:
                    self._update_stored_item_position(item, entity.position)

    def get_adjacent_positions(self, position: Tuple[int, int, int], range: int = 1, include_diagonals: bool = False, consider_z: bool = False) -> List[Tuple[int, int, int]]:
        x, y, z = position
        adjacent_positions = []

        # Determine the bounds for the loops
        x_min, y_min, z_min = max(x - range, 0), max(y - range, 0), z - range if consider_z else z
        x_max, y_max, z_max = min(x + range, self.map_size[0] - 1 if self.map_size else x + range), \
                            min(y + range, self.map_size[1] - 1 if self.map_size else y + range), \
                            z + range if consider_z else z

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


    def execute_affordance(self, affordance: Affordance, source: StateBlock, target: StateBlock) -> None:
        if affordance.is_applicable(source, target):
            affordance.apply(source, target)

    def is_within_bounds(self, position: Tuple[int, int, int]) -> bool:
        if not self.map_size:
            return True
        x, y, _ = position
        max_x, max_y = self.map_size
        return 0 <= x < max_x and 0 <= y < max_y

    def neighbors(self, position: Tuple[int, int, int]) -> List[Tuple[int, int, int]]:
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
            if self.is_within_bounds(pos) and not self.blocks_move[pos]:
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