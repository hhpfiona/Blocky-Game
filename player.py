from __future__ import annotations
import random
import pygame

from block import Block
from goal import Goal, generate_goals

from actions import Action, KEY_ACTION, ROTATE_CLOCKWISE, \
    ROTATE_COUNTER_CLOCKWISE, \
    SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PASS, PAINT, COMBINE


def create_players(num_human: int, num_random: int, smart_players: list[int]) \
        -> list[Player]:
    """Return a new list of Player objects.

    <num_human> is the number of human player, <num_random> is the number of
    random players, and <smart_players> is a list of difficulty levels for each
    SmartPlayer that is to be created.

    The list should contain <num_human> HumanPlayer objects first, then
    <num_random> RandomPlayer objects, then the same number of SmartPlayer
    objects as the length of <smart_players>. The difficulty levels in
    <smart_players> should be applied to each SmartPlayer object, in order.

    Player ids are given in the order that the players are created, starting
    at id 0.

    Each player is assigned a random goal.
    """
    i = 0
    players = []
    goals = generate_goals(num_human + num_random + len(smart_players))
    while len(players) < num_human:
        players.append(HumanPlayer(i, goals[i]))
        i += 1
    while len(players) - num_human < num_random:
        players.append(RandomPlayer(i, goals[i]))
        i += 1
    for j in range(len(smart_players)):
        # make sure that this lines up with smart player implementation
        players.append(SmartPlayer(i, goals[i], smart_players[j]))
        i += 1
    return players


def _get_block(block: Block, location: tuple[int, int], level: int) -> \
        Block | None:
    """Return the Block within <block> that is at <level> and includes
    <location>. <location> is a coordinate-pair (x, y).

    A block includes all locations that are strictly inside it, as well as
    locations on the top and left edges. A block does not include locations that
    are on the bottom or right edge.

    If a Block includes <location>, then so do its ancestors. <level> specifies
    which of these blocks to return. If <level> is greater than the level of
    the deepest block that includes <location>, then return that deepest block.

    If no Block can be found at <location>, return None.

    Preconditions:
        - block.level <= level <= block.max_depth
    """
    if not _check_location(block, location):
        return None
    elif block.level == level or block.colour is not None:
        return block
    else:
        if block.max_depth < level:
            return _get_block(block, location, block.max_depth)
    for child in block.children:
        if _check_location(child, location):
            return _get_block(child, location, level)


def _check_location(block: Block, location: tuple[int, int]) -> \
        bool:
    """Return true if the given <location> is included in <block>
    Private helper function for the function _get_block."""
    x = block.position[0]
    x_1 = block.position[0] + block.size
    y = block.position[1]
    y_1 = block.position[1] + block.size

    if x <= location[0] < x_1 and y <= location[1] < y_1:
        return True
    return False

def _get_random_block(board: Block) -> Block:
    """
    A private helper for RandomPlayer and SmartPlayer. Return a random block at
    a random depth within <board>.
    """
    random_pos = (random.randint(0, board.size), random.randint(0, board.size))
    random_level = random.randint(1, board.max_depth)

    return _get_block(board, random_pos, random_level)


def _move(block: Block, move: int, player: Player) -> tuple[bool, Action]:
    """
    A private helper for RandomPlayer and SmartPlayer. Execute move on block.
    To be used on a copy of the actual board.
    """
    if move == 0:
        return block.smash(), SMASH
    elif move == 1:
        return block.swap(0), SWAP_HORIZONTAL
    elif move == 2:
        return block.swap(1), SWAP_VERTICAL
    elif move == 3:
        return block.rotate(1), ROTATE_CLOCKWISE
    elif move == 4:
        return block.rotate(3), ROTATE_COUNTER_CLOCKWISE
    elif move == 5:
        return block.combine(), COMBINE
    elif move == 6:
        return block.paint(player.goal.colour), PAINT
    elif move == 7:
        return True, PASS

class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    Instance Attributes:
    - id: This player's number.
    - goal: This player's assigned goal for the game.
    - penalty: The penalty accumulated by this player through their actions.
    """
    id: int
    goal: Goal
    penalty: int

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.id = player_id
        self.penalty = 0

    def get_selected_block(self, board: Block) -> Block | None:
        """Return the block that is currently selected by the player.

        If no block is selected by the player, return None.
        """
        raise NotImplementedError

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player based on the pygame event.
        """
        raise NotImplementedError

    def generate_move(self, board: Block) -> \
            tuple[Action, Block] | None:
        """Return a potential move to make on the <board>.

        The move is a tuple consisting of an action and
        the block the action will be applied to.

        Return None if no move can be made, yet.
        """
        raise NotImplementedError


