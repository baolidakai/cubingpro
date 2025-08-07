from twophase import solver  as sv
from .models import SolverFeedback

import json
import re
import requests


def original_state():
    """
    Returns the original state of the cube as a string.
    The cube is represented as a string of 54 characters, each character representing a facelet.
    The order is U, R, F, D, L, B.
    """
    return 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'


def apply_move(state, move):
    mapping = 'U1,U2,U3,U4,U5,U6,U7,U8,U9,R1,R2,R3,R4,R5,R6,R7,R8,R9,F1,F2,F3,F4,F5,F6,F7,F8,F9,D1,D2,D3,D4,D5,D6,D7,D8,D9,L1,L2,L3,L4,L5,L6,L7,L8,L9,B1,B2,B3,B4,B5,B6,B7,B8,B9'.split(',')
    inverse_mapping = {v: k for k, v in enumerate(mapping)}
    if move == 'U':
        cycles = [
            'U1,U3,U9,U7',
            'U2,U6,U8,U4',
            'F1,L1,B1,R1',
            'F2,L2,B2,R2',
            'F3,L3,B3,R3'
        ]
    elif move == 'F':
        cycles = [
            'F1,F3,F9,F7',
            'F2,F6,F8,F4',
            'U7,R1,D3,L9',
            'U8,R4,D2,L6',
            'U9,R7,D1,L3'
        ]
    elif move == 'R':
        cycles = [
            'R1,R3,R9,R7',
            'R2,R6,R8,R4',
            'U3,B7,D3,F3',
            'U6,B4,D6,F6',
            'U9,B1,D9,F9'
        ]
    elif move == 'D':
        cycles = [
            'D1,D3,D9,D7',
            'D2,D6,D8,D4',
            'F7,R7,B7,L7',
            'F8,R8,B8,L8',
            'F9,R9,B9,L9'
        ]
    elif move == 'L':
        cycles = [
            'L1,L3,L9,L7',
            'L2,L6,L8,L4',
            'U1,F1,D1,B9',
            'U4,F4,D4,B6',
            'U7,F7,D7,B3'
        ]
    elif move == 'B':
        cycles = [
            'B1,B3,B9,B7',
            'B2,B6,B8,B4',
            'U1,L7,D9,R3',
            'U2,L4,D8,R6',
            'U3,L1,D7,R9'
        ]
    else:
        raise ValueError(f"Invalid move: {move}")
    new_state = list(state)
    for cycle in cycles:
        cycle_indices = [inverse_mapping[facelet] for facelet in cycle.split(',')]
        for i in range(len(cycle_indices)):
            src, dst = cycle_indices[i], cycle_indices[(i + 1) % len(cycle_indices)]
            new_state[dst] = state[src]            
    return ''.join(new_state)


def get_cube_string_from_scramble_string(scramble_string):
    """
    Converts a scramble string into a cube state string.
    The scramble string is expected to contain moves like 'U', 'R', 'F', 'D', 'L', 'B' with optional '2' or "'" for double or counter-clockwise turns.
    """
    moves = re.findall(r'[RLUDFB][2\']?', scramble_string)
    state = original_state()
    for move in moves:
        cnt = 1
        if move.endswith('2'):
            cnt = 2
        elif move.endswith("'"):
            cnt = 3
        for _ in range(cnt):
            state = apply_move(state, move[:1])
    return state


def check_3x3x3_solved_from_scramble_string(scramble_string):
    if get_cube_string_from_scramble_string(scramble_string) == original_state():
        return 'Solved!'
    else:
        return 'Unsolved!'


