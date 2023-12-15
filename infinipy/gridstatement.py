from infinipy.worldstatement import WorldStatement
from infinipy.stateblock import StateBlock
from infinipy.statement import Statement,CompositeStatement
from typing import Dict, List, Tuple, Optional
import heapq
import math
#l


class GridStatement:
    def __init__(self, WorldStatement: WorldStatement, spatial_registry: dict,statement_registry:Dict[str,Statement] ):
        self.worldstatement = WorldStatement
        self.spatial_registry = spatial_registry
        self.position_dict = self.create_position_dict()
        self.statement_registry = statement_registry
        self.los_dict = self.create_los_dict()
        self.move_dict = self.create_move_dict()
        self.max_height = max([pos[1] for pos in self.spatial_registry.keys()])
        self.max_width = max([pos[0] for pos in self.spatial_registry.keys()])
        self.path_dict = self.create_path_dict()
        self.distance_dict = self.create_distance_dict()
        self.ray_dict = self.precompute_rays()

    def blocks_move(self,position:Tuple[int,int])->bool:
        return self.move_dict[position]
    
    def blocks_los(self,position:Tuple[int,int])->bool:
        return self.los_dict[position]
    
    def create_position_dict(self):
        position_dict = {}
        #we need to go through each key in the worlstatement and check if the
        # statetemetn of the position dict is true
        for entity_tuple, composite_statement in self.worldstatement.conditions.items():
            for pos,statement in self.spatial_registry.items():
                if composite_statement.validates(statement):
                    if pos in position_dict:
                        position_dict[pos].append(entity_tuple)
                    else:
                        position_dict[pos]=[entity_tuple]
        return position_dict
    
    def create_los_dict(self):
        blocks_los = CompositeStatement([(self.statement_registry["blocks_los_is_true"],True)])
        
        los_dict = {keys:True for keys in self.spatial_registry.keys()}
        already_checked = set()
        for pos,entities_at_pos in self.position_dict.items():
            if pos in already_checked:
                continue
            already_checked.add(pos)
            entities_statements = [self.worldstatement.conditions[entity] for entity in entities_at_pos]
            #flatten the list of lists
            print(entities_statements)
            any_blocks_los = not any([blocks_los.is_validated_by(statement) for statement in entities_statements])
            los_dict[pos]= any_blocks_los
        return los_dict
    
    def create_move_dict(self):
        
        blocks_move = CompositeStatement([(self.statement_registry["blocks_move_is_true"],True)])
        move_dict = {keys:False for keys in self.spatial_registry.keys()}
        already_checked = set()
        for pos,entities_at_pos in self.position_dict.items():
            if pos in already_checked:
                continue
            already_checked.add(pos)
            entities_statements = [self.worldstatement.conditions[entity] for entity in entities_at_pos]
            #flatten the list of lists
            any_blocks_move = not any([blocks_move.is_validated_by(statement) for statement in entities_statements])
            move_dict[pos]= any_blocks_move
        return move_dict
    
    def create_path_dict(self):
        path_dict = {}
        for pos_start in self.spatial_registry.keys():
            for pos_end in self.spatial_registry.keys():
                if (pos_end,pos_start) in path_dict:
                    path_dict[(pos_start,pos_end)] = path_dict[(pos_end,pos_start)]
                elif pos_start == pos_end:
                    path_dict[(pos_start,pos_end)] = []
                else:
                    path_dict[(pos_start,pos_end)] = self.a_star(pos_start,pos_end)
        return path_dict
    
    def create_distance_dict(self):
        distance_dict = {}
        for key in self.spatial_registry.keys():
            for key2 in self.spatial_registry.keys():
                if (key2,key) in distance_dict:
                    distance_dict[(key,key2)] = distance_dict[(key2,key)]
                elif key != key2:
                    distance_dict[(key,key2)] = self.distance(key,key2)
                else:
                    distance_dict[(key,key2)] = 0
                    
    def create_cansee_dict(self):
        cansee_dict = {}
        for pos_start in self.spatial_registry.keys():
            for pos_end in self.spatial_registry.keys():
                if (pos_end,pos_start) in cansee_dict:
                    cansee_dict[(pos_start,pos_end)] = cansee_dict[(pos_end,pos_start)]
                elif pos_start == pos_end:
                    cansee_dict[(pos_start,pos_end)] = True
                else:
                    cansee_dict[(pos_start,pos_end)] = self.line_of_sight(pos_start,pos_end)[0]
        return cansee_dict
            
    
    def is_within_bounds(self,position:Tuple[int,int])->bool:
        return position[0]>=0 and position[0]<=self.max_width and position[1]>=0 and position[1]<=self.max_height

    def get_neighbors(self,position:Tuple[int,int],allow_diagonal:bool = True,allow_blocks_move= True)->List[Tuple[int,int]]:
        candidates = [(position[0]+1,position[1]),(position[0]-1,position[1]),(position[0],position[1]+1),(position[0],position[1]-1)]
        if allow_diagonal:
            diagonal_candidates = [(position[0]+1,position[1]+1),(position[0]-1,position[1]+1),(position[0]+1,position[1]-1),(position[0]-1,position[1]-1)]
            candidates.extend(diagonal_candidates)
        #remove from candidates out of bounds
        candidates = [candidate for candidate in candidates if self.is_within_bounds(candidate)]
        if not allow_blocks_move:
            candidates = [candidate for candidate in candidates if self.move_dict[candidate]]
        return candidates
    
    def a_star(self, start: Tuple[int, int], goal: Tuple[int, int], allow_diagonal = True) -> Optional[List[Tuple[int, int]]]:
        if not (isinstance(start, tuple) and isinstance(goal, tuple)):
            raise TypeError("Start and goal must be tuples")

        open_set = [(0, start)]  # The open set is a list of tuples (priority, position)
        came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
        g_score: Dict[Tuple[int, int], int] = {start: 0}
        f_score: Dict[Tuple[int, int], int] = {start: self.heuristic(start, goal)}

        while open_set:
            current = heapq.heappop(open_set)[1]
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path

            for neighbor in self.get_neighbors(current, allow_diagonal,allow_blocks_move = False):
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

    
    def dijkstra(self, start: Tuple[int, int], max_distance: int, allow_diagonal = True) -> Dict[Tuple[int, int], int]:
        if not isinstance(start, tuple):
            raise TypeError("Start must be a tuple")

        distances: Dict[Tuple[int, int], int] = {start: 0}
        unvisited = [(0, start)]  # The unvisited set is a list of tuples (distance, position)

        while unvisited:
            current_distance, current_position = heapq.heappop(unvisited)
            if current_distance > max_distance:
                continue

            for neighbor in self.get_neighbors(current_position, allow_diagonal,allow_blocks_move = False):
                new_distance = current_distance + 1  # Assuming uniform cost between nodes
                if neighbor not in distances or new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    heapq.heappush(unvisited, (new_distance, neighbor))

        return distances
    
    def floyd_warshall(self, allows_diagonal: bool = False):
        grid_size = (self.max_width+1, self.max_height+1)
        num_vertices = grid_size[0] * grid_size[1]
        inf = float('inf')

        # Initialize distance and path matrices
        dist = [[inf] * num_vertices for _ in range(num_vertices)]
        path = [[-1] * num_vertices for _ in range(num_vertices)]

        # Initialize distances for adjacent nodes and same node
        for x in range(grid_size[0]):
            for y in range(grid_size[1]):
                idx = x * grid_size[1] + y
                dist[idx][idx] = 0  # Distance to self is zero

                # Use get_neighbors to determine moveable neighbors
                neighbors = self.get_neighbors((x, y), allow_diagonal=allows_diagonal, allow_blocks_move=True)
                for nx, ny in neighbors:
                    neighbor_idx = nx * grid_size[1] + ny
                    dist[idx][neighbor_idx] = 1  # Distance to moveable neighbor is 1
                    path[idx][neighbor_idx] = neighbor_idx

        # Floyd-Warshall algorithm
        for k in range(num_vertices):
            for i in range(num_vertices):
                for j in range(num_vertices):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        path[i][j] = path[i][k]

        # Reconstruct paths and create dictionary
        paths_dict = {}
        for i in range(num_vertices):
            for j in range(num_vertices):
                if i != j and path[i][j] != -1:
                    start_pos = (i // grid_size[1], i % grid_size[1])
                    end_pos = (j // grid_size[1], j % grid_size[1])
                    path_sequence = []
                    while i != j:
                        i = path[i][j]
                        path_sequence.append((i // grid_size[1], i % grid_size[1]))
                    paths_dict[(start_pos, end_pos)] = path_sequence

        return paths_dict
    
    def cast_light(self, origin: Tuple[int, int], max_radius: int, angle: float) -> List[Tuple[int, int, int]]:
        x0, y0 = origin
        # Assuming the angle and max_radius only affect x and y for simplicity
        x1 = x0 + int(max_radius * math.cos(angle))
        y1 = y0 + int(max_radius * math.sin(angle))

        dx, dy = abs(x1 - x0), abs(y1 - y0)
        x, y = x0, y0
        n = 1 + dx + dy
        x_inc = 1 if x1 > x0 else -1
        y_inc = 1 if y1 > y0 else -1
        error = dx - dy
        dx *= 2
        dy *= 2

        line_points = []
        first_iteration = True
        for _ in range(n):
            if self.is_within_bounds((x, y)):
                line_points.append((x, y))
                if not first_iteration and self.blocks_los((x, y)):
                    break
            first_iteration = False

            if error > 0:
                x += x_inc
                error -= dy
            else:
                y += y_inc
                error += dx

        return line_points
    
    def line(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        return self.ray_dict.get((start, end), [])

    def line_of_sight(self, start: Tuple[int, int], end: Tuple[int, int]) -> Tuple[bool, List[Tuple[int, int]]]:
        line_points = self.line(start, end)
        visible_points = []
        for point in line_points[1:]:
            if self.blocks_los(point):
                return False, visible_points
            visible_points.append(point)
        return True, visible_points

    def shadow_casting(self, origin: Tuple[int, int], max_radius: int = None) -> List[Tuple[int, int]]:
        max_radius = max_radius or max(self.max_height, self.max_width)
        visible_cells = [origin]
        for end in self.spatial_registry.keys():
            if self.get_distance(origin, end) <= max_radius:
                line_points = self.line(origin, end)
                for point in line_points[1:]:
                    if self.blocks_los(point):
                        break
                    visible_cells.append(point)
        return list(set(visible_cells))
    
    def distance(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
    
    def get_distance(self, start: Tuple[int, int], end: Tuple[int, int]) -> int:
        return self.distance_dict[(start,end)]
    
    def precompute_rays(self):
        rays = {}
        for start in self.spatial_registry.keys():
            for end in self.spatial_registry.keys():
                if start != end:
                    rays[(start, end)] = self.compute_ray(start, end)
        return rays

    def compute_ray(self, start: Tuple[int, int], end: Tuple[int, int]) -> List[Tuple[int, int]]:
        dx, dy = end[0] - start[0], end[1] - start[1]
        distance = self.get_distance(start, end)
        angle = math.atan2(dy, dx)
        return self.cast_light(start, int(math.ceil(distance)), angle)

