import time
import math
import copy

class Bot:
    def __init__(self, color, depth=3, beam_size=1):
        self.player = color
        self.opponent = 3 - color
        self.best_moves = []
        self.depth=depth
        self.beam_size=beam_size

    def predict(self, board):
        if board.count % 2 == 1:
            self.best_moves.clear()
        if self.best_moves != []:
            return self.best_moves.pop()
        else:
            start_time = time.time()
            m1, m2, _ = self.beam_search(board, self.depth, self.beam_size)
            if time.time() - start_time > 20 :
                print('\ntime : ', time.time() - start_time)
            self.best_moves.append(m2)
            return m1

    def beam_search(self, board, depth, beam_size):
        if (board.size**2 - board.count) < (depth-1)*4 + 2 : 
            depth = 1

        size = board.size

        successors = []

        for half_move1 in board.active_area:
            #if half_move1 not in board.available_moves:
            #    continue
            score1 = self.evaluate(board, half_move1)
            x1, y1 = half_move1

            board.state[x1][y1] = board.player_in_turn() #deepcopy is too expensive here

            for half_move2 in board.active_area:
                #if half_move2 not in board.available_moves:
                #    continue
                x2, y2 = half_move2
                if x1*size+y1 < x2*size+y2:
                    score2 = self.evaluate(board, half_move2)
                    score = score1 + score2
                    successors.append([half_move1, half_move2, score])

            board.state[x1][y1] = 0 #rollback

        successors.sort(key=lambda a:a[-1], reverse=True)
        if board.player_in_turn() == self.player:
            best_moves = successors[:beam_size]
        else:
            best_moves = successors[-1:]

        if depth > 1:
            children = []
            for moves in best_moves:
                x1, y1 = moves[0]
                x2, y2 = moves[1]

                b = copy.deepcopy(board)
                b.update(moves[0])
                b.update(moves[1])

                child = self.beam_search(b, depth-1, beam_size)
                children.append([moves[0], moves[1], child[-1]+moves[-1]])

            return max(children, key=lambda a:a[-1])
        else:
            return best_moves[0]

    def evaluate(self, board, half_move):
        s_index = 0

        size = board.size
        state = board.state
        x, y = half_move

        e = math.exp(1)
        player_weight = [0.0, e**2, e**3, e**6, e**6, e**30, 0.0]
        opponent_weight = [-0.0, -2*e**2, -2*e**4, -4*e**6, -4*e**6, -e**29, -0.0]

        for dx, dy in [[1,0], [0,1], [1,1], [1,-1]]:
            for i in range(6):
                if x+dx*(-i) >= 0 and x+dx*(-i+5) < size and y+dy*(-i) >= 0 and y+dy*(-i+5) < size and y+dy*(-i) < size and y+dy*(-i+5) >= 0:
                    
                    index = list([x+dx*(-i+j), y+dy*(-i+j)] for j in range(6))
                    index = index[::-1]
                    window = list(state[x][y] for x, y in index)
                    if self.opponent not in window:
                        cnt = window.count(self.player)
                        if board.player_in_turn() == self.player:
                            s_index += player_weight[cnt]
                        s_index -= player_weight[cnt-1]
                    elif self.player not in window:
                        cnt = window.count(self.opponent)
                        if board.player_in_turn() == self.opponent:
                            s_index += opponent_weight[cnt]
                        s_index -= opponent_weight[cnt-1]

        return s_index