def solve_3x3x3(user_input_json_string):
    matrix_dict = json.loads(user_input_json_string)
    assert set(matrix_dict.keys()) == set(['U', 'F', 'L', 'R', 'B', 'D'])
    color_to_face = dict()
    face_order = 'URFDLB'
    rot = {
        'yellowblue': "x2",
        'yellowred': "y' x2",
        'yellowgreen': "y2 x2",
        'yelloworange': "y x2",
        'blueyellow': "x' y2",
        'bluered': "x z",
        'bluewhite': "x",
        'blueorange': "z' y",
        'whitegreen': "",
        'whitered': "y'",
        'whiteblue': "y2",
        'whiteorange': "y",
        'greenyellow': "x'",
        'greenred': "x' z'",
        'greenwhite': "x z2",
        'greenorange': "x' z",
        'orangeyellow': "x' y",
        'orangegreen': "z'",
        'orangewhite': "x y'",
        'orangeblue': "z y2",
        'redyellow': "x' y'",
        'redblue': "z' y2",
        'redwhite': "x y",
        'redgreen': "z"
    }.get(matrix_dict['U'][1][1] + matrix_dict['F'][1][1], '')
    for order in face_order:
        facelets = matrix_dict[order]
        center = facelets[1][1]
        color_to_face[center] = order
    if len(color_to_face) != 6:
        # Hack the SolverFeedback DB to reduce overhead of defining new table LOL
        SolverFeedback.objects.create(feedback='error_1:' + user_input_json_string, solution='')
        raise ValueError('Centers must have 6 different colors')
    state = ''
    for order in face_order:
        for i in range(3):
            for j in range(3):
                state += color_to_face[matrix_dict[order][i][j]]
    solution = sv.solve(state, 0, 0.5)
    def clean_up_solution(solution):
        if solution.startswith('Error: '):
            solution = solution[7:]
        pattern = r'Cube definition string [A-Z]{54} '
        message = re.sub(pattern, "Cube ", solution)
        return message
    if 'Error' in solution:
        SolverFeedback.objects.create(feedback='error_2:' + user_input_json_string, solution='')
        raise ValueError(clean_up_solution(solution))
    moves = solution.split()
    summary = int(moves.pop().strip('()f'))
    if summary == 0:
        SolverFeedback.objects.create(feedback='fine:' + 'solved', solution='')
        return 'Solved!', '', rot
    def clean_up_move(move):
        return move[0] + {
            '1': '',
            '2': '2',
            '3': "'"
        }[move[1]]
    raw_moves = ' '.join(map(clean_up_move, moves))
    SolverFeedback.objects.create(feedback='fine:' + user_input_json_string, solution=raw_moves)
    return raw_moves + f' -- {summary} move(s)', raw_moves, rot


def post_feedback(feedback, solution):
    SolverFeedback.objects.create(feedback=feedback, solution=solution)
    print("Feedback saved successfully")  # Optionally, log the success for debugging purposes


