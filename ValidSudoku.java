class Solution {
    public boolean isValidSudoku(char[][] board) {
        int[] rows = new int[9];
        int[] cols = new int[9];
        int[] boxes = new int[9];

        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                final char ch = board[r][c];
                if (ch == '.') continue;

                final int bit = 1 << (ch - '1');
                // '1'..'9' -> bit 0..8
                final int box = (r / 3) * 3 + c / 3;

                if ((rows[r]&bit | cols[c]&bit | boxes[box]&bit) != 0)
                    return false;

                rows[r] |= bit;
                cols[c] |= bit;
                boxes[box] |= bit;
            }
        }

        return true;
    }
}