class HumanPlayer(Player):
    """A human player.

    Instance Attributes:
    - _level: The level of the Block that the user selected most recently.
    - _desired_action: The most recent action that the user is attempting to do.

    Representation Invariants:
    - self._level >= 0
    """
    _level: int
    _desired_action: Action | None

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        Player.__init__(self, player_id, goal)

        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _desired_action to None.
        self._level = 0
        self._desired_action = None

    def get_selected_block(self, board: Block) -> Block | None:
        """Return the block that is currently selected by the player based on
        the position of the mouse on the screen and the player's desired level.

        If no block is selected by the player, return None.
        """
        mouse_pos = pygame.mouse.get_pos()
        block = _get_block(board, mouse_pos, self._level)

        return block

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the relevant keyboard events made by the player based on
        the mapping in KEY_ACTION, as well as the W and S keys for changing
        the level.
        """
        if event.type == pygame.KEYUP:
            if event.key in KEY_ACTION:
                self._desired_action = KEY_ACTION[event.key]
            elif event.key == pygame.K_w:
                self._level -= 1
                self._desired_action = None
            elif event.key == pygame.K_s:
                self._level += 1
                self._desired_action = None

    def generate_move(self, board: Block) -> \
            tuple[Action, Block] | None:
        """Return the move that the player would like to perform. The move may
        not be valid.

        Return None if the player is not currently selecting a block.

        This player's desired action gets reset after this method is called.
        """
        block = self.get_selected_block(board)

        if block is None or self._desired_action is None:
            self._correct_level(board)
            self._desired_action = None
            return None
        else:
            move = self._desired_action, block

            self._desired_action = None
            return move

    def _correct_level(self, board: Block) -> None:
        """Correct the level of the block that the player is currently
        selecting, if necessary.
        """
        self._level = max(0, min(self._level, board.max_depth))


class ComputerPlayer(Player):
    """A computer player. This class is still abstract,
    as how it generates moves is still to be defined
    in a subclass.

    Instance Attributes:
    - _proceed: True when the player should make a move, False when the
                player should wait.
    """
    _proceed: bool

    def __init__(self, player_id: int, goal: Goal) -> None:
        Player.__init__(self, player_id, goal)

        self._proceed = False

    def get_selected_block(self, board: Block) -> Block | None:
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        if (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == pygame.BUTTON_LEFT):
            self._proceed = True

    # Note: this is included just to make pyTA happy; as it thinks
    #       we forgot to implement this abstract method otherwise :)
    def generate_move(self, board: Block) -> \
            tuple[Action, Block] | None:
        raise NotImplementedError


class RandomPlayer(ComputerPlayer):
    """A computer player who chooses completely random moves."""

    def generate_move(self, board: Block) -> \
            tuple[Action, Block] | None:
        """Return a valid, randomly generated move only during the player's
        turn. Return None if the player should not make a move yet.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>.

        This function does not mutate <board>.
        """
        copy = board.create_copy()
        valid_move = False

        if self._proceed:
            while valid_move is False:
                move_block = _get_random_block(copy)
                move_type = random.randint(0, 6)
                move = _move(move_block, move_type, self)
                if move[0] is True:
                    self._proceed = False
                    return move[1], board
        return None


class SmartPlayer(ComputerPlayer):
    """A computer player who chooses moves by assessing a series of random
    moves and choosing the one that yields the best score.

    Private Instance Attributes:
    - _num_test: The number of moves this SmartPlayer will test out before
                 choosing a move.
    """
    _num_test: int

    def __init__(self, player_id: int, goal: Goal, difficulty: int) -> None:
        """Initialize this SmartPlayer with a <player_id> and <goal>.

        Use <difficulty> to determine and record how many moves this SmartPlayer
        will assess before choosing a move. The higher the value for
        <difficulty>, the more moves this SmartPlayer will assess, and hence the
        more difficult an opponent this SmartPlayer will be.

        Preconditions:
        - difficulty >= 0
        """
        super().__init__(player_id, goal)
        self._num_test = difficulty

    def generate_move(self, board: Block) -> \
            tuple[Action, Block] | None:
        """Return a valid move only during the player's turn by assessing
        multiple valid moves and choosing the move that results in the highest
        score for this player's goal.  This score should also account for the
        penalty of the move.  Return None if the player should not make a move.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>. If no move can be found that is better than
        the current score, this player will pass.

        This method does not mutate <board>.
        """
        if not self._proceed:
            return None
        
        best_move = (0, PASS, board)  # score, action, move_block
        moves = []

        while len(moves) < self._num_test:
            b2 = board.create_copy()
            prev_score = self.goal.score(b2)
            move_block = _get_random_block(b2)
            if move_block.level == move_block.max_depth:
                move_type = random.randint(0, 6)
            elif move_block.level == move_block.max_depth - 1:
                move_type = random.randint(0, 5)
            else:
                move_type = random.randint(0, 4)

            valid, action = _move(move_block, move_type, self)
            if valid:
                new_score = self.goal.score(b2)
                score = new_score - prev_score - action.penalty
                moves.append((action, move_block, score))

        for move in moves:
            action = move[0]
            move_block = move[1]
            pos = move_block.position
            lev = move_block.level
            block = _get_block(board, pos, lev)
            score = move[2]
            if score > best_move[0]:
                best_move = [score, action, block]

        if best_move[1] is PASS:
            return None
        return best_move[1], best_move[2]
