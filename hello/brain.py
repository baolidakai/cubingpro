from twophase import solver  as sv
from .models import SolverFeedback

import json
import re


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