class Solution {
    public boolean isValidSudoku(char[][] board) {
        final int SIZE = 9;
        int[] rows = new int[SIZE];
        int[] cols = new int[SIZE];
        int[] boxes = new int[SIZE];

        for (int r = 0 ; r < SIZE; r++) {
            for (int c = 0; c < SIZE; c++) {
                final char ch = board[r][c];
                if (ch == '.')
                    continue;
                final int box = (r/3) * 3 + c/3;
                final int bit = 1 << (ch - '1');

                if ((rows[r]&bit | cols[c]&bit | boxes[box]&bit) > 0)
                    return false;

                rows[r] = rows[r] | bit;
                cols[c] = cols[c] | bit;
                boxes[box] = boxes[box] | bit;
            }
        }

        return true;
    }
}
