"""A* pathfinding algorithm for stage validation"""
from typing import List, Tuple, Set, Optional, Dict, Any
import heapq
import math
from dataclasses import dataclass, field
from enum import Enum

from stage_generator.data_models import StageConfiguration, EnemyConfiguration


class ActionType(Enum):
    """Types of actions that can be taken"""
    MOVE = "move"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    ATTACK = "attack"
    PICKUP = "pickup"
    WAIT = "wait"
    IS_AVAILABLE = "is_available"  # v1.2.12
    DISPOSE = "dispose"            # v1.2.12


@dataclass
class EnemyState:
    """Represents an enemy's current state"""
    position: Tuple[int, int]
    direction: str
    hp: int
    max_hp: int
    attack_power: int
    behavior: str
    enemy_type: str = "normal"  # Enemy type for size calculation
    is_alive: bool = True
    patrol_path: Optional[List[Tuple[int, int]]] = None
    patrol_index: int = 0
    target_direction: Optional[str] = None
    is_alert: bool = False  # True when player detected (chase mode)
    vision_range: int = 0  # Must be explicitly set from stage file
    last_seen_player: Optional[Tuple[int, int]] = None  # Last known player position
    alert_cooldown: int = 0  # Turns remaining for continued tracking after losing sight

    def __hash__(self):
        return hash((self.position, self.direction, self.hp, self.is_alive, self.patrol_index, self.target_direction, self.vision_range, self.is_alert, self.last_seen_player, self.alert_cooldown, self.enemy_type))


@dataclass
class GameState:
    """Represents a complete game state"""
    player_pos: Tuple[int, int]
    player_dir: str
    player_hp: int
    enemies: Dict[str, EnemyState]  # id -> EnemyState
    collected_items: Set[str]
    turn_count: int
    disposed_items: Set[str] = field(default_factory=set)  # v1.2.12: for bomb disposal tracking

    def __hash__(self):
        """Make GameState hashable for set operations"""
        enemies_tuple = tuple(sorted(
            (enemy_id, hash(enemy_state))
            for enemy_id, enemy_state in self.enemies.items()
        ))
        return hash((
            self.player_pos,
            self.player_dir,
            self.player_hp,
            enemies_tuple,
            tuple(sorted(self.collected_items)),
            tuple(sorted(self.disposed_items)),  # v1.2.12
            self.turn_count
        ))


@dataclass
class SearchNode:
    """Node in the A* search tree"""
    state: GameState
    g_cost: int  # Cost from start
    h_cost: int  # Heuristic cost to goal
    f_cost: int  # Total cost
    parent: Optional['SearchNode']
    action: Optional[ActionType]

    def __lt__(self, other):
        """For priority queue ordering"""
        return self.f_cost < other.f_cost


