# -*- coding: utf-8 -*-
"""
Created on Sun May 16 16:35:09 2021

@author: ThinkPad
"""

import random
import time
import numpy as np
import copy
import pandas as pd


def input_change(Input):
    if Input[1] in [2,3,4,5,6]:
        return [Input[0], Input[1]-1]
    else:
        return [Input[0], 6]

def output_change(output):
    if output[1] in [1,2,3,4,5]:
        return [output[0], output[1]+1]
    else:
        return [output[0], 1]
    
def dices_change(dices):
    new = []
    for i in range(5):
        if dices[i] in [1,2,3,4,5]:
            new.append(dices[i]+1)
        else:
            new.append(1)
    return new


def roll(num=5):
    '''Roll 5 dices, return the list of 5 dices'''
    items = []
    for i in range(0, num):
        items.append(random.randint(1,6))
    return items

class Record(object):
    """
    A record for game state
    """
    
    def __init__(self, dice_num=5):
        #self.dice = roll(dice_num)
        self.states = {}
        
    def init_record(self):
        self.availables = list(range(1+1+8*6))
        
        for m in self.availables:
            self.states[m] = 1
            
    def choice_to_order(self, choice):
        if choice == 0:
            return 49
        if choice == [2,6]:
            return 0
        m = choice[0]
        n = choice[1]
        order = (m-3)*6 + n
        return order
    
    def order_to_choice(self, order):
        if order == 0:
            return [2,6]
        if order == 49:
            return 0 
        else:
            m = int((order-0.1)//6) + 3
            n = order%6
            if n == 0:
                n = 6
            return [m,n]
    
    def current_state(self):
        if len(self.availables) == 50:
            return -1
        else:
            return min(self.availables)-1
            
            
    def update(self, player, order):
        self.states[order] = player
        if order >= 49:
            #print("Game Over!")
            pass
        else:
            for i in range(min(self.availables), order + 1):
                self.availables.remove(i)
        
class MCTS(object):
    
    def __init__(self, board_record, play_turn, dices, time = 10, max_actions = 5):
        self.record = board_record
        #self.record2 = record2
        self.play_turn = play_turn
        self.cal_time = float(time)
        self.max_actions = max_actions
        self.dices = dices
        
        self.player = play_turn[0]
        self.counter = 0
        self.confident = 1.96
        self.plays = {}
        self.wins = {}
        self.max_depth = 1
        
        self.choice_length = len(board_record.availables)
        
    def strategy_pool(self):
        if len(self.record.availables) >= 7:
            return [0,1,2,3,4,5,6]
        elif len(self.record.availables) == 50:
            return [1,2,3,4,5,6]
        else:
            return 0
        
        
    def get_action(self, current_state):
        
        self.plays = {}
        self.wins = {}
        #self.simulation_dices = roll()
        
        #self.index_depth = self.plays.index_num(self.dices)
        #self.index_breadth = self.plays.index_num(self.simulation_dices)
        self.counter = 0
        simulation = 0
        begin = time.time()
        while time.time() - begin < self.cal_time:
            self.simulation_dices = roll()
            record_copy = copy.deepcopy(self.record)
            turn_copy = copy.deepcopy(self.play_turn)
            self.run_simulation(record_copy, turn_copy) # Run MCTS algorithm
            simulation += 1
            
        print("total run:", simulation)
        print(self.counter)
        #print(self.plays)
        #print(self.wins)
        order = self.select_one_move(current_state)
        choice = self.record.order_to_choice(order)
        if choice != 0:
            choice = output_change(choice)
        
        print("AI move: " , choice)
        return order
    
    def run_simulation(self, record, play_turn):
        
        plays = self.plays
        wins = self.wins
        #availables = record.availables
        current_state = record.current_state()
        self.if_one_is_applied = False
        
        player = self.get_player(play_turn) # Get the player to make decision now
        
        #plays[(player, current_state)] = {}
        #wins[(player, current_state)] = {}
        
        winner = -1
        visited_states = set()
        expand = True
        
        #index_depth = self.plays.index_num(dices)
        #index_breadth = self.plays.index_num(self.simulation_dices)
        
        for i in range(1, self.max_actions + 1):
            if i == self.max_actions:
                strategy = 0
                next_policy = 49
            else:
                if current_state == -1:
                    if (player, current_state) in plays and len(plays[(player, current_state)]) == 7:
                
                        log_total = np.log(np.sum(plays[(player, current_state)][strategy] for strategy in [1,2,3,4,5,6,7]))
                        value, strategy = max(
                                ((wins[(player, current_state)][strategy] / plays[(player, current_state)][strategy]) + 
                                 self.confident*np.sqrt(2*log_total/plays[(player, current_state)][strategy]), strategy)
                                for strategy in [1,2,3,4,5,6,7])
                        next_policy = current_state + strategy
                    else:
                        strategy = random.choice([1,2,3,4,5,6,7])
                        next_policy = current_state + strategy
             
                else:
                
                    if (player, current_state) in plays and len(plays[(player, current_state)]) == 7:
                
                        log_total = np.log(np.sum(plays[(player, current_state)][strategy] for strategy in self.strategy_pool()))
                        value, strategy = max(
                                ((wins[(player, current_state)][strategy] / plays[(player, current_state)][strategy]) + 
                                 self.confident*np.sqrt(2*log_total/plays[(player, current_state)][strategy]), strategy)
                                for strategy in self.strategy_pool())
                        
                        if strategy != 0:
                            next_policy = current_state + strategy
                            if next_policy > 49:
                                next_policy = 49
                        else:
                            next_policy = 49
                    else:
                        strategy = random.choice([0,1,2,3,4,5,6])
                        if strategy != 0:
                            next_policy = current_state + strategy
                            if next_policy > 49:
                                next_policy = 49
                        else:
                            next_policy = 49
            record.update(player, next_policy)
            
            if (player, current_state) not in plays:
                plays[(player, current_state)] = {}
                wins[(player, current_state)] = {}
            
            if expand and strategy not in plays[(player, current_state)] :
                expand = False
                plays[(player, current_state)][strategy] = 1
                wins[(player, current_state)][strategy] = 0
                if i > self.max_depth:
                    self.max_depth = i
                    
            visited_states.add((player, current_state, strategy))
            
            if next_policy in [0,6,12,18,24,36,42,48]: #[0,6,12,18,24,36,42,48][0,1,7,13,19,25,31,37,43]
                self.if_one_is_applied = True
            if next_policy == 49:
                self.call = player
                winner = self.decide_the_winner(record)
                self.counter += 1
                break
            
            player = self.get_player(play_turn)
            
            current_state = next_policy
        
        # back up 
        for player, current_state, strategy in visited_states:
            if strategy not in plays[(player, current_state)]:
                continue
            plays[(player, current_state)][strategy] += 1
            self.plays = plays
            if player == winner:
                wins[(player, current_state)][strategy] += 1
                self.wins = wins
                
    
    def get_player(self, players):
        p = players.pop(0)
        players.append(p)
        return p 
    
    def select_one_move(self, current_state):
        percent_wins, strategy = max((
                 (self.wins.get((self.player, current_state)).get(strategy, 0) / 
                 self.plays.get((self.player, current_state)).get(strategy, 1)), 
                 strategy)
                 for strategy in self.strategy_pool())
        if strategy == 0:
            next_policy = 49
        else:
            next_policy = current_state + strategy
        
        return next_policy
    
    def decide_the_winner(self, record):
        """Find out who's the winner"""
        total_dices = self.simulation_dices + self.dices
        state_exist = record.availables
        latest = min(state_exist)
        call_player = self.call
        if call_player == self.play_turn[0]:
            raise_player = self.play_turn[1]
        else:
            raise_player = self.play_turn[0]
        curr_decision = record.order_to_choice(latest - 1)
        key_num = curr_decision[1]
        if self.if_one_is_applied == False:
            if total_dices.count(6) + total_dices.count(key_num) >= curr_decision[0]:
                winner = raise_player # raise player wins
            else:
                winner = call_player # call player wins
        else:
            if total_dices.count(key_num) >= curr_decision[0]:
                winner = raise_player
            else:
                winner = call_player
        return winner
        
    
    def __str__(self):
        return "Liar Dice"
    
class Human_player(object):
    """
    This is for real player
    """
    def __init__(self, record, player):
        self.record = record
        self.player = player
        self.dices = roll()
        self.output_dices = dices_change(self.dices)
    def get_action(self, current_state):
        try:
            print("Your dices are:", self.output_dices)
            call = input("Do you want to call ?(Y/N)\n")
            if call == 'N':
                action = [int(i,10) for i in input("Your choice(please split by comma):").split(",")]
                action = input_change(action)
            elif call == 'Y':
                action = 0
                return 49
            order = self.record.choice_to_order(action)
        except Exception as e:
            order = -1
        if order == -1 or order not in self.record.availables:
            print("invalid")
            order = self.get_action
        return order
    
    def __str__(self):
        return "Human"

class Game(object):
    """
    The game server
    """
    def __init__(self, record, **kwargs):
        self.record = record
        self.player = [1,2]
        self.time = float(kwargs.get('time',10))
        self.max_actions = int(kwargs.get('max_action', 5))
        self.ai_dices = roll()
        #self.human_dices = roll()
        
    def start_game(self):
        player_1, player_2 = self.init_player()
        self.record.init_record()
        AI_player = MCTS(self.record, [player_1, player_2], self.ai_dices, time = 10, max_actions = 4)
        human_player = Human_player(self.record, player_2)
        self.human_dices = human_player.dices
        players = {}
        players[player_1] = AI_player
        players[player_2] = human_player
        self.turn = [player_1, player_2]
        self.if_one_is_applied = False
        random.shuffle(self.turn)
        while(1):
            a = self.turn.pop(0)
            self.turn.append(a)
            player_in_turn = players[a]
            order = player_in_turn.get_action(self.record.current_state())
            if order in [0,6,12,18,24,36,42,48]:
                self.if_one_is_applied = True
            self.record.update(a, order)
            #print("record:", a, order)
            self.output(self.record, human_player, AI_player, player_in_turn, order)
            if order == 49:
                self.call = a
                winner = self.if_end(self.record)
                print("Game over, the winner is", players[winner])
                print("Ai's Dices are:", dices_change(self.ai_dices))
                print("Human's Dices are:", dices_change(self.human_dices))
                break
        
    def init_player(self):
        P = list(range(len(self.player)))
        index1 = random.choice(P)
        P.remove(index1)
        index2 = random.choice(P)
        
        return self.player[index1], self.player[index2]
    
    def if_end(self, record):
        """
        check if the game is ended
        """
        #winner = ai.decide_the_winner(self.record)
        total_dices = self.ai_dices + self.human_dices
        state_exist = record.availables
        latest = min(state_exist)
        #raise_player = self.turn[0]
        call_player = self.call
        if call_player == self.turn[0]:
            raise_player = self.turn[1]
        else:
            raise_player = self.turn[0]
        curr_decision = record.order_to_choice(latest - 1)
        key_num = curr_decision[1]
        if self.if_one_is_applied == False: #if '1' hasn't been applied, '1' can be considered as any number
            if total_dices.count(6) + total_dices.count(key_num) >= curr_decision[0]: 
                winner = raise_player # raise player wins
            else:
                winner = call_player # call player wins
        else: # if '1' has been applied, '1' can only be considered as itself
            if total_dices.count(key_num) >= curr_decision[0]:
                winner = raise_player
            else:
                winner = call_player
        return winner
        
    def output(self, record, human_player, AI_player, player_in_turn, order):
        """
        Output the information about game process.
        """
        strategy = self.record.order_to_choice(order)
        if strategy !=0:
            strategy = output_change(strategy)
        if player_in_turn == human_player:
            if order == 49:
                print("Human decides to call")
            else:
                print("Human player guesses there are %d, '%d's" %(strategy[0], strategy[1]))
        else:
            if order == 49:
                print("AI decides to call")
            else:
                print("AI player guesses there are %d, '%d's" %(strategy[0], strategy[1]))
                
def run():
    try:
        record = Record()
        game = Game(record, time = 10)
        game.start_game()
    except KeyboardInterrupt:
        print('\n\rquit')
    

if __name__ == '__main__':
    run()              