from collections import deque

n = int(input())
n_list = list(map(lambda x: int(x), input().split(' ')))

pig_1_nif = deque()
pig_2_naf = deque()
pig_3_nuf = deque()

pigs_cards = dict()

len_n_list = len(n_list)


def get_key(d: dict, value: int) -> int:
    for _ in d.keys():
        if d[_] == value:
            return _


def get_win_cards(d: dict) -> deque:
    win_table = deque()
    for val in d.values():
        if val != 0:
            win_table.appendleft(val)
    return win_table


while len_n_list > 0:
    pig_1_nif.appendleft(n_list.pop(-1))
    pig_2_naf.appendleft(n_list.pop(-1))
    pig_3_nuf.appendleft(n_list.pop(-1))
    len_n_list -= 3

pigs_cards[2] = pig_1_nif
pigs_cards[1] = pig_2_naf
pigs_cards[0] = pig_3_nuf

table = dict()

while (0, 0) not in table.values():
    if len(pigs_cards[0]) > 0:
        table[0] = pigs_cards[0].pop()
    else:
        table[0] = 0
    if len(pigs_cards[1]) > 0:
        table[1] = pigs_cards[1].pop()
    else:
        table[1] = 0
    if len(pigs_cards[2]) > 0:
        table[2] = pigs_cards[2].pop()
    else:
        table[2] = 0

    if n not in table.values():
        max_value = max(table.values())
        winner_index = get_key(table, max_value)
        any_pig = pigs_cards.get(winner_index)
        any_pig = get_win_cards(table) + any_pig
        pigs_cards[winner_index] = any_pig
    else:
        if 1 in table.values() and n in table.values():
            winner_index = get_key(table, 1)
            any_pig = pigs_cards.get(winner_index)
            any_pig = get_win_cards(table) + any_pig
            pigs_cards[winner_index] = any_pig
        else:
            winner_index = get_key(table, n)
            any_pig = pigs_cards.get(winner_index)
            any_pig = get_win_cards(table) + any_pig
            pigs_cards[winner_index] = any_pig

for key in pigs_cards.keys():
    if len(pigs_cards[key]) == n:
        print(key + 1)
        break
