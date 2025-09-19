"""A* pathfinding algorithm for stage validation"""
from typing import List, Tuple, Set, Optional, Dict, Any
import heapq
import math
from dataclasses import dataclass
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


@dataclass
class EnemyState:
    """Represents an enemy's current state"""
    position: Tuple[int, int]
    direction: str
    hp: int
    max_hp: int
    attack_power: int
    behavior: str
    is_alive: bool = True
    patrol_path: Optional[List[Tuple[int, int]]] = None
    patrol_index: int = 0
    target_direction: Optional[str] = None
    vision_range: int = 3
    is_alert: bool = False  # True when player detected (chase mode)
    last_seen_player: Optional[Tuple[int, int]] = None  # Last known player position

    def __hash__(self):
        return hash((self.position, self.direction, self.hp, self.is_alive, self.patrol_index, self.target_direction, self.vision_range, self.is_alert, self.last_seen_player))


@dataclass
class GameState:
    """Represents a complete game state"""
    player_pos: Tuple[int, int]
    player_dir: str
    player_hp: int
    enemies: Dict[str, EnemyState]  # id -> EnemyState
    collected_items: Set[str]
    turn_count: int

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

    def _extract_walls(self) -> Set[Tuple[int, int]]:
        """Extract wall positions from board grid"""
        walls = set()
        for y, row in enumerate(self.stage.board.grid):
            for x, cell in enumerate(row):
                if cell == '#':
                    walls.add((x, y))
        return walls

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
                    is_alive=True,
                    patrol_path=[tuple(pos) for pos in enemy.patrol_path] if hasattr(enemy, 'patrol_path') and enemy.patrol_path else None,
                    patrol_index=self._calculate_initial_patrol_index(enemy) if hasattr(enemy, 'patrol_path') and enemy.patrol_path else 0,
                    vision_range=getattr(enemy, 'vision_range', 3),
            is_alert=False,
            last_seen_player=None
                )
                for enemy in self.stage.enemies
            },
            collected_items=set(),
            turn_count=0
        )

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

            # Check if goal reached
            if self._is_goal_reached(current_node.state):
                print(f"探索完了: 解法発見! 総ノード数: {nodes_explored:,}")
                return self._reconstruct_path(current_node)

            # Check turn limit - allow some flexibility for complex scenarios
            if current_node.state.turn_count >= max_turns * 1.2:  # Allow 20% more turns for exploration
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
            if not required_items.issubset(state.collected_items):
                return False
            return True

        # Check all victory conditions (ALL must be satisfied)
        for condition in victory_conditions:
            condition_type = condition.get('type', '')

            if condition_type == 'reach_goal':
                if state.player_pos != self.goal_pos:
                    return False
            elif condition_type == 'defeat_all_enemies':
                if any(enemy.is_alive and enemy.hp > 0 for enemy in state.enemies.values()):
                    return False
            elif condition_type == 'collect_all_items':
                required_items = set(self.items.keys())
                if not required_items.issubset(state.collected_items):
                    return False
            elif condition_type == 'defeat_all_enemies_and_reach_goal':
                # Special compound condition for compatibility
                if state.player_pos != self.goal_pos:
                    return False
                if any(enemy.is_alive and enemy.hp > 0 for enemy in state.enemies.values()):
                    return False

        return True

    def _heuristic(self, state: GameState) -> int:
        """Calculate heuristic cost to goal (combat-aware)"""
        # Distance to goal
        goal_dist = abs(state.player_pos[0] - self.goal_pos[0]) + abs(state.player_pos[1] - self.goal_pos[1])

        # Add cost for uncollected items (improved heuristic)
        uncollected_items = set(self.items.keys()) - state.collected_items
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

        return goal_dist + item_cost + combat_cost

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

        # Check enemies (cannot move into living enemy position)
        for enemy_state in state.enemies.values():
            if (enemy_state.position == (new_x, new_y) and
                enemy_state.is_alive and enemy_state.hp > 0):
                return False

        return True

    def _can_attack(self, state: GameState) -> bool:
        """Check if player can attack an enemy and survive the combat"""
        # NOTE: Attack happens BEFORE enemy movement in actual game engine
        # Check attack target based on enemy positions BEFORE their movement
        dx, dy = self.directions[state.player_dir]
        target_x = state.player_pos[0] + dx
        target_y = state.player_pos[1] + dy

        # Check if there's a living enemy at target position BEFORE enemy movement
        for enemy_state in state.enemies.values():
            if (enemy_state.position == (target_x, target_y) and
                enemy_state.is_alive and enemy_state.hp > 0):

                # Check if player can survive combat with this enemy
                if self._can_player_survive_combat(state, enemy_state):
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
            enemy_counterattacks = turns_to_kill_enemy - enemy_first_attack_turn + 1

        # プレイヤーが受ける総ダメージ
        total_damage_to_player = max(0, enemy_counterattacks) * enemy_attack

        can_survive = total_damage_to_player < player_hp

        # デバッグ情報にアイテム効果を含める
        base_attack = self.stage.player.attack_power
        attack_bonus = player_attack - base_attack
        attack_info = f"{player_attack}"
        if attack_bonus > 0:
            attack_info += f" (基本:{base_attack}+装備:{attack_bonus})"

        print(f"🔍 戦闘生存チェック（段階的回転対応）:")
        print(f"   プレイヤーHP={player_hp}, 敵HP={enemy_hp}")
        print(f"   プレイヤー攻撃力={attack_info}, 敵攻撃力={enemy_attack}")
        print(f"   敵方向={enemy_direction} → 目標方向={target_direction} (回転ターン数={rotation_turns})")
        print(f"   敵を倒すターン数={turns_to_kill_enemy}, 敵の反撃開始ターン={enemy_first_attack_turn}")
        print(f"   敵の反撃回数={enemy_counterattacks}, 予想ダメージ={total_damage_to_player}")
        print(f"   生存可能={can_survive}")

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
                print(f"  🔍 アイテム{item_id}: 攻撃力ボーナス+35追加")

        total_attack = base_attack + attack_bonus
        print(f"  🔍 最終攻撃力: {base_attack} + {attack_bonus} = {total_attack}")
        return total_attack

    def _can_pickup(self, state: GameState) -> bool:
        """Check if player can pick up an item"""
        # Check if there's an item at player position
        for item_id, item_pos in self.items.items():
            if item_pos == state.player_pos and item_id not in state.collected_items:
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

            # Find and damage enemy
            for enemy_id, enemy_state in new_state.enemies.items():
                if (enemy_state.position == target_pos and
                    enemy_state.is_alive and enemy_state.hp > 0):

                    # Calculate damage to enemy
                    new_enemy_hp, enemy_dies = self._calculate_combat_damage(
                        self._calculate_effective_attack_power(new_state), enemy_state.hp
                    )

                    # 攻撃を受けたエネミーはalert状態になる（ゲームエンジンと同じ）
                    # Update enemy state with alert status after being attacked
                    new_enemy_state = EnemyState(
                        position=enemy_state.position,
                        direction=enemy_state.direction,
                        hp=new_enemy_hp,
                        max_hp=enemy_state.max_hp,
                        attack_power=enemy_state.attack_power,
                        behavior=enemy_state.behavior,
                        is_alive=not enemy_dies,
                        patrol_path=enemy_state.patrol_path,
                        patrol_index=enemy_state.patrol_index,
                        vision_range=enemy_state.vision_range,
                        is_alert=True,  # 攻撃を受けたらalert状態に変更
                        last_seen_player=state.player_pos  # プレイヤー位置を記録
                    )
                    new_state.enemies[enemy_id] = new_enemy_state

                    # ゲームエンジンでは攻撃後エネミーの反撃は次のターンのAI処理で行われる
                    # (In game engine, enemy counter-attack happens in next turn's AI processing)

                    break

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

        # ゲームエンジンと同じ処理順序：プレイヤーアクション実行後にエネミーAI処理
        # (Game engine processes player action first, then enemy AI)
        self._apply_enemy_ai(new_state)

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
        return path

    def _calculate_initial_patrol_index(self, enemy_config) -> int:
        """Calculate the initial patrol index for an enemy based on its position (same as game engine)"""
        if not hasattr(enemy_config, 'patrol_path') or not enemy_config.patrol_path:
            return 0

        enemy_pos = tuple(enemy_config.position)
        patrol_path = [tuple(pos) for pos in enemy_config.patrol_path]

        # Find current position in patrol path (same as game engine _initialize_patrol_index)
        for i, pos in enumerate(patrol_path):
            if pos == enemy_pos:
                return i  # Return exact index, same as game engine

        return 0  # Fallback to start of path

    def _apply_enemy_ai(self, state: GameState) -> None:
        """Apply enemy AI behavior (patrol, combat, etc.)"""
        for enemy_id, enemy_state in state.enemies.items():
            if not enemy_state.is_alive or enemy_state.hp <= 0:
                continue

            # Alert状態のエネミーは積極的に行動（ゲームエンジンと同じ）
            # Alert enemies actively pursue and attack player (same as game engine)
            if enemy_state.is_alert:
                # Alert状態では常に積極的な戦闘AI
                self._apply_combat_ai(state, enemy_state)
            # Check if enemy can see player (use enemy's actual vision_range)
            elif self._can_enemy_see_player(state, enemy_state):
                # Combat behavior - move towards or attack player
                self._apply_combat_ai(state, enemy_state)
            elif enemy_state.behavior == "patrol" and enemy_state.patrol_path:
                # Patrol behavior
                self._apply_patrol_ai(state, enemy_state)
            elif enemy_state.behavior == "static":
                # Static enemiesもプレイヤーを視界で発見したらchase modeに切り替わる（ゲームエンジンと同じ）
                # Static enemies also switch to chase mode when player detected (same as game engine)
                if self._can_enemy_see_player(state, enemy_state):
                    # プレイヤー発見！alert状態に切り替え
                    enemy_state.is_alert = True
                    enemy_state.last_seen_player = state.player_pos
                    # Chase AIを実行
                    self._apply_combat_ai(state, enemy_state)
                # else: 視界にプレイヤーがいない場合は何もしない（static behavior）

    def _can_enemy_see_player(self, state: GameState, enemy_state: EnemyState) -> bool:
        """Check if enemy can see the player using directional cone vision (same as game engine)"""
        px, py = state.player_pos
        ex, ey = enemy_state.position

        # Use enemy's actual vision_range (fallback to default if None)
        vision_range = enemy_state.vision_range if enemy_state.vision_range is not None else 3

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

                # Check if this target position matches player position
                if (target_x, target_y) == (px, py):
                    # 90-degree field of view check (same as engine/__init__.py:311)
                    if abs(offset) <= distance:
                        return True

        return False

    def _apply_combat_ai(self, state: GameState, enemy_state: EnemyState) -> None:
        """Apply combat AI - attack player with gradual rotation (same as game engine)"""
        px, py = state.player_pos
        ex, ey = enemy_state.position

        # Calculate Manhattan distance
        distance = abs(px - ex) + abs(py - ey)

        # If adjacent, attack with gradual rotation (same as game engine)
        if distance == 1:
            # Calculate required direction to face player
            dx = px - ex
            dy = py - ey

            if dx == 1:
                target_direction = "E"
            elif dx == -1:
                target_direction = "W"
            elif dy == 1:
                target_direction = "S"
            elif dy == -1:
                target_direction = "N"
            else:
                return  # Should not happen for adjacent positions

            # ゲームエンジンの段階的回転システムを実装
            # Implement gradual rotation system from game engine
            if enemy_state.direction != target_direction:
                # 段階的回転: 1ターンに1段階回転
                # Gradual rotation: one step per turn
                rotation_map = {
                    ("N", "E"): "E", ("N", "S"): "E", ("N", "W"): "W",
                    ("E", "S"): "S", ("E", "W"): "S", ("E", "N"): "N",
                    ("S", "W"): "W", ("S", "N"): "W", ("S", "E"): "E",
                    ("W", "N"): "N", ("W", "E"): "N", ("W", "S"): "S"
                }

                # 回転処理（方向転換のみ、移動はしない）
                key = (enemy_state.direction, target_direction)
                if key in rotation_map:
                    enemy_state.direction = rotation_map[key]
            else:
                # 正しい方向を向いているので攻撃実行
                # Facing correct direction, execute attack
                new_player_hp = max(0, state.player_hp - enemy_state.attack_power)
                state.player_hp = new_player_hp
        else:
            # 隣接していない場合は移動
            # Not adjacent, move towards player
            self._apply_chase_ai(state, enemy_state)

    def _apply_patrol_ai(self, state: GameState, enemy_state: EnemyState) -> None:
        """Apply patrol AI - patrol mode or chase mode based on player detection"""
        if not enemy_state.is_alive:
            return

        # Check if enemy can see player
        can_see_player = self._can_enemy_see_player(state, enemy_state)

        if can_see_player and not enemy_state.is_alert:
            # Player detected! Switch to chase mode
            enemy_state.is_alert = True
            enemy_state.last_seen_player = state.player_pos
            # Continue to chase logic below
        elif not can_see_player and enemy_state.is_alert:
            # Lost sight of player, return to patrol mode
            enemy_state.is_alert = False
            enemy_state.last_seen_player = None
            # Continue to patrol logic below

        if enemy_state.is_alert:
            # Chase mode: move toward player
            self._apply_chase_ai(state, enemy_state)
        else:
            # Patrol mode: follow patrol path
            self._apply_standard_patrol_ai(state, enemy_state)

    def _apply_standard_patrol_ai(self, state: GameState, enemy_state: EnemyState) -> None:
        """Apply standard patrol AI - move enemy along patrol path (same as game engine)"""
        if not enemy_state.patrol_path or len(enemy_state.patrol_path) <= 1:
            return

        # Get current target position (same as game engine's get_next_patrol_position)
        # Based on actual game engine: returns current position (current_patrol_index)
        current_target = tuple(enemy_state.patrol_path[enemy_state.patrol_index])

        # If already at current target, advance to next patrol point (same as game engine)
        if enemy_state.position == current_target:
            enemy_state.patrol_index = (enemy_state.patrol_index + 1) % len(enemy_state.patrol_path)
            current_target = tuple(enemy_state.patrol_path[enemy_state.patrol_index])

        # Move towards target if different from current position
        if current_target != enemy_state.position:
            # Calculate required direction (same logic as game engine)
            dx = current_target[0] - enemy_state.position[0]
            dy = current_target[1] - enemy_state.position[1]

            # Choose required direction (x-axis priority, same as game engine)
            if dx != 0:
                required_direction = "E" if dx > 0 else "W"
            elif dy != 0:
                required_direction = "S" if dy > 0 else "N"
            else:
                return  # Already at target

            # Gradual rotation: turn first if direction doesn't match (same as game engine)
            if enemy_state.direction != required_direction:
                # Perform rotation only (same as game engine)
                enemy_state.direction = required_direction
            else:
                # Move in the current direction (same as game engine)
                offset_x = 1 if required_direction == "E" else (-1 if required_direction == "W" else 0)
                offset_y = 1 if required_direction == "S" else (-1 if required_direction == "N" else 0)

                next_position = (enemy_state.position[0] + offset_x, enemy_state.position[1] + offset_y)

                # Check if next position is valid (not blocked by player or walls)
                if (next_position not in self.walls and
                    next_position != state.player_pos):
                    # Update enemy position
                    enemy_state.position = next_position

    def _apply_chase_ai(self, state: GameState, enemy_state: EnemyState) -> None:
        """Apply chase AI - move toward player"""
        player_pos = state.player_pos
        enemy_pos = enemy_state.position

        # Calculate direction to player
        dx = player_pos[0] - enemy_pos[0]
        dy = player_pos[1] - enemy_pos[1]

        # Determine movement direction (prioritize x-axis like game engine)
        # Game engine uses "接触重視x軸優先" - prioritize x-axis when distances are equal
        if abs(dx) >= abs(dy):
            # Move horizontally (prioritize x-axis)
            if dx > 0:
                new_pos = (enemy_pos[0] + 1, enemy_pos[1])
                enemy_state.direction = "E"
            else:
                new_pos = (enemy_pos[0] - 1, enemy_pos[1])
                enemy_state.direction = "W"
        else:
            # Move vertically (only when abs(dy) > abs(dx))
            if dy > 0:
                new_pos = (enemy_pos[0], enemy_pos[1] + 1)
                enemy_state.direction = "S"
            else:
                new_pos = (enemy_pos[0], enemy_pos[1] - 1)
                enemy_state.direction = "N"

        # Check if movement is valid
        if (new_pos not in self.walls and
            0 <= new_pos[0] < self.width and
            0 <= new_pos[1] < self.height and
            new_pos != state.player_pos):  # Don't move into player position
            enemy_state.position = new_pos