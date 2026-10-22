class Solution {
public:
    bool isValidSudoku(vector<vector<char>>& board) {
        bool seenRows[9][9] = {};
        bool seenCols[9][9] = {};
        bool seenBoxes[9][9] = {};

        for (int row = 0; row < 9; row++) {
            for (int col = 0; col < 9; col++) {
                if (board[row][col] == '.')
                    continue;

                int digit = board[row][col] - '1';  // 0-8
                int box = row / 3 * 3 + col / 3;

                if (seenRows[row][digit] || seenCols[col][digit] || seenBoxes[box][digit])
                    return false;

                seenRows[row][digit] = true;
                seenCols[col][digit] = true;
                seenBoxes[box][digit] = true;
            }
        }
        return true;
    }
};