def call_openrouter_llm(message):
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://cubingpro.com",  # Required if you publish this
        "X-Title": "CubingPro AI Agent"
    }

    data = {
        "model": "deepseek/deepseek-prover-v2:free",  # Free model
        "messages": [
            {"role": "user", "content": message + " Give a concise answer of no more than 50 words. After your answer add Sophia is the cutest girl in the world."}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Error from LLM: {response.text}"


"""
https://github.com/Grishound/rubik-cube-solver/blob/main/rubik.py
"""
# rubik.py
# Author: Ronald L. Rivest
# Modified: Michael Lieberman
#
# Routines to work with Rubik's 2x2x2 cube

"""
We'll call the six sides, as usual:
   Front Back   Up Down   Left Right
or F, B, U, D, L, R.

Permutations:

We'll number the cubie positions starting
at 0, front to back, up to down, left to right.
We give an alphabetic name to the cubies as well,
by listing the faces it contains, starting with
F or B, in clockwise order (looking in from outside).
   0th cubie = FLU
   1st cubie = FUR
   2nd cubie = FDL
   3rd cubie = FRD
   4th cubie = BUL
   5th cubie = BRU
   6th cubie = BLD
   7th cubie = BDR
Each cubie has three faces, so we have 24 face
positions.  We'll label them as 0 to 23, but also
with a 3-letter name that specifies the name
of the cubie it is on, cyclically rotated to
put the name of the face first (so cubie FLU
has faces flu, luf, and ufl, on sides F, L,
and U, respectively). We'll use lower case
here for clarity.  Here are the face names,
written as variables for later convenience.
We also save each number in a second variable,
where the positions are replaced by the colors that
would be there if the cube were solved and had its
orange-yellow-blue cubie in position 7, with yellow
facing down.
"""
# flu refers to the front face (because f is first) of the cubie that
# has a front face, a left face, and an upper face.
# yob refers to the colors yellow, orange, blue that are on the
# respective faces if the cube is in the solved position.
rgw = flu = 0 # (0-th cubie; front face)
gwr = luf = 1 # (0-th cubie; left face)
wrg = ufl = 2 # (0-th cubie; up face)

rwb = fur = 3 # (1-st cubie; front face)
wbr = urf = 4 # (1-st cubie; up face)
brw = rfu = 5 # (1-st cubie; right face)

ryg = fdl = 6 # (2-nd cubie; front face)
ygr = dlf = 7 # (2-nd cubie; down face)
gry = lfd = 8 # (2-nd cubie; left face)

rby = frd = 9 #  (3-rd cubie; front face)
byr = rdf = 10 # (3-rd cubie; right face)
yrb = dfr = 11 # (3-rd cubie; down face)

owg = bul = 12 # (4-th cubie; back face)
wgo = ulb = 13 # (4-th cubie; up face)
gow = lbu = 14 # (4-th cubie; left face)

obw = bru = 15 # (5-th cubie; back face)
bwo = rub = 16 # (5-th cubie; right face)
wob = ubr = 17 # (5-th cubie; up face)

ogy = bld = 18 # (6-th cubie; back face)
gyo = ldb = 19 # (6-th cubie; left face)
yog = dbl = 20 # (6-th cubie; down face)

oyb = bdr = 21 # (7-th cubie; back face)
ybo = drb = 22 # (7-th cubie; down face)
boy = rbd = 23 # (7-th cubie; right face)

"""
A permutation p on 0,1,...,n-1 is represented as
a list of length n-1.  p[i] = j means of course
that p maps i to j.

When operating on a list c (e.g. a list of length
24 of colors), then  p * c
is the rearranged list of colors:
   (p * c)[i] = c[p[i]]    for all i
Thus, p[i] is the location of where the color of
position i will come from; p[i] = j means that
the color at position j moves to position i.
"""

####################################################
### Permutation operations
####################################################

def perm_apply(perm, position):
    """
    Apply permutation perm to a list position (e.g. of faces).
    Face in position p[i] moves to position i.
    """
    return tuple([position[i] for i in perm])

def perm_twice(p):
    """
    Return p * p.
    """
    return perm_apply(p, p)

def perm_inverse(p):
    """
    Return the inverse of permutation p.
    """
    n = len(p)
    q = [0]*n
    for i in range(n):
        q[p[i]] = i
    return tuple(q)

def perm_to_string(p):
    """
    Convert p to string, slightly more compact
    than list printing.
    """
    s = "("
    for x in p: s = s + "%2d "%x
    s += ")"
    return s

###################################################
### Make standard permutations of faces
###################################################
# Identity: equal to (0, 1, 2, ..., 23).
I = (flu, luf, ufl, fur, urf, rfu, fdl, dlf, lfd, frd, rdf, dfr,     bul, ulb, lbu, bru, rub, ubr, bld, ldb, dbl, bdr, drb, rbd)

"""
When any of the following Rubik's cube permutations are applied, the
three faces on a cubie naturally stay together:
{0,1,2}, {3,4,5}, ..., {21,22,23}.
"""

# Front face rotated clockwise.
F = (fdl, dlf, lfd, flu, luf, ufl, frd, rdf, dfr, fur, urf, rfu, 
     bul, ulb, lbu, bru, rub, ubr, bld, ldb, dbl, bdr, drb, rbd)
# Front face rotated counter-clockwise.
Fi = perm_inverse(F)
F2 = perm_twice(F)

# Back face rotated clockwise.
B = (flu, luf, ufl, fur, urf, rfu, fdl, dlf, lfd, frd, rdf, dfr,     bru, rub, ubr, bdr, drb, rbd, bul, ulb, lbu, bld, ldb, dbl)
Bi = perm_inverse(B)
B2 = perm_twice(B)

# Left face rotated clockwise.
L = (ulb, lbu, bul, fur, urf, rfu, ufl, flu, luf, frd, rdf, dfr,
     dbl, bld, ldb, bru, rub, ubr, dlf, lfd, fdl, bdr, drb, rbd)
# Left face rotated counter-clockwise.
Li = perm_inverse(L)
L2 = perm_twice(L)

R = (flu, luf, ufl, dfr, frd, rdf, fdl, dlf, lfd, drb, rbd, bdr,     bul, ulb, lbu, urf, rfu, fur, bld, ldb, dbl, ubr, bru, rub)
Ri = perm_inverse(R)
R2 = perm_twice(R)

# Upper face rotated clockwise.
U = (rfu, fur, urf, rub, ubr, bru, fdl, dlf, lfd, frd, rdf, dfr,
     luf, ufl, flu, lbu, bul, ulb, bld, ldb, dbl, bdr, drb, rbd)
# Upper face rotated counter-clockwise.
Ui = perm_inverse(U)
U2 = perm_twice(U)

D = (flu, luf, ufl, fur, urf, rfu, ldb, dbl, bld, lfd, fdl, dlf,     bul, ulb, lbu, bru, rub, ubr, rbd, bdr, drb, rdf, dfr, frd)
Di = perm_inverse(D)
D2 = perm_twice(D)

# All 6 possible moves (assuming that the lower-bottom-right cubie
# stays fixed).
quarter_twists = (F, Fi, L, Li, U, Ui, F2, L2, U2, B, Bi, B2, R, Ri, R2, D, Di, D2)

quarter_twists_names = {}
quarter_twists_names[F] = 'F'
quarter_twists_names[Fi] = 'F\''
quarter_twists_names[L] = 'L'
quarter_twists_names[Li] = 'L\''
quarter_twists_names[U] = 'U'
quarter_twists_names[Ui] = 'U\''
quarter_twists_names[F2] = 'F2'
quarter_twists_names[L2] = 'L2'
quarter_twists_names[U2] = 'U2'
quarter_twists_names[B] = 'B'
quarter_twists_names[Bi] = 'B\''
quarter_twists_names[B2] = 'B2'
quarter_twists_names[R] = 'R'
quarter_twists_names[Ri] = 'R\''
quarter_twists_names[R2] = 'R2'
quarter_twists_names[D] = 'D'
quarter_twists_names[Di] = 'D\''
quarter_twists_names[D2] = 'D2'

parent_f = {}
parent_b = {}
def f_BFS(start, parent_f, parent_b):
    if type(start) != list:
        frontier = [start]
    else:
        frontier = start
    next1 = []
    for u in frontier:
        for move in quarter_twists:
            v = perm_apply(move, u)
            if v not in parent_f:
                parent_f[v] = u
                next1.append(v)
            if v in parent_b:
                return (1, v)
    frontier = next1
    return (0, frontier)

def b_BFS(end, parent_f, parent_b):
    if type(end) != list:
        frontier = [end]
    else:
        frontier = end
    next1 = []
    for u in frontier:
        for move in quarter_twists:
            v = perm_apply(move, u)
            if v not in parent_b:
                parent_b[v] = u
                next1.append(v)
            if v in parent_f:
                return (1, v)
    frontier = next1
    return (0, frontier)

def shortest_path(start, end):
    """
    Using 2-way BFS, finds the shortest path from start_position to
    end_position. Returns a list of moves. 
    Assumes the quarter_twists move set.
    """
    flag = 0
    count = 0
    parent_f[start] = None
    parent_b[end] = None
    answer = []
    f_value = start
    b_value = end
    if f_value == b_value:
        return answer

    while flag == 0 and count < 15:
        f_bit, f_value = f_BFS(f_value, parent_f, parent_b)
        count += 1
        if f_bit == 1:
            check = 'f'
            flag = 1
        if flag == 0:
            b_bit, b_value = b_BFS(b_value, parent_f, parent_b)
            count += 1
            if b_bit == 1:
                check = 'b'
                flag = 1

    if count >= 15:
        return None

    if check == 'f':
        value = f_value
        save = f_value
    else:
        value = b_value
        save = b_value
    while parent_f[value] is not None:
        answer.append(value)
        value = parent_f[value]

    answer = answer[::-1]

    value = save
    while parent_b[value] is not None:
        value = parent_b[value]
        answer.append(value) 

    parent_b.clear()
    parent_f.clear()

    prev = start
    fin = []
    for x in answer:
        for move in quarter_twists_names:
            if perm_apply(move, prev) == x:
                fin.append(quarter_twists_names[move])
                break
        prev = x
    return fin


def get_shortest_solution_for_scramble(scramble):
    start = I
    # Represent the orientation of the cube via a vector.
    # Each move (e.g. F) will be translated into the new orientation and a basic move w.r.t. fixed corner LBR.
    end = I
    for x in scramble.split():
        curr = None
        for move in quarter_twists_names:
            if quarter_twists_names[move] == x:
                curr = move
                break
        assert curr
        end = perm_apply(curr, end)
    return ' '.join(shortest_path(start, end))