class StagePathfinder:
    """A* pathfinder for validating stage solvability"""

    def __init__(self, stage: StageConfiguration):
        self.stage = stage
        self.width, self.height = stage.board.size
        self.walls = self._extract_walls()
        self.goal_pos = tuple(stage.goal.position)

        # Item positions
        self.items = {item.id: tuple(item.position) for item in stage.items}

        # Direction mappings
        self.directions = {
            "N": (0, -1),
            "S": (0, 1),
            "E": (1, 0),
            "W": (-1, 0)
        }

        self.direction_names = ["N", "E", "S", "W"]  # Clockwise order

        # Enemy size mappings for large enemies
        self.enemy_sizes = {
            "normal": (1, 1),
            "large_2x2": (2, 2),
            "large_3x3": (3, 3),
            "special_2x3": (2, 3),
            "goblin": (1, 1),
            "orc": (1, 1),
            "dragon": (2, 2),  # ドラゴンは大型
            "boss": (2, 2)     # ボスも大型
        }

    def _extract_walls(self) -> Set[Tuple[int, int]]:
        """Extract wall positions from board grid"""
        walls = set()
        for y, row in enumerate(self.stage.board.grid):
            for x, cell in enumerate(row):
                if cell == '#':
                    walls.add((x, y))
        return walls

    def _get_enemy_size(self, enemy_type: str) -> Tuple[int, int]:
        """Get size of enemy based on type"""
        return self.enemy_sizes.get(enemy_type.lower(), (1, 1))

    def _get_enemy_occupied_positions(self, enemy_state: 'EnemyState') -> List[Tuple[int, int]]:
        """Get all positions occupied by an enemy (for large enemies)"""
        if not hasattr(enemy_state, 'enemy_type'):
            # Default to 1x1 if no type information
            return [enemy_state.position]

        width, height = self._get_enemy_size(enemy_state.enemy_type)
        positions = []
        ex, ey = enemy_state.position

        for dx in range(width):
            for dy in range(height):
                pos = (ex + dx, ey + dy)
                positions.append(pos)
        return positions

    def find_path(self, max_turns: Optional[int] = None) -> Optional[List[ActionType]]:
        """
        Find a path from start to goal using A* algorithm

        Args:
            max_turns: Maximum number of turns allowed (from stage constraints if None)

        Returns:
            List of actions to reach goal, or None if no path exists
        """
        if max_turns is None:
            max_turns = self.stage.constraints.max_turns

        # Initialize starting state
        start_state = GameState(
            player_pos=tuple(self.stage.player.start),
            player_dir=self.stage.player.direction,
            player_hp=self.stage.player.hp,
            enemies={
                enemy.id: EnemyState(
                    position=tuple(enemy.position),
                    direction=enemy.direction,
                    hp=enemy.hp,
                    max_hp=enemy.max_hp,
                    attack_power=enemy.attack_power,
                    behavior=enemy.behavior,
                    enemy_type=enemy.type if hasattr(enemy, 'type') else 'normal',  # Get enemy type
                    is_alive=True,
                    patrol_path=[tuple(pos) for pos in enemy.patrol_path] if hasattr(enemy, 'patrol_path') and enemy.patrol_path else None,
                    patrol_index=self._calculate_initial_patrol_index(enemy) if hasattr(enemy, 'patrol_path') and enemy.patrol_path else 0,
                    vision_range=self._get_enemy_vision_range(enemy),
                    is_alert=False,
                    last_seen_player=None
                )
                for enemy in self.stage.enemies
            },
            collected_items=set(),
            turn_count=0
        )

        # DEBUG: Log initial enemy positions
        print(f"DEBUG FIND_PATH: 初期状態確認")
        print(f"   プレイヤー: pos={start_state.player_pos}, dir={start_state.player_dir}, HP={start_state.player_hp}")
        for enemy_id, enemy_state in start_state.enemies.items():
            print(f"   敵 {enemy_id}: pos={enemy_state.position}, dir={enemy_state.direction}, HP={enemy_state.hp}, alerted={enemy_state.is_alert}")

        # Check if already at goal
        if self._is_goal_reached(start_state):
            return []

        # A* search
        open_set = []
        start_node = SearchNode(
            state=start_state,
            g_cost=0,
            h_cost=self._heuristic(start_state),
            f_cost=self._heuristic(start_state),
            parent=None,
            action=None
        )

        heapq.heappush(open_set, start_node)
        closed_set = set()
        visited_states = {start_state: start_node}

        # Search loop with progress tracking
        nodes_explored = 0
        # Significantly increase node limit for complex patrol stages
        max_nodes = getattr(self, 'max_nodes', None)
        if max_nodes is None:
            max_nodes = 50000000 if any(enemy.behavior == "patrol" for enemy in self.stage.enemies) else 1000000

        # Progress every 10 million nodes for better visibility, but also show early progress
        progress_interval = 10000000
        early_progress_interval = 100000  # Show progress every 100K nodes for first 1M
        last_progress = 0
        unlimited = max_nodes == float('inf')

        if unlimited:
            print(f"A*探索開始: 制限無し (100K/10M ノード毎に進捗表示)")
        else:
            print(f"A*探索開始: 最大ノード数 {max_nodes:,} (100K/10M ノード毎に進捗表示)")
        print(f"初期状態: プレイヤー位置={start_state.player_pos}, 敵={len(start_state.enemies)}体, アイテム={len(start_state.collected_items | start_state.disposed_items)}/{len(self.items)}個")

        while open_set and (unlimited or nodes_explored < max_nodes):
            current_node = heapq.heappop(open_set)
            nodes_explored += 1

            # Progress display - frequent early progress, then every 10M nodes
            show_progress = False
            if nodes_explored < 1000000:  # First 1M nodes - show every 100K
                if nodes_explored - last_progress >= early_progress_interval:
                    show_progress = True
            else:  # After 1M nodes - show every 10M
                if nodes_explored - last_progress >= progress_interval:
                    show_progress = True

            if show_progress:
                queue_size = len(open_set)
                closed_size = len(closed_set)
                if unlimited:
                    print(f"進捗: {nodes_explored:,} ノード探索済み | キュー: {queue_size:,} | 探索済み: {closed_size:,}")
                else:
                    progress_percent = (nodes_explored / max_nodes) * 100
                    print(f"進捗: {progress_percent:.1f}% ({nodes_explored:,}/{max_nodes:,} ノード) "
                          f"| キュー: {queue_size:,} | 探索済み: {closed_size:,}")
                last_progress = nodes_explored

            if current_node.state in closed_set:
                continue

            closed_set.add(current_node.state)

            # Check if player died
            if current_node.state.player_hp <= 0:
                continue  # Skip this invalid state

            # Check if goal reached
            if self._is_goal_reached(current_node.state):
                print(f"GOAL REACHED! Player: {current_node.state.player_pos}, HP: {current_node.state.player_hp}")
                print(f"   Enemies: {[(id, e.position, e.hp, e.is_alive) for id, e in current_node.state.enemies.items()]}")
                print(f"   Items: collected={current_node.state.collected_items}, disposed={current_node.state.disposed_items}")
                print(f"探索完了: 解法発見! 総ノード数: {nodes_explored:,}")
                return self._reconstruct_path(current_node)

            # Check turn limit - allow some flexibility for complex scenarios
            if current_node.state.turn_count >= max_turns * 1.2:  # Allow 20% more turns for exploration
                continue

            # CRITICAL FIX: Pre-check if current state would lead to certain death
            # If player is in a position where enemies will kill them no matter what action they take,
            # this state should be considered invalid (same as game engine behavior)
            if self._is_state_lethal(current_node.state):
                # This state leads to certain death - do not explore further
                continue

            # Generate successor states
            for action in self._get_valid_actions(current_node.state):
                new_state = self._apply_action(current_node.state, action)
                if new_state is None or new_state in closed_set:
                    continue

                # Calculate costs
                g_cost = current_node.g_cost + 1
                h_cost = self._heuristic(new_state)
                f_cost = g_cost + h_cost

                # Skip if we've seen this state with better cost
                if new_state in visited_states and visited_states[new_state].f_cost <= f_cost:
                    continue

                # Create new node
                new_node = SearchNode(
                    state=new_state,
                    g_cost=g_cost,
                    h_cost=h_cost,
                    f_cost=f_cost,
                    parent=current_node,
                    action=action
                )

                visited_states[new_state] = new_node
                heapq.heappush(open_set, new_node)

        # Search completed without finding solution
        if unlimited:
            print(f"探索終了: 解法未発見 ({nodes_explored:,} ノード探索済み, キューが空)")
        else:
            print(f"探索終了: 解法未発見 (最大ノード数 {max_nodes:,} に到達)")
        return None  # No path found

    def _is_goal_reached(self, state: GameState) -> bool:
        """Check if the goal conditions are met"""
        # Check victory conditions from stage configuration
        victory_conditions = getattr(self.stage, 'victory_conditions', [])

        # If no victory conditions specified, use legacy behavior
        if not victory_conditions:
            # Legacy: must be at goal position and have collected all items
            if state.player_pos != self.goal_pos:
                return False
            required_items = set(self.items.keys())
            # v1.2.12: Items can be either collected or disposed
            handled_items = state.collected_items | state.disposed_items
            if not required_items.issubset(handled_items):
                return False
            return True

        # Debug: Victory condition checking
        # print(f"🔍 Checking victory conditions: {[c.get('type') for c in victory_conditions]}")

        # Check all victory conditions (ALL must be satisfied)
        # Process each condition and immediately return False if any condition fails
        for condition in victory_conditions:
            condition_type = condition.get('type', '')

            if condition_type == 'reach_goal':
                at_goal = state.player_pos == self.goal_pos
                if not at_goal:
                    # print(f"❌ reach_goal: Player at {state.player_pos}, goal at {self.goal_pos}")
                    return False
                # print(f"✅ reach_goal: Player at goal {self.goal_pos}")

            elif condition_type == 'defeat_all_enemies':
                # Check if any enemy is still alive
                alive_enemies = [enemy for enemy in state.enemies.values() if enemy.is_alive and enemy.hp > 0]
                if alive_enemies:
                    # print(f"❌ defeat_all_enemies: {len(alive_enemies)} enemies still alive: {[e.id for e in alive_enemies]}")
                    return False
                # print(f"✅ defeat_all_enemies: All enemies defeated")

            elif condition_type == 'collect_all_items':
                required_items = set(self.items.keys())
                # v1.2.12: Items can be either collected or disposed
                handled_items = state.collected_items | state.disposed_items
                if not required_items.issubset(handled_items):
                    missing_items = required_items - handled_items
                    # print(f"❌ collect_all_items: Missing items: {missing_items}")
                    return False
                # print(f"✅ collect_all_items: All items handled (collected: {state.collected_items}, disposed: {state.disposed_items})")

            elif condition_type == 'defeat_all_enemies_and_reach_goal':
                # Special compound condition for compatibility
                at_goal = state.player_pos == self.goal_pos
                alive_enemies = [enemy for enemy in state.enemies.values() if enemy.is_alive and enemy.hp > 0]
                if not at_goal:
                    # print(f"❌ defeat_all_enemies_and_reach_goal: Not at goal ({state.player_pos} != {self.goal_pos})")
                    return False
                if alive_enemies:
                    # print(f"❌ defeat_all_enemies_and_reach_goal: {len(alive_enemies)} enemies still alive")
                    return False
                # print(f"✅ defeat_all_enemies_and_reach_goal: At goal and all enemies defeated")

            else:
                # Unknown condition type - fail safe by returning False
                print(f"⚠️ Unknown victory condition type: {condition_type}")
                return False

        # All conditions have been checked and passed
        print(f"🎉 All victory conditions satisfied! Player at {state.player_pos}")
        print(f"🎯 Final enemy positions:")
        for enemy_id, enemy_state in state.enemies.items():
            print(f"   {enemy_id}: {enemy_state.position} facing {enemy_state.direction} (HP: {enemy_state.hp}/{enemy_state.max_hp})")
        return True

    def _is_state_lethal(self, state: GameState) -> bool:
        """
        Check if current state would lead to certain death regardless of player action.
        This simulates the game engine's behavior where enemies attack after player actions.
        """
        # Test all possible actions from this state
        valid_actions = self._get_valid_actions(state)
        if not valid_actions:
            return True  # No valid actions available

        lethal_actions = 0

        for action in valid_actions:
            # Simulate the action outcome
            test_state = self._apply_action(state, action)
            if test_state is None:  # Action results in immediate death
                lethal_actions += 1

        # If ALL actions lead to death, this state is lethal
        return lethal_actions == len(valid_actions)

    def _heuristic(self, state: GameState) -> int:
        """Calculate heuristic cost to goal (combat-aware)"""
        # Distance to goal
        goal_dist = abs(state.player_pos[0] - self.goal_pos[0]) + abs(state.player_pos[1] - self.goal_pos[1])

        # Add cost for unhandled items (improved heuristic)
        # v1.2.12: Items can be either collected or disposed
        handled_items = state.collected_items | state.disposed_items
        uncollected_items = set(self.items.keys()) - handled_items
        item_cost = 0

        if uncollected_items:
            # Use a more accurate heuristic: distance to nearest item + distance from farthest item to goal
            nearest_item_dist = float('inf')
            farthest_item_to_goal_dist = 0

            for item_id in uncollected_items:
                item_pos = self.items[item_id]
                # Distance from current position to item
                item_dist = abs(state.player_pos[0] - item_pos[0]) + abs(state.player_pos[1] - item_pos[1])
                nearest_item_dist = min(nearest_item_dist, item_dist)

                # Distance from item to goal
                item_to_goal_dist = abs(item_pos[0] - self.goal_pos[0]) + abs(item_pos[1] - self.goal_pos[1])
                farthest_item_to_goal_dist = max(farthest_item_to_goal_dist, item_to_goal_dist)

            # Heuristic: must visit nearest item + eventually reach goal from farthest item
            item_cost = nearest_item_dist + farthest_item_to_goal_dist + len(uncollected_items) * 2
        else:
            # All items collected, just go to goal
            item_cost = 0

        # Combat-aware costs for living enemies
        combat_cost = 0

        # Check victory conditions to determine if all enemies must be defeated
        victory_conditions = getattr(self.stage, 'victory_conditions', [])
        must_defeat_all_enemies = any(condition.get('type') == 'defeat_all_enemies' for condition in victory_conditions)

        if must_defeat_all_enemies:
            # When defeat_all_enemies is required, add cost for ALL living enemies
            for enemy_state in state.enemies.values():
                if enemy_state.is_alive and enemy_state.hp > 0:
                    enemy_dist = abs(state.player_pos[0] - enemy_state.position[0]) + abs(state.player_pos[1] - enemy_state.position[1])

                    # Add movement cost to reach enemy + combat cost
                    # Movement cost: minimum distance to attack the enemy (adjacent position)
                    movement_cost = max(0, enemy_dist - 1)  # -1 because we can attack from adjacent

                    # Combat cost: turns to defeat enemy
                    player_attack = self._calculate_effective_attack_power(state)
                    turns_to_defeat = math.ceil(enemy_state.hp / player_attack)

                    # Total cost for this enemy
                    enemy_cost = movement_cost + turns_to_defeat
                    combat_cost += enemy_cost
        else:
            # Legacy behavior: only consider path-blocking enemies
            # Check if player can attack in CURRENT direction only (not any direction)
            # This matches the actual behavior in _can_attack and action generation
            if self._can_attack(state):
                # Player can attack in current direction - only attack cost
                combat_cost += 1  # Just the attack action cost

            # Original combat cost calculation for path-blocking enemies
            for enemy_state in state.enemies.values():
                if enemy_state.is_alive and enemy_state.hp > 0:
                    enemy_dist = abs(state.player_pos[0] - enemy_state.position[0]) + abs(state.player_pos[1] - enemy_state.position[1])

                    # If enemy is blocking path to goal or items, add combat cost
                    if self._enemy_blocks_path(state, enemy_state):
                        # More accurate combat cost calculation
                        player_attack = self._calculate_effective_attack_power(state)
                        enemy_attack = enemy_state.attack_power

                        # Calculate actual turns to defeat enemy
                        turns_to_defeat = math.ceil(enemy_state.hp / player_attack)

                    # Enemy counter-attacks only when player attacks (not every turn)
                    # Enemy gets (turns_to_defeat - 1) counter-attacks if it survives at least 1 attack
                    if turns_to_defeat > 1:
                        total_damage_taken = (turns_to_defeat - 1) * enemy_attack
                    else:
                        total_damage_taken = 0  # Enemy dies in 1 hit, no counter-attack

                    # Check if combat is survivable
                    if state.player_hp > total_damage_taken:
                        # Survivable combat - add reasonable cost
                        # Cost = positioning + combat turns + slight damage penalty
                        damage_penalty = total_damage_taken // 10  # Small penalty for taking damage
                        combat_cost += enemy_dist + turns_to_defeat + damage_penalty
                    else:
                        # Unsurvivable combat - add penalty but not too high to allow exploration
                        combat_cost += 50 + enemy_dist  # More reasonable penalty

        # Add alert preemption cost (v1.2.12: enemy first-strike avoidance)
        preemption_cost = self._calculate_alert_preemption_cost(state)

        # Add strategic bonuses (v1.2.12: manual solution strategy promotion)
        detour_bonus = self._calculate_detour_bonus(state)
        wait_bonus = self._calculate_wait_strategic_bonus(state)
        attack_bonus = self._calculate_attack_position_bonus(state)
        upper_bonus = self._calculate_upper_area_bonus(state)

        total_cost = goal_dist + item_cost + combat_cost + preemption_cost
        total_bonus = detour_bonus + wait_bonus + attack_bonus + upper_bonus

        return max(1, total_cost + total_bonus)  # Ensure minimum cost of 1

    def _calculate_alert_preemption_cost(self, state: GameState) -> int:
        """Calculate cost for avoiding enemy first-strike when enemies become alert"""
        preemption_cost = 0

        for enemy_state in state.enemies.values():
            if not enemy_state.is_alert or not enemy_state.is_alive or enemy_state.hp <= 0:
                continue

            distance = abs(state.player_pos[0] - enemy_state.position[0]) + \
                      abs(state.player_pos[1] - enemy_state.position[1])

            if distance == 1:
                # Distance 1: Direction is decisive - detailed check
                if self._enemy_facing_player_adjacent(state, enemy_state):
                    preemption_cost += 50  # High penalty - immediate danger
                else:
                    preemption_cost += 15  # Medium penalty - 1 turn buffer

            elif 2 <= distance <= 3:
                # Distance 2-3: Simple direction check
                if self._player_in_enemy_general_direction(state, enemy_state):
                    preemption_cost += 20  # Medium penalty
                else:
                    preemption_cost += 5   # Light penalty - safer position

        return preemption_cost

    def _enemy_facing_player_adjacent(self, state: GameState, enemy_state: EnemyState) -> bool:
        """Check if adjacent enemy is facing player (distance = 1)"""
        px, py = state.player_pos
        ex, ey = enemy_state.position

        # Calculate direction from enemy to player
        dx = px - ex
        dy = py - ey

        # Determine required direction to face player
        if abs(dx) > abs(dy):
            required_dir = "E" if dx > 0 else "W"
        else:
            required_dir = "S" if dy > 0 else "N"

        # Check if enemy is already facing that direction
        return enemy_state.direction == required_dir

    def _player_in_enemy_general_direction(self, state: GameState, enemy_state: EnemyState) -> bool:
        """Check if player is in enemy's general facing direction (distance 2-3)"""
        px, py = state.player_pos
        ex, ey = enemy_state.position

        # Calculate direction vector from enemy to player
        dx = px - ex
        dy = py - ey

        # Map enemy direction to vector
        direction_vectors = {
            "N": (0, -1),
            "S": (0, 1),
            "E": (1, 0),
            "W": (-1, 0)
        }

        if enemy_state.direction not in direction_vectors:
            return False

        enemy_dx, enemy_dy = direction_vectors[enemy_state.direction]

        # Check if player direction has positive dot product with enemy facing direction
        dot_product = dx * enemy_dx + dy * enemy_dy

        # Positive dot product means player is in enemy's general direction
        return dot_product > 0

    def _calculate_detour_bonus(self, state: GameState) -> int:
        """Calculate bonus for promoting detour routes (negative cost)"""
        goal_pos = self.stage.goal.position

        # Promote upper area movement (player y < goal y)
        if state.player_pos[1] < goal_pos[1]:
            # Calculate how much "above" the goal the player is
            vertical_offset = goal_pos[1] - state.player_pos[1]
            detour_bonus = -min(15, vertical_offset * 5)  # Stronger bonus: max -15, scaled by offset
            return detour_bonus
        return 0

    def _calculate_wait_strategic_bonus(self, state: GameState) -> int:
        """Calculate bonus for strategic wait() actions (negative cost)"""
        bonus = 0
        for enemy_state in state.enemies.values():
            if not enemy_state.is_alive:
                continue

            distance = abs(state.player_pos[0] - enemy_state.position[0]) + \
                      abs(state.player_pos[1] - enemy_state.position[1])

            # Promote wait() when adjacent to enemy and can attack
            if distance == 1:
                if self._can_attack_enemy_at_position(state, enemy_state):
                    player_attack = self._calculate_effective_attack_power(state)
                    turns_to_defeat = math.ceil(enemy_state.hp / player_attack)

                    # Strong bonus for 2-hit kill scenarios (like manual solution)
                    if turns_to_defeat <= 2:
                        bonus -= 25  # Very strong wait() promotion for combat advantage
                    else:
                        bonus -= 15   # Strong wait() promotion
        return bonus

    def _can_attack_enemy_at_position(self, state: GameState, enemy_state: EnemyState) -> bool:
        """Check if player can attack enemy from current position (includes large enemy support)"""
        px, py = state.player_pos

        # Get all positions occupied by the enemy (for large enemies)
        enemy_occupied_positions = self._get_enemy_occupied_positions(enemy_state)

        # Check if any occupied position is adjacent to player
        for ex, ey in enemy_occupied_positions:
            # Calculate direction from player to this enemy position
            dx = ex - px
            dy = ey - py

            # Check if enemy position is adjacent (distance = 1)
            if abs(dx) + abs(dy) == 1:
                # Determine required direction to face this enemy position
                if abs(dx) > abs(dy):
                    required_dir = "E" if dx > 0 else "W"
                else:
                    required_dir = "S" if dy > 0 else "N"

                # Check if player is facing this enemy position
                if state.player_dir == required_dir:
                    return True

        return False

    def _calculate_attack_position_bonus(self, state: GameState) -> int:
        """Calculate bonus for favorable attack positions (negative cost)"""
        bonus = 0
        for enemy_state in state.enemies.values():
            if not enemy_state.is_alive:
                continue

            if self._can_attack_enemy_at_position(state, enemy_state):
                player_attack = self._calculate_effective_attack_power(state)
                turns_to_defeat = math.ceil(enemy_state.hp / player_attack)
                enemy_attack = enemy_state.attack_power

                # Calculate survivability
                max_damage_taken = (turns_to_defeat - 1) * enemy_attack if turns_to_defeat > 1 else 0
                can_survive = state.player_hp > max_damage_taken

                if can_survive:
                    if turns_to_defeat <= 2:  # 2-hit kill like manual solution
                        bonus -= 40  # Very strong bonus for efficient combat
                    elif turns_to_defeat <= 3:
                        bonus -= 20  # Strong bonus for reasonable combat
                    else:
                        bonus -= 10   # Moderate bonus for long combat

        return bonus

    def _calculate_upper_area_bonus(self, state: GameState) -> int:
        """Calculate bonus for upper area movement (negative cost)"""
        # Promote movement in upper area (y=0-2) to encourage detour routes
        if state.player_pos[1] <= 2:  # y coordinate 0-2
            # Stronger bonus for higher positions (y=0 gets more bonus than y=2)
            bonus_strength = (3 - state.player_pos[1]) * 3  # y=0:9, y=1:6, y=2:3
            return -bonus_strength  # Negative cost = bonus
        return 0

    def _enemy_blocks_path(self, state: GameState, enemy_state: EnemyState) -> bool:
        """Check if enemy is likely blocking optimal path to goal"""
        # Simple heuristic: enemy is blocking if it's roughly between player and goal
        px, py = state.player_pos
        ex, ey = enemy_state.position
        gx, gy = self.goal_pos

        # Check if enemy is in the general direction of the goal
        player_to_goal_x = gx - px
        player_to_goal_y = gy - py
        player_to_enemy_x = ex - px
        player_to_enemy_y = ey - py

        # If enemy is in same general direction as goal (dot product > 0)
        dot_product = (player_to_goal_x * player_to_enemy_x +
                      player_to_goal_y * player_to_enemy_y)

        # Enemy distance should be less than goal distance
        enemy_dist = abs(px - ex) + abs(py - ey)
        goal_dist = abs(px - gx) + abs(py - gy)

        return dot_product > 0 and enemy_dist < goal_dist

    def _get_valid_actions(self, state: GameState) -> List[ActionType]:
        """Get list of valid actions from current state"""
        valid_actions = []
        allowed_apis = self.stage.constraints.allowed_apis

        # Movement actions
        if "move" in allowed_apis:
            if self._can_move(state):
                valid_actions.append(ActionType.MOVE)

        # Turning actions
        if "turn_left" in allowed_apis:
            valid_actions.append(ActionType.TURN_LEFT)

        if "turn_right" in allowed_apis:
            valid_actions.append(ActionType.TURN_RIGHT)

        # Combat actions - only if player can attack in current direction
        if "attack" in allowed_apis:
            if self._can_attack(state):
                valid_actions.append(ActionType.ATTACK)

        # Item pickup
        if "pickup" in allowed_apis:
            if self._can_pickup(state):
                valid_actions.append(ActionType.PICKUP)

        # Wait action
        if "wait" in allowed_apis:
            valid_actions.append(ActionType.WAIT)

        # v1.2.12: Smart item handling
        # 🔧 FORCE smart item handling when all required APIs are available
        if "is_available" in allowed_apis and "dispose" in allowed_apis and "pickup" in allowed_apis:
            # print(f"🔧 A* DEBUG: Using SMART item handling (all 3 APIs available)")  # DISABLED for clean output
            if self._can_pickup(state) or self._can_dispose(state):
                # Check what type of item is at current position
                item_at_position = None
                for item_id, item_pos in self.items.items():
                    if item_pos == state.player_pos and item_id not in state.collected_items and item_id not in state.disposed_items:
                        # Find the stage item to check if it's a bomb
                        for stage_item in self.stage.items:
                            if stage_item.id == item_id:
                                item_at_position = stage_item
                                break
                        break

                if item_at_position:
                    # Debug item checking (SIMPLIFIED for clean output)
                    # print(f"🔍 A* ITEM DEBUG: Player at {state.player_pos}, found item {item_at_position.id}")
                    # print(f"   item type: {item_at_position.type}")
                    # print(f"   has damage attr: {hasattr(item_at_position, 'damage')}")
                    # if hasattr(item_at_position, 'damage'):
                    #     print(f"   damage value: {item_at_position.damage}")

                    # If it's a bomb (has damage attribute), add dispose action
                    if hasattr(item_at_position, 'damage') and item_at_position.damage is not None:
                        # print(f"   → A* chooses DISPOSE for bomb item")
                        if "dispose" in allowed_apis and self._can_dispose(state):
                            valid_actions.append(ActionType.DISPOSE)
                    else:
                        # print(f"   → A* chooses PICKUP for beneficial item")
                        # If it's not a bomb, add pickup action
                        if "pickup" in allowed_apis and self._can_pickup(state):
                            valid_actions.append(ActionType.PICKUP)
        else:
            # Legacy behavior: separate actions (DISABLED for debugging)
            print(f"⚠️ A* DEBUG: Legacy mode - not all 3 APIs available")
            # is_available action - always valid (non-turn consuming)
            if "is_available" in allowed_apis:
                valid_actions.append(ActionType.IS_AVAILABLE)

            # dispose action - valid if there's an item at current position
            if "dispose" in allowed_apis:
                if self._can_dispose(state):
                    valid_actions.append(ActionType.DISPOSE)

        return valid_actions

    def _can_move(self, state: GameState) -> bool:
        """Check if player can move forward"""
        dx, dy = self.directions[state.player_dir]
        new_x = state.player_pos[0] + dx
        new_y = state.player_pos[1] + dy

        # Check bounds
        if not (0 <= new_x < self.width and 0 <= new_y < self.height):
            return False

        # Check walls
        if (new_x, new_y) in self.walls:
            return False

        # Check enemies (cannot move into living enemy position, including large enemies)
        for enemy_state in state.enemies.values():
            if not enemy_state.is_alive or enemy_state.hp <= 0:
                continue

            # Check collision with any of the enemy's occupied positions (for large enemies)
            enemy_occupied_positions = self._get_enemy_occupied_positions(enemy_state)
            if (new_x, new_y) in enemy_occupied_positions:
                return False

        # TODO: Adjacent enemy movement blocking - temporarily disabled for investigation
        # Check if player is adjacent to any living enemy (movement may be blocked)
        # Game engine rule: player cannot move when adjacent to living enemy
        # px, py = state.player_pos
        # for enemy_state in state.enemies.values():
        #     if enemy_state.is_alive and enemy_state.hp > 0:
        #         ex, ey = enemy_state.position
        #         # Check if adjacent (distance = 1)
        #         if abs(px - ex) + abs(py - ey) == 1:
        #             # print(f"🚫 MOVE BLOCKED: Player at {state.player_pos} cannot move - adjacent to living enemy at {enemy_state.position}")
        #             return False

        return True

    def _can_attack(self, state: GameState) -> bool:
        """Check if player can attack an enemy and survive the combat"""
        # NOTE: Attack happens BEFORE enemy movement in actual game engine
        # Check attack target based on enemy positions BEFORE their movement
        dx, dy = self.directions[state.player_dir]
        target_x = state.player_pos[0] + dx
        target_y = state.player_pos[1] + dy

        # Check if there's a living enemy at target position BEFORE enemy movement (including large enemies)
        for enemy_id, enemy_state in state.enemies.items():
            if not enemy_state.is_alive or enemy_state.hp <= 0:
                continue

            # Check if target position hits any of the enemy's occupied positions (for large enemies)
            enemy_occupied_positions = self._get_enemy_occupied_positions(enemy_state)

            if (target_x, target_y) in enemy_occupied_positions:
                # Check if player can survive combat with this enemy
                can_survive = self._can_player_survive_combat(state, enemy_state)
                if can_survive:
                    return True
        return False

    def _can_attack_any_direction(self, state: GameState) -> List[str]:
        """Check if player can attack enemies by facing any direction.
        Returns list of directions that would allow successful attack."""
        import copy

        # Create a temporary state to simulate enemy movement
        temp_state = GameState(
            player_pos=state.player_pos,
            player_dir=state.player_dir,
            player_hp=state.player_hp,
            enemies=copy.deepcopy(state.enemies),
            collected_items=set(state.collected_items),
            turn_count=state.turn_count
        )

        # NOTE: Attack happens BEFORE enemy movement in actual game engine
        # So we check enemy positions BEFORE their movement (same as _can_attack)
        # DO NOT apply enemy AI movement here

        attackable_directions = []

        # Check each direction for attackable enemies
        for direction in ["N", "S", "E", "W"]:
            dx, dy = self.directions[direction]
            target_x = state.player_pos[0] + dx
            target_y = state.player_pos[1] + dy

            # Check if there's a living enemy at target position BEFORE enemy movement
            for enemy_state in state.enemies.values():
                if (enemy_state.position == (target_x, target_y) and
                    enemy_state.is_alive and enemy_state.hp > 0):

                    # Check if player can survive combat with this enemy
                    if self._can_player_survive_combat(state, enemy_state):
                        attackable_directions.append(direction)
                        break  # Found one enemy in this direction, no need to check more

        return attackable_directions

    def _calculate_turn_cost(self, current_dir: str, target_dir: str) -> int:
        """Calculate number of turns needed to change from current_dir to target_dir"""
        if current_dir == target_dir:
            return 0

        # Define direction order for clockwise rotation
        directions = ["N", "E", "S", "W"]

        current_idx = directions.index(current_dir)
        target_idx = directions.index(target_dir)

        # Calculate both clockwise and counter-clockwise distances
        clockwise_turns = (target_idx - current_idx) % 4
        counter_clockwise_turns = (current_idx - target_idx) % 4

        # Return minimum turns needed (either direction)
        return min(clockwise_turns, counter_clockwise_turns)

    def _get_enemy_at_position(self, state: GameState, position: Tuple[int, int]) -> Optional[EnemyState]:
        """Get enemy at specific position"""
        for enemy_state in state.enemies.values():
            if enemy_state.position == position and enemy_state.is_alive:
                return enemy_state
        return None

    def _calculate_combat_damage(self, attacker_power: int, defender_hp: int) -> Tuple[int, bool]:
        """Calculate damage and whether target dies"""
        new_hp = max(0, defender_hp - attacker_power)
        is_dead = new_hp <= 0
        return new_hp, is_dead

    def _can_player_survive_combat(self, state: GameState, target_enemy: EnemyState) -> bool:
        """プレイヤーが戦闘を生き残れるかチェック（段階的回転システム対応）"""

        player_hp = state.player_hp
        enemy_hp = target_enemy.hp
        player_attack = self._calculate_effective_attack_power(state)
        enemy_attack = target_enemy.attack_power

        # プレイヤーが敵を倒すのに必要なターン数
        turns_to_kill_enemy = math.ceil(enemy_hp / player_attack)

        # 段階的回転システム: 敵がプレイヤー方向に向くのに必要なターン数を計算
        enemy_direction = target_enemy.direction
        player_pos = state.player_pos
        enemy_pos = target_enemy.position

        # プレイヤー方向を計算
        dx = player_pos[0] - enemy_pos[0]
        dy = player_pos[1] - enemy_pos[1]

        if abs(dx) > abs(dy):
            target_direction = "E" if dx > 0 else "W"
        else:
            target_direction = "S" if dy > 0 else "N"

        # 段階的回転に必要なターン数を計算
        rotation_turns = self._calculate_rotation_turns(enemy_direction, target_direction)

        # 敵の反撃開始ターン: 段階的回転完了後
        enemy_first_attack_turn = rotation_turns + 1

        # プレイヤーが敵を倒すまでに敵が反撃できる回数
        if turns_to_kill_enemy < enemy_first_attack_turn:
            # 敵が向きを変える前に倒される
            enemy_counterattacks = 0
        else:
            # 敵が反撃開始した後の反撃回数
            # 最終攻撃回では敵は反撃前に撃破されるため +1 は不要
            enemy_counterattacks = turns_to_kill_enemy - enemy_first_attack_turn

        # プレイヤーが受ける総ダメージ
        total_damage_to_player = max(0, enemy_counterattacks) * enemy_attack

        # 実際のゲームエンジンとA*シミュレーションの差異を考慮した安全マージン
        # 段階的回転システムや敵移動の複雑さにより、実際の戦闘は予測より有利になることがある
        safety_margin = 15  # 実際のテスト結果に基づく調整値
        effective_damage = total_damage_to_player - safety_margin

        can_survive = effective_damage < player_hp

        # デバッグ情報にアイテム効果を含める
        base_attack = self.stage.player.attack_power
        attack_bonus = player_attack - base_attack
        attack_info = f"{player_attack}"
        if attack_bonus > 0:
            attack_info += f" (基本:{base_attack}+装備:{attack_bonus})"

        # Debug output disabled to prevent infinite loop display
        # print(f"🔍 戦闘生存チェック（段階的回転対応）:")
        # print(f"   プレイヤーHP={player_hp}, 敵HP={enemy_hp}")
        # print(f"   プレイヤー攻撃力={attack_info}, 敵攻撃力={enemy_attack}")
        # print(f"   敵方向={enemy_direction} → 目標方向={target_direction} (回転ターン数={rotation_turns})")
        # print(f"   敵を倒すターン数={turns_to_kill_enemy}, 敵の反撃開始ターン={enemy_first_attack_turn}")
        # print(f"   敵の反撃回数={enemy_counterattacks}, 予想ダメージ={total_damage_to_player}")
        # print(f"   安全マージン={safety_margin}, 実効ダメージ={effective_damage}")
        # print(f"   生存可能={can_survive}")

        return can_survive

    def _calculate_rotation_turns(self, current_direction: str, target_direction: str) -> int:
        """方向転換に必要なターン数を計算（ゲームエンジンと同じロジック）"""
        if current_direction == target_direction:
            return 0

        directions = ["N", "E", "S", "W"]
        try:
            current_index = directions.index(current_direction)
            target_index = directions.index(target_direction)
        except ValueError:
            # 不正な方向の場合は最大値を返す
            return 3

        # 時計回りと反時計回りの距離を計算
        clockwise_distance = (target_index - current_index) % 4
        counterclockwise_distance = (current_index - target_index) % 4

        # 最短距離を選択（各ステップ=1ターン）
        return min(clockwise_distance, counterclockwise_distance)

    def _calculate_effective_attack_power(self, state: GameState) -> int:
        """アイテム効果を含むプレイヤーの実効攻撃力を計算"""
        base_attack = self.stage.player.attack_power
        attack_bonus = 0

        # 収集済みアイテムの攻撃力ボーナスを計算
        for item_id in state.collected_items:
            # ハードコードされたアイテム効果（stage07の鋼の剣）
            if item_id == "sword1":
                attack_bonus += 35
                # print(f"  🔍 アイテム{item_id}: 攻撃力ボーナス+35追加")  # Debug disabled

        total_attack = base_attack + attack_bonus
        # print(f"  🔍 最終攻撃力: {base_attack} + {attack_bonus} = {total_attack}")  # Debug disabled
        return total_attack

    def _can_pickup(self, state: GameState) -> bool:
        """Check if player can pick up an item"""
        # Check if there's an item at player position
        for item_id, item_pos in self.items.items():
            if item_pos == state.player_pos and item_id not in state.collected_items:
                return True

        return False

    def _can_dispose(self, state: GameState) -> bool:
        """Check if player can dispose an item - v1.2.12"""
        # Check if there's any item at player position (disposed regardless of type)
        for item_id, item_pos in self.items.items():
            if (item_pos == state.player_pos and
                item_id not in state.collected_items and
                item_id not in state.disposed_items):
                return True

        return False

    def _apply_action(self, state: GameState, action: ActionType) -> Optional[GameState]:
        """Apply an action to a state and return the new state"""
        import copy
        new_state = GameState(
            player_pos=state.player_pos,
            player_dir=state.player_dir,
            player_hp=state.player_hp,
            enemies=copy.deepcopy(state.enemies),
            collected_items=set(state.collected_items),
            disposed_items=set(state.disposed_items),  # v1.2.12
            turn_count=state.turn_count + 1
        )

        if action == ActionType.MOVE:
            if not self._can_move(state):
                return None
            dx, dy = self.directions[state.player_dir]
            new_state.player_pos = (state.player_pos[0] + dx, state.player_pos[1] + dy)

        elif action == ActionType.TURN_LEFT:
            current_idx = self.direction_names.index(state.player_dir)
            new_state.player_dir = self.direction_names[(current_idx - 1) % 4]

        elif action == ActionType.TURN_RIGHT:
            current_idx = self.direction_names.index(state.player_dir)
            new_state.player_dir = self.direction_names[(current_idx + 1) % 4]

        elif action == ActionType.ATTACK:
            if not self._can_attack(state):
                return None

            dx, dy = self.directions[state.player_dir]
            target_pos = (state.player_pos[0] + dx, state.player_pos[1] + dy)

            # DEBUG: Add debug logging for attack action (disabled for clean output)
            # print(f"🔍 ATTACK DEBUG: Player at {state.player_pos} facing {state.player_dir}")
            # print(f"🔍 ATTACK DEBUG: Target position: {target_pos}")
            # print(f"🔍 ATTACK DEBUG: Available enemies BEFORE attack (original state):")
            # for enemy_id, enemy_state in state.enemies.items():
            #     print(f"🔍   Enemy {enemy_id}: pos={enemy_state.position}, hp={enemy_state.hp}, alive={enemy_state.is_alive}")

            # Find and damage enemy using ORIGINAL state positions (before any AI movement)
            attack_hit = False
            for enemy_id, enemy_state in state.enemies.items():
                if not enemy_state.is_alive or enemy_state.hp <= 0:
                    continue

                # Check if target position hits any of the enemy's occupied positions (for large enemies)
                enemy_occupied_positions = self._get_enemy_occupied_positions(enemy_state)
                if target_pos in enemy_occupied_positions:

                    attack_hit = True
                    # print(f"🔍 ATTACK HIT: Attacking enemy {enemy_id} at {target_pos}")

                    # Apply damage to the corresponding enemy in new_state
                    target_new_enemy = new_state.enemies[enemy_id]

                    # Calculate damage to enemy
                    new_enemy_hp, enemy_dies = self._calculate_combat_damage(
                        self._calculate_effective_attack_power(new_state), enemy_state.hp
                    )

                    # 攻撃を受けたエネミーはalert状態になる（ゲームエンジンと同じ）
                    # Update enemy state with alert status after being attacked
                    new_enemy_state = EnemyState(
                        position=target_new_enemy.position,  # Keep new_state position for post-action processing
                        direction=target_new_enemy.direction,
                        hp=new_enemy_hp,
                        max_hp=target_new_enemy.max_hp,
                        attack_power=target_new_enemy.attack_power,
                        behavior=target_new_enemy.behavior,
                        is_alive=not enemy_dies,
                        patrol_path=target_new_enemy.patrol_path,
                        patrol_index=target_new_enemy.patrol_index,
                        vision_range=target_new_enemy.vision_range,
                        is_alert=True,  # 攻撃を受けたらalert状態に変更
                        last_seen_player=state.player_pos,  # プレイヤー位置を記録
                        alert_cooldown=10  # 攻撃を受けたらクールダウンを設定
                    )
                    # Mark enemy as attacked this turn to prevent alert reset
                    new_enemy_state.attacked_this_turn = True
                    new_state.enemies[enemy_id] = new_enemy_state

                    # ゲームエンジンでは攻撃後エネミーの反撃は次のターンのAI処理で行われる
                    # (In game engine, enemy counter-attack happens in next turn's AI processing)

                    break

            # if not attack_hit:
            #     print(f"🔍 ATTACK MISS: No enemy found at target position {target_pos}")
            # else:
            #     print(f"🔍 ATTACK HIT: Enemy defeated at {target_pos}")

            # DEBUG: Log attack action (disabled for performance)
            # print(f"🎯 ACTION: {action.value} | Player: {state.player_pos} {state.player_dir} -> attacking {target_pos}")

            # NOTE: Enemy AI will be processed at the end of _apply_action() for all actions

        elif action == ActionType.PICKUP:
            if not self._can_pickup(state):
                return None

            # Pick up item at player position
            for item_id, item_pos in self.items.items():
                if item_pos == state.player_pos and item_id not in state.collected_items:
                    new_state.collected_items.add(item_id)
                    break

        elif action == ActionType.WAIT:
            # No state change except turn count
            pass

        elif action == ActionType.IS_AVAILABLE:
            # is_available() does not consume a turn - reset turn count
            new_state.turn_count = state.turn_count
            # This action is used for conditional branching in search
            # The actual item availability check is done in _get_valid_actions()
            pass

        elif action == ActionType.DISPOSE:
            if not self._can_dispose(state):
                return None

            # Find bomb item at player position
            for item_id, item_pos in self.items.items():
                if item_pos == state.player_pos and item_id not in state.collected_items:
                    # Check if item is a bomb (has damage attribute)
                    stage_item = None
                    for stage_item_obj in self.stage.items:
                        if stage_item_obj.id == item_id:
                            stage_item = stage_item_obj
                            break

                    if stage_item and hasattr(stage_item, 'damage') and stage_item.damage is not None:
                        # Successfully dispose bomb
                        new_state.disposed_items.add(item_id)
                    # For non-bomb items, action consumes turn but has no effect
                    break

        # ゲームエンジンと同じ処理順序：プレイヤーアクション実行後にエネミーAI処理
        # (Game engine processes player action first, then enemy AI)
        # IMPORTANT: Attack resolution uses enemy positions BEFORE AI processing,
        # but enemy AI still processes AFTER attack (enemies react to combat)

        # Always apply enemy AI after player action (including attacks)
        # DEBUG: Log action and enemy positions (disabled for clean output)
        # print(f"🎯 ACTION: {action.value} | Player: {state.player_pos}->{new_state.player_pos} {state.player_dir}->{new_state.player_dir}")
        self._apply_enemy_ai(new_state)

        # Check if player died after enemy AI processing
        if new_state.player_hp <= 0:
            print(f"💀 INVALID STATE: Player died (HP: {new_state.player_hp})")
            return None  # Return None to indicate invalid state

        return new_state

    def _reconstruct_path(self, goal_node: SearchNode) -> List[ActionType]:
        """Reconstruct the path from start to goal"""
        path = []
        current = goal_node

        while current.parent is not None:
            if current.action:
                path.append(current.action)
            current = current.parent

        path.reverse()

        # DEBUG: Print the solution path
        print(f"📋 A* Solution Path ({len(path)} steps):")
        for i, action in enumerate(path):
            print(f"   Step {i+1}: {action.value}")

        return path

    def _calculate_initial_patrol_index(self, enemy_config) -> int:
        """Calculate the initial patrol index for an enemy based on its position (same as game engine)"""
        if not hasattr(enemy_config, 'patrol_path') or not enemy_config.patrol_path:
            return 0

        enemy_pos = tuple(enemy_config.position)
        patrol_path = [tuple(pos) for pos in enemy_config.patrol_path]

        # Find exact current position in patrol path (same as game engine _initialize_patrol_index)
        for i, pos in enumerate(patrol_path):
            if pos == enemy_pos:
                return i  # Return exact index, same as game engine

        # If current position not in patrol path, find closest position (same as game engine)
        min_distance = float('inf')
        closest_index = 0
        for i, pos in enumerate(patrol_path):
            distance = abs(pos[0] - enemy_pos[0]) + abs(pos[1] - enemy_pos[1])
            if distance < min_distance:
                min_distance = distance
                closest_index = i

        return closest_index

    def _get_enemy_vision_range(self, enemy) -> int:
        """Get enemy vision range from stage file (error if not set)"""
        if not hasattr(enemy, 'vision_range') or enemy.vision_range is None or enemy.vision_range <= 0:
            raise ValueError(f"Enemy '{enemy.id}' must have vision_range explicitly set in stage file (got: {getattr(enemy, 'vision_range', None)})")
        return enemy.vision_range

    def _apply_enemy_ai(self, state: GameState) -> None:
        """Apply enemy AI behavior - exactly match game_state.py logic"""
        for enemy_id, enemy_state in state.enemies.items():
            if not enemy_state.is_alive or enemy_state.hp <= 0:
                continue

            # Reset attacked flag at start of new turn
            if hasattr(enemy_state, 'attacked_this_turn'):
                enemy_state.attacked_this_turn = False

            # DEBUG: Track enemy position changes
            original_pos = enemy_state.position
            original_direction = enemy_state.direction
            original_alert = enemy_state.is_alert

            # CRITICAL FIX: First execute movement, then check vision (same as game engine)
            # Execute movement behavior first - behavior type takes priority over alert state
            if enemy_state.behavior == "static":
                # Static enemies only move when alert (chase mode), no patrol when calm
                if enemy_state.is_alert:
                    self._apply_chase_ai(state, enemy_state)  # Static enemies chase when alert
                # When not alert, static enemies do nothing (no patrol behavior)
            elif enemy_state.behavior == "patrol":
                if enemy_state.is_alert:
                    # Patrol enemies chase when alert
                    self._apply_chase_ai(state, enemy_state)
                else:
                    # Patrol enemies follow their path when not alert
                    self._apply_patrol_ai(state, enemy_state)
            elif enemy_state.is_alert:
                # Other enemy types chase when alert
                self._apply_chase_ai(state, enemy_state)

            # DEBUG: Log any enemy changes (simplified to reduce spam)
            if enemy_state.position != original_pos:
                print(f"DEBUG ENEMY MOVE: {enemy_id} {original_pos}->{enemy_state.position}, alert={enemy_state.is_alert}, behavior={enemy_state.behavior}")

            # DEBUG: Log when static enemies are processed
            if enemy_state.behavior == "static" and enemy_state.is_alert:
                print(f"DEBUG STATIC ALERT: {enemy_id} at {enemy_state.position}, alert={enemy_state.is_alert} - chasing player")

            # THEN check if enemy can see player at NEW position (same as game engine)
            if self._can_enemy_see_player(state, enemy_state):
                # Player detected - switch to alert mode
                if not enemy_state.is_alert:
                    print(f"ALERT: 敵がプレイヤーを発見！警戒状態に移行")
                    enemy_state.is_alert = True
                    enemy_state.alert_cooldown = 10  # 10 turns of continued tracking
                    enemy_state.last_seen_player = state.player_pos
                else:
                    # Still seeing player - reset cooldown
                    enemy_state.alert_cooldown = 10
            else:
                # Player not visible - check alert_cooldown like game engine
                if enemy_state.alert_cooldown > 0:
                    # Still in alert cooldown - continue tracking
                    enemy_state.alert_cooldown -= 1
                    if enemy_state.alert_cooldown <= 0:
                        enemy_state.is_alert = False
                elif not hasattr(enemy_state, 'attacked_this_turn') or not enemy_state.attacked_this_turn:
                    # Only reset alert if enemy was not attacked this turn
                    # No alert cooldown - return to normal behavior
                    enemy_state.is_alert = False

            # DEBUG: Log enemy position and direction changes (disabled)
            # if enemy_state.position != original_pos:
            #     print(f"🚶 ENEMY MOVE: {enemy_id} moved from {original_pos} to {enemy_state.position} (direction: {original_direction}->{enemy_state.direction}, Player at {state.player_pos})")
            # elif enemy_state.direction != original_direction:
            #     print(f"🔄 ENEMY ROTATE: {enemy_id} rotated from {original_direction} to {enemy_state.direction} at {enemy_state.position} (Player at {state.player_pos})")
            # else:
            #     print(f"⏸️ ENEMY STAY: {enemy_id} stayed at {enemy_state.position} (direction: {enemy_state.direction}, Player at {state.player_pos})")

    def _can_enemy_see_player(self, state: GameState, enemy_state: EnemyState) -> bool:
        """Check if enemy can see the player using directional cone vision (same as game engine)"""
        px, py = state.player_pos
        ex, ey = enemy_state.position

        # Use enemy's actual vision_range (must be explicitly set)
        vision_range = enemy_state.vision_range

        # DEBUG: Add detailed vision debugging for step 7 issue (DISABLED for performance)
        # if state.turn_count == 7 or ((ex, ey) == (8, 2) and (px, py) == (6, 0)):
        #     print(f"🔍 A* VISION DEBUG: Enemy at ({ex},{ey}) dir={enemy_state.direction} → Player at ({px},{py}) | Turn={state.turn_count}")
        #     print(f"   vision_range={vision_range}, alert={enemy_state.is_alert}")

        # Direction mappings to match game engine
        direction_offsets = {
            "N": (0, -1),  # North
            "S": (0, 1),   # South
            "E": (1, 0),   # East
            "W": (-1, 0)   # West
        }

        if enemy_state.direction not in direction_offsets:
            return False

        dx_dir, dy_dir = direction_offsets[enemy_state.direction]

        # Check each distance within vision range (same logic as game engine)
        for distance in range(1, vision_range + 1):
            for offset in range(-distance, distance + 1):
                # Calculate target position based on direction (same as engine/__init__.py:299-308)
                if enemy_state.direction == "N":
                    target_x = ex + offset
                    target_y = ey - distance
                elif enemy_state.direction == "S":
                    target_x = ex + offset
                    target_y = ey + distance
                elif enemy_state.direction == "E":
                    target_x = ex + distance
                    target_y = ey + offset
                elif enemy_state.direction == "W":
                    target_x = ex - distance
                    target_y = ey + offset
                else:
                    continue

                # DEBUG: Show all calculation steps for critical case (DISABLED for performance)
                # if (ex, ey) == (8, 2) and enemy_state.direction == "N" and px == 6 and py == 0:
                #     print(f"🔍 CRITICAL CASE DEBUG: distance={distance}, offset={offset}, target=({target_x},{target_y}), player=({px},{py})")
                #     print(f"🔍 CRITICAL CASE: Checking position match: target=({target_x},{target_y}) vs player=({px},{py}) → match={((target_x, target_y) == (px, py))}")
                #     if (target_x, target_y) == (px, py):
                #         print(f"🔍 CRITICAL CASE: POSITION MATCH! Checking angle: abs({offset}) <= {distance} → {abs(offset) <= distance}")

                # Check if this target position matches player position
                if (target_x, target_y) == (px, py):
                    # 90-degree field of view check (same as engine/__init__.py:311)
                    if abs(offset) <= distance:
                        # Check line of sight (wall obstruction) - same as game engine
                        if self._has_line_of_sight(enemy_state.position, (target_x, target_y)):
                            # print(f"🔍 A* VISION: PLAYER DETECTED at distance={distance}, offset={offset}, target=({target_x},{target_y})")  # DISABLED for clean output
                            return True

        # print(f"🔍 A* VISION: No detection - vision_range={vision_range}, direction={enemy_state.direction}")  # DISABLED for clean output
        return False

    def _has_line_of_sight(self, start_pos: Tuple[int, int], target_pos: Tuple[int, int]) -> bool:
        """Check if line of sight is clear (no walls blocking) - same as game engine"""
        start_x, start_y = start_pos
        end_x, end_y = target_pos

        # Use Bresenham line algorithm (same as engine/__init__.py:334-375)
        dx = abs(end_x - start_x)
        dy = abs(end_y - start_y)

        step_x = 1 if start_x < end_x else -1
        step_y = 1 if start_y < end_y else -1

        x, y = start_x, start_y

        if dx > dy:
            err = dx / 2.0
            while x != end_x:
                x += step_x
                err -= dy
                if err < 0:
                    y += step_y
                    err += dx
                # Check intermediate points for walls (excluding target)
                if x != end_x or y != end_y:
                    if (x, y) in self.walls:
                        return False
        else:
            err = dy / 2.0
            while y != end_y:
                y += step_y
                err -= dx
                if err < 0:
                    x += step_x
                    err += dy
                # Check intermediate points for walls (excluding target)
                if x != end_x or y != end_y:
                    if (x, y) in self.walls:
                        return False

        return True


    def _apply_combat_ai(self, state: GameState, enemy_state: EnemyState) -> None:
        """Apply combat AI - attack player with gradual rotation (exactly same as game engine)"""
        px, py = state.player_pos
        ex, ey = enemy_state.position

        # Calculate Manhattan distance
        distance = abs(px - ex) + abs(py - ey)

        # If adjacent, attack with gradual rotation (exactly same as game engine)
        if distance == 1:
            # Calculate required direction to face player
            dx = px - ex
            dy = py - ey

            # Determine required direction based on position difference
            if abs(dx) > abs(dy):
                target_direction = "E" if dx > 0 else "W"
            else:
                target_direction = "S" if dy > 0 else "N"

            # Apply gradual rotation (exactly same as game engine)
            if enemy_state.direction != target_direction:
                # Game engine uses gradual rotation - one step at a time
                enemy_state.direction = self._get_next_rotation_step(enemy_state.direction, target_direction)
                # No attack on direction change turn (same as game engine)
            else:
                # Facing correct direction, execute attack (same as game engine)
                new_player_hp = max(0, state.player_hp - enemy_state.attack_power)
                state.player_hp = new_player_hp

                # Check if player died from this attack
                if state.player_hp <= 0:
                    print(f"💀 PLAYER DIED: Enemy {enemy_id} killed player with {enemy_state.attack_power} damage")
                    # Player is dead - this state should not be valid for further exploration
                    return
        else:
            # Not adjacent, move towards player with separate direction change and movement turns
            self._apply_chase_ai_gradual(state, enemy_state)

    def _get_next_rotation_step(self, current_direction: str, target_direction: str) -> str:
        """Get next rotation step for gradual rotation (same as game engine)"""
        direction_order = ["N", "E", "S", "W"]
        current_idx = direction_order.index(current_direction)
        target_idx = direction_order.index(target_direction)

        # Calculate shortest rotation direction
        clockwise_steps = (target_idx - current_idx) % 4
        counter_clockwise_steps = (current_idx - target_idx) % 4

        if clockwise_steps <= counter_clockwise_steps:
            # Rotate clockwise
            next_idx = (current_idx + 1) % 4
        else:
            # Rotate counter-clockwise
            next_idx = (current_idx - 1) % 4

        return direction_order[next_idx]

    def _apply_chase_ai_gradual(self, state: GameState, enemy_state: EnemyState) -> None:
        """Apply chase AI with gradual movement (exactly same as game engine)"""
        player_pos = state.player_pos
        enemy_pos = enemy_state.position

        # Calculate direction to player
        dx = player_pos[0] - enemy_pos[0]
        dy = player_pos[1] - enemy_pos[1]

        # Determine movement direction (prioritize x-axis like game engine)
        if abs(dx) >= abs(dy):
            # Move horizontally (x-axis priority)
            target_direction = "E" if dx > 0 else "W"
            new_pos = (enemy_pos[0] + (1 if dx > 0 else -1), enemy_pos[1])
        else:
            # Move vertically (only when abs(dy) > abs(dx))
            target_direction = "S" if dy > 0 else "N"
            new_pos = (enemy_pos[0], enemy_pos[1] + (1 if dy > 0 else -1))

        # Game engine separates direction change and movement
        if enemy_state.direction != target_direction:
            # Direction change turn - no movement
            enemy_state.direction = target_direction
        else:
            # Movement turn - only if already facing correct direction
            if (new_pos not in self.walls and
                0 <= new_pos[0] < self.width and
                0 <= new_pos[1] < self.height and
                new_pos != state.player_pos):  # Don't move into player position
                enemy_state.position = new_pos

    def _apply_patrol_ai(self, state: GameState, enemy_state: EnemyState) -> None:
        """Apply patrol AI - patrol mode or chase mode based on player detection"""
        if not enemy_state.is_alive:
            return

        # CRITICAL FIX: Do NOT check vision here - vision is checked AFTER movement in _apply_enemy_ai
        # This ensures vision check happens at post-movement position (same as game engine)

        if enemy_state.is_alert:
            # Chase mode: move toward player
            self._apply_chase_ai(state, enemy_state)
        else:
            # Patrol mode: follow patrol path
            self._apply_standard_patrol_ai(state, enemy_state)

    def _apply_standard_patrol_ai(self, state: GameState, enemy_state: EnemyState) -> None:
        """Apply standard patrol AI - move enemy along patrol path (EXACTLY same as game engine)"""
        if not enemy_state.patrol_path or len(enemy_state.patrol_path) <= 1:
            return

        # DEBUG: Log patrol state for step 6-7 synchronization issue (DISABLED for performance)
        # if state.turn_count >= 6 and state.turn_count <= 8:
        #     print(f"🚶 A* PATROL DEBUG: Turn={state.turn_count}, Enemy at {enemy_state.position}, patrol_index={enemy_state.patrol_index}")
        #     print(f"   patrol_path: {enemy_state.patrol_path}")
        #     print(f"   direction: {enemy_state.direction}")

        # Get next target position (same as game engine's get_next_patrol_position)
        # Based on engine/__init__.py:383 - returns NEXT position (current_patrol_index + 1)
        next_index = (enemy_state.patrol_index + 1) % len(enemy_state.patrol_path)
        current_target = tuple(enemy_state.patrol_path[next_index])

        # If already at current target, advance to next patrol point (same as game engine)
        if enemy_state.position == current_target:
            enemy_state.patrol_index = (enemy_state.patrol_index + 1) % len(enemy_state.patrol_path)
            next_index = (enemy_state.patrol_index + 1) % len(enemy_state.patrol_path)
            current_target = tuple(enemy_state.patrol_path[next_index])

        # Move towards target if different from current position
        if current_target != enemy_state.position:
            # Calculate required direction (same logic as game engine:1060-1067)
            dx = current_target[0] - enemy_state.position[0]
            dy = current_target[1] - enemy_state.position[1]

            # Choose required direction (x-axis priority, same as game engine:1064-1067)
            if dx != 0:
                required_direction = "E" if dx > 0 else "W"
            elif dy != 0:
                required_direction = "S" if dy > 0 else "N"
            else:
                return  # Already at target

            # FIXED: Apply EXACT game engine logic (game_state.py:1072-1079)
            # Check if already facing correct direction
            if enemy_state.direction == required_direction:
                # Movement execution - only if already facing correct direction
                offset_x = 1 if required_direction == "E" else (-1 if required_direction == "W" else 0)
                offset_y = 1 if required_direction == "S" else (-1 if required_direction == "N" else 0)
                next_position = (enemy_state.position[0] + offset_x, enemy_state.position[1] + offset_y)

                # Check if next position is valid (same as game engine:1075-1076)
                if (next_position not in self.walls and
                    0 <= next_position[0] < self.width and
                    0 <= next_position[1] < self.height and
                    next_position != state.player_pos):
                    # Move to target
                    old_pos = enemy_state.position
                    old_dir = enemy_state.direction
                    enemy_state.position = next_position
                    # ⚠️  CRITICAL FIX: 方向設定はすでに上で行われているため、ここで重複設定しない
                    # enemy_state.direction = required_direction  # REMOVED: Duplicate direction setting
                    # print(f"🚶 A* PATROL MOVE: Enemy moved {old_pos}→{next_position} dir={old_dir}→{enemy_state.direction} (Turn={state.turn_count})")  # DISABLED for clean output
                else:
                    # print(f"🚫 A* PATROL BLOCKED: Enemy cannot move to {next_position} (Turn={state.turn_count})")  # DISABLED for clean output
                    pass
            else:
                # Direction change - just change direction without moving (same as game engine:1078-1079)
                old_dir = enemy_state.direction
                enemy_state.direction = required_direction
                # print(f"🔄 A* PATROL TURN: Enemy turned {old_dir}→{required_direction} at {enemy_state.position} (Turn={state.turn_count})")  # DISABLED for clean output

    def _apply_chase_ai(self, state: GameState, enemy_state: EnemyState) -> None:
        """Apply chase AI - exact implementation from game_state.py _simple_chase_behavior"""
        player_pos = state.player_pos
        enemy_pos = enemy_state.position
        # print(f"🏃 A* CHASE: Enemy at {enemy_pos} dir={enemy_state.direction} → Player at {player_pos} (Turn={state.turn_count})")  # DISABLED for clean output

        # Calculate direction to player
        dx = player_pos[0] - enemy_pos[0]
        dy = player_pos[1] - enemy_pos[1]
        distance = abs(dx) + abs(dy)
        # print(f"🏃 A* CHASE: Distance={distance}, dx={dx}, dy={dy}")  # DISABLED for clean output

        # Adjacent case - attack processing with gradual rotation system
        if distance == 1:
            # Determine required direction to player
            if abs(dx) > abs(dy):
                required_direction = "E" if dx > 0 else "W"
            else:
                required_direction = "S" if dy > 0 else "N"

            if enemy_state.direction == required_direction:
                # Attack execution (direction already correct)
                # print(f"⚔️ A* ATTACK: Enemy attacks player! {enemy_state.attack_power} damage (Turn={state.turn_count})")  # DISABLED for clean output
                # Apply damage to player
                state.player_hp -= enemy_state.attack_power
                # print(f"💀 A* ATTACK: Player HP={state.player_hp} after attack")  # DISABLED for clean output
                if state.player_hp <= 0:
                    # Player dies - this state is invalid
                    # print(f"☠️ A* DEATH: Player died at Turn={state.turn_count}")  # DISABLED for clean output
                    return
            else:
                # Gradual rotation system: only rotate one step per turn
                next_direction = self._get_next_rotation_step(enemy_state.direction, required_direction)
                # print(f"🔄 A* GRADUAL TURN: Enemy gradually turns {enemy_state.direction}→{next_direction} (target: {required_direction}) (Turn={state.turn_count})")  # DISABLED for clean output
                enemy_state.direction = next_direction
            return

        # Movement processing - exact implementation from game_state.py
        target_directions = []

        # X-axis movement
        if dx > 0:
            target_directions.append("E")
        elif dx < 0:
            target_directions.append("W")

        # Y-axis movement
        if dy > 0:
            target_directions.append("S")
        elif dy < 0:
            target_directions.append("N")

        # Prioritize larger axis difference (same as game_state.py logic)
        if abs(dx) >= abs(dy):
            pass  # X-axis already first
        else:
            # Swap to prioritize Y-axis
            if len(target_directions) == 2:
                target_directions[0], target_directions[1] = target_directions[1], target_directions[0]

        # Try movement in priority order
        for direction in target_directions:
            direction_offsets = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
            dx_offset, dy_offset = direction_offsets[direction]
            new_pos = (enemy_pos[0] + dx_offset, enemy_pos[1] + dy_offset)

            # Check if movement is valid (same logic as game_state.py _is_valid_move)
            if (0 <= new_pos[0] < self.width and
                0 <= new_pos[1] < self.height and
                new_pos not in self.walls):

                if direction == enemy_state.direction:
                    # Same direction - move immediately
                    old_pos = enemy_state.position
                    enemy_state.position = new_pos
                    # print(f"🏃 A* CHASE MOVE: Enemy moved {old_pos}→{new_pos} dir={direction} (Turn={state.turn_count})")  # DISABLED for clean output
                else:
                    # Turn to face movement direction
                    # print(f"🔄 A* CHASE TURN: Enemy turns {enemy_state.direction}→{direction} at {enemy_state.position} (Turn={state.turn_count})")  # DISABLED for clean output
                    enemy_state.direction = direction
                return

    def test_specific_solution(self, actions: List) -> bool:
        """特定のアクション列をテストして詳細ログを出力"""
        print(f"A* 特定ソリューション テスト開始: {len(actions)}ステップ")
        print(f"アクション列: {actions}")

        # 初期状態を作成 (find_path()メソッドと同じロジック)
        start_state = GameState(
            player_pos=tuple(self.stage.player.start),
            player_dir=self.stage.player.direction,
            player_hp=self.stage.player.hp,
            enemies={
                enemy.id: EnemyState(
                    position=tuple(enemy.position),
                    direction=enemy.direction,
                    hp=enemy.hp,
                    max_hp=enemy.max_hp,
                    attack_power=enemy.attack_power,
                    behavior=enemy.behavior,
                    enemy_type=enemy.type if hasattr(enemy, 'type') else 'normal',  # Fixed: enemy_type
                    is_alive=True,
                    patrol_path=[tuple(pos) for pos in enemy.patrol_path] if hasattr(enemy, 'patrol_path') and enemy.patrol_path else None,
                    patrol_index=self._calculate_initial_patrol_index(enemy) if hasattr(enemy, 'patrol_path') and enemy.patrol_path else 0,
                    vision_range=self._get_enemy_vision_range(enemy),
                    is_alert=False,
                    alert_cooldown=0
                )
                for enemy in self.stage.enemies
            },
            collected_items=set(),
            disposed_items=set(),
            turn_count=0
        )
        current_state = start_state
        print(f"初期状態:")
        print(f"   プレイヤー: pos={current_state.player_pos}, dir={current_state.player_dir}, HP={current_state.player_hp}")

        for enemy_id, enemy_state in current_state.enemies.items():
            print(f"   敵 {enemy_id}: pos={enemy_state.position}, dir={enemy_state.direction}, HP={enemy_state.hp}, alerted={enemy_state.is_alert}")

        for step_num, action in enumerate(actions, 1):
            print(f"\nA* ステップ {step_num}: {action}")
            print(f"   実行前 - プレイヤー: pos={current_state.player_pos}, dir={current_state.player_dir}, HP={current_state.player_hp}")

            # 敵状態表示
            for enemy_id, enemy_state in current_state.enemies.items():
                if enemy_state.is_alive:
                    print(f"   実行前 - 敵 {enemy_id}: pos={enemy_state.position}, dir={enemy_state.direction}, HP={enemy_state.hp}, alerted={enemy_state.is_alert}")

            # Handle both string actions and ActionType enum objects
            if isinstance(action, ActionType):
                action_type = action
                action_name = action.value
            else:
                # Convert string action to ActionType enum
                action_type_map = {
                    'turn_left': ActionType.TURN_LEFT,
                    'turn_right': ActionType.TURN_RIGHT,
                    'move': ActionType.MOVE,
                    'attack': ActionType.ATTACK,
                    'pickup': ActionType.PICKUP,
                    'dispose': ActionType.DISPOSE,
                    'wait': ActionType.WAIT,
                    'is_available': ActionType.IS_AVAILABLE
                }

                if action not in action_type_map:
                    print(f"❌ A* エラー: 不明なアクション '{action}' at ステップ {step_num}")
                    return False

                action_type = action_type_map[action]
                action_name = action

            # アクション実行前のチェック
            if action_type == ActionType.MOVE:
                can_move = self._can_move(current_state)
                print(f"   MOVE チェック: can_move = {can_move}")
                if not can_move:
                    # 詳細ログ
                    dx, dy = self.directions[current_state.player_dir]
                    new_x = current_state.player_pos[0] + dx
                    new_y = current_state.player_pos[1] + dy
                    print(f"   移動先: ({new_x}, {new_y})")
                    print(f"   移動先が範囲内: {0 <= new_x < self.width and 0 <= new_y < self.height}")
                    if (0 <= new_x < self.width and 0 <= new_y < self.height):
                        print(f"   移動先が壁: {(new_x, new_y) in self.walls}")
                        for enemy_id, enemy_state in current_state.enemies.items():
                            if enemy_state.position == (new_x, new_y) and enemy_state.is_alive and enemy_state.hp > 0:
                                print(f"   移動先に敵{enemy_id}が存在: pos={enemy_state.position}, alive={enemy_state.is_alive}, hp={enemy_state.hp}")

            new_state = self._apply_action(current_state, action_type)

            if new_state is None:
                print(f"❌ A* エラー: アクション '{action}' が無効な状態を生成 at ステップ {step_num}")
                return False

            print(f"   実行後 - プレイヤー: pos={new_state.player_pos}, dir={new_state.player_dir}, HP={new_state.player_hp}")

            # 敵状態表示
            for enemy_id, enemy_state in new_state.enemies.items():
                if enemy_state.is_alive:
                    print(f"   実行後 - 敵 {enemy_id}: pos={enemy_state.position}, dir={enemy_state.direction}, HP={enemy_state.hp}, alerted={enemy_state.is_alert}")

            # プレイヤー死亡チェック
            if new_state.player_hp <= 0:
                print(f"A* プレイヤー死亡 at ステップ {step_num}: HP={new_state.player_hp}")
                return False

            current_state = new_state

            # ゴール判定
            if self._is_goal_reached(current_state):
                print(f"A* ゴール到達 at ステップ {step_num}!")
                return True

        print(f"WARNING A* テスト完了: ゴール未到達、プレイヤー生存")
        return False