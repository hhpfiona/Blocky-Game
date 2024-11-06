from __future__ import annotations
import math
import random
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> list[Goal]:
    """Return a randomly generated list of goals with length <num_goals>.

    Each goal must be randomly selected from the two types of Goals provided
    and must have a different randomly generated colour from COLOUR_LIST.
    No two goals can have the same colour.

    Preconditions:
    - num_goals <= len(COLOUR_LIST)
    """
    colours = COLOUR_LIST.copy()
    goals = []
    while len(goals) < num_goals:

        goal = random.choice([1, 2])
        col = random.choice(colours)
        colours.remove(col)

        if goal == 1:
            goals.append(PerimeterGoal(col))
        elif goal == 2:
            goals.append(BlobGoal(col))

    return goals

def flatten(block: Block) -> list[list[tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j].

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    if block.colour is not None and block.level <= block.max_depth:
        unit_cells = []
        i = 0
        rows_columns = 2**(block.max_depth - block.level)
        while len(unit_cells) < rows_columns:
            unit_cells.append([block.colour])
            while len(unit_cells[i]) < rows_columns:
                unit_cells[i].append(block.colour)
            i += 1
        return unit_cells
    else:
        flattened = []
        top_left = flatten(block.children[1])
        bottom_left = flatten(block.children[2])
        top_right = flatten(block.children[0])
        bottom_right = flatten(block.children[3])

        rows_cols = 2**(block.max_depth - block.level)

        for i in range(rows_cols // 2):
            left = top_left[i] + bottom_left[i]
            flattened.append(left)
        for j in range(rows_cols // 2):
            right = top_right[j] + bottom_right[j]
            flattened.append(right)

        return flattened


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    Instance Attributes:
    - colour: The target colour for this goal, that is the colour to which
              this goal applies.
    """
    colour: tuple[int, int, int]

    def __init__(self, target_colour: tuple[int, int, int]) -> None:
        """Initialize this goal to have the given <target_colour>.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given <board>.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """A goal to maximize the presence of this goal's target colour
    on the board's perimeter.
    """

    def __init__(self, target_colour: tuple[int, int, int]) -> None:
        Goal.__init__(self, target_colour)

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.

        The score for a PerimeterGoal is defined to be the number of unit cells
        on the perimeter whose colour is this goal's target colour. Corner cells
        count twice toward the score.
        """
        score = 0
        f = flatten(board)

        for i in range(len(f)):

            top_col = f[i][0]
            bot_col = f[i][len(f) - 1]

            if top_col == self.colour:
                score += 1
            if bot_col == self.colour:
                score += 1

            left_col = f[0][i]
            right_col = f[len(f) - 1][i]

            if left_col == self.colour:
                score += 1
            if right_col == self.colour:
                score += 1

        return score

    def description(self) -> str:
        """Return a description of this goal.
        """
        return (f'Goal: Maximize the presence of {colour_name(self.colour)} '
                f'on the perimeter of the board')


class BlobGoal(Goal):
    """A goal to create the largest connected blob of this goal's target
    colour, anywhere within the Block.
    """

    def __init__(self, target_colour: tuple[int, int, int]) -> None:
        Goal.__init__(self, target_colour)

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.

        The score for a BlobGoal is defined to be the total number of
        unit cells in the largest connected blob within this Block.
        """
        max_blob = 0
        flat = flatten(board)

        visited = []
        for column in range(len(flat)):
            visited.append([])
            for cell in range(column):
                visited[column].append(-1)

        for i in range(board.size):
            for j in range(board.size):
                new_blob = self._undiscovered_blob_size((i, j), flat, visited)
                max_blob = max(max_blob, new_blob)

        return max_blob

    def _undiscovered_blob_size(self, pos: tuple[int, int],
                                board: list[list[tuple[int, int, int]]],
                                visited: list[list[int]]) -> int:
        """Return the size of the largest connected blob in <board> that (a) is
        of this Goal's target <colour>, (b) includes the cell at <pos>, and (c)
        involves only cells that are not in <visited>.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure (to <board>) that, in each cell,
        contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.

        If <pos> is out of bounds for <board>, return 0.
        """
        col = pos[0]
        row = pos[1]

        try:
            cell = board[col][row]
            vis = visited[col][row]
        except IndexError:
            # out of bounds
            return 0

        if vis != -1:  # already visited
            return 0
        elif cell != self.colour:  # unvisited but not target colour
            visited[pos[0]][pos[1]] = 0
            return 0
        else:  # unvisited with target colour
            visited[pos[0]][pos[1]] = 1
            max_blob = 1

            # Recursively find connected blobs up, down, left, right of pos
            u = self._undiscovered_blob_size((pos[0], pos[1]-1), board, visited)
            d = self._undiscovered_blob_size((pos[0], pos[1]+1), board, visited)
            l = self._undiscovered_blob_size((pos[0]-1, pos[1]), board, visited)
            r = self._undiscovered_blob_size((pos[0]+1, pos[1]), board, visited)

            max_blob += u + d + l + r

            return max_blob

    def description(self) -> str:
        """Return a description of this goal.
        """
        return (f'Goal: Create the largest blob of {colour_name(self.colour)} '
                f'anywhere within this block.')


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
