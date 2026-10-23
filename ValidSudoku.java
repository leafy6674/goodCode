class Solution {
  public boolean isValidSudoku(char[][] board) {
    final int SIZE = board.length;
    int[] rows, cols, boxes;
    rows = new int[SIZE];
    cols = new int[SIZE];
    boxes = new int[SIZE];

    for (int r = 0; r < SIZE; r++) {
      for (int c = 0; c < SIZE; c++) {
        final char ch = board[r][c];
        if (ch == '.')
          continue;
        final int marker = 1 << (ch - '1');
        final int box = r/3 * 3 + c/3;
        if ((marker & (rows[r] | cols[c] | boxes[box])) > 0)
          return false;

        rows[r] |= marker;
        cols[c] |= marker;
        boxes[box] |= marker;
      }
    }

    return true;
  }
}
