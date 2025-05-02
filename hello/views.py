from django.shortcuts import render, redirect, get_object_or_404

import markdown

from .models import Greeting, Page
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import csv
import os
import json

from .brain import *

# Create your views here.


def index(request):
    return render(request, "index.html")


def eg_intro(request):
    return render(request, "eg_intro.html")


import re


def preprocess(alg):
    pattern = r"[RLUDFB][2']?"
    moves = re.findall(pattern, alg)
    if moves and (moves[0].startswith('B') or moves[-1].startswith('B')):
        moves.append('z2')
    return ' '.join(moves)


def pyraminx_inverse(alg):
    pattern = r"[RLUDFB][2']?"
    moves = re.findall(pattern, alg)
    moves.reverse()
    def inv(m):
        if m.endswith('2'):
            return m[:-1]
        if m.endswith("'"):
            return m[:-1]
        return m + "'"
    return ' '.join([inv(m) for m in moves])


def read_csv_data(filepath, delimiter):
    data = []
    csv_path = os.path.join(settings.BASE_DIR, filepath)

    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        for row in reader:
            # Example: convert values and calculate something if needed
            for method in ['CLL', 'EG1', 'EG2']:
                row[f'{method}_viz'] = preprocess(row.get(f'{method}_alg', ''))
            data.append(row)

    return data


def comp_visualization(request):
    return render(request, "comp_visualization.html")


def u2r2(request):
    return render(request, "u2r2.html")


def eg_alg(request):
    table_data = read_csv_data('hello/algorithms/eg.csv', ',')
    return render(request, "eg_alg.html", {'table_data': table_data})


def clock_7simul_flip_intro(request):
    table_data = read_csv_data('hello/tutorials/7sf.csv', ';')
    return render(request, "7simul_flip_intro.html", {'table_data': json.dumps(table_data)})


def clock_7simul_flip_improved(request):
    table_data = read_csv_data('hello/tutorials/7sf_improved.csv', ';')
    return render(request, "7simul_flip_improved.html", {'table_data': json.dumps(table_data)})


def clock_7simul_flip_theory(request):
    return render(request, "7simul_flip_theory.html", {})


def clock_7simul_flip_tool(request):
    return render(request, "7simul_flip_tool.html", {})


def pyraminx_corner_first_intro(request):
    # TODO: Make this a CSV.
    return render(request, "corner_first_intro.html", {})


def read_pyraminx_csv_data(filepath, delimiter):
    data = []
    csv_path = os.path.join(settings.BASE_DIR, filepath)

    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        for row in reader:
            if 'alg' in row:
                row['inv'] = pyraminx_inverse(row['alg'])
            data.append(row)

    return data


def pyraminx_corner_first_alg(request):
    table_data = read_pyraminx_csv_data('hello/algorithms/pyraminx_corner_first.csv', '|')
    return render(request, "corner_first_alg.html", {'table_data': json.dumps(table_data)})


def pyraminx_v_first_alg(request):
    table_data = read_pyraminx_csv_data('hello/algorithms/pyraminx_v_first.csv', ',')
    return render(request, "v_first_alg.html", {'table_data': table_data})


def skewb_sarah_beginner(request):
    table_data = read_csv_data('hello/algorithms/skewb_sarah_beginner.csv', ',')
    return render(request, "sarah_beginner.html", {'table_data': table_data})


def skewb_sarah_intermediate(request):
    table_data = read_csv_data('hello/algorithms/skewb_sarah_intermediate.csv', ',')
    return render(request, "sarah_intermediate.html", {'table_data': table_data})


def dr(request):
    return render(request, "dr.html")


def tutorial_editor(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        author = request.POST.get('author')
        Page.objects.create(title=title, content=content, author=author)
        return redirect('tutorial_viewer')
    return render(request, "tutorial_editor.html")


def tutorial_viewer(request):
    pages = Page.objects.order_by('-created_at')
    return render(request, "tutorial_viewer.html", {'pages': pages})


def view_page(request, page_id):
    page = get_object_or_404(Page, id=page_id)
    html = markdown.markdown(page.content, extensions=['extra', 'nl2br'])
    return render(request, 'view.html', {'page': page, 'html': html})


@csrf_exempt
def api_solver(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            user_input = body.get('matrix_dict', '')
            output, clean_alg, rot = solve_3x3x3(json.dumps(user_input))

            return JsonResponse({
                'output': output,
                'clean_alg': clean_alg,
                'rot': rot
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)


def solver(request):
    output = ''
    user_input = ''
    clean_alg = ''
    rot = ''
    if request.method == 'POST':
        user_input = request.POST.get('matrix_dict', '')
        
        # Run your Python logic here with the input
        try:
            output, clean_alg, rot = solve_3x3x3(user_input)
        except Exception as e:
            output = f"Error: {str(e)}"

    return render(request, 'solver.html', {'output': output, 'matrix_dict': user_input, 'clean_alg': clean_alg, 'rot': rot})


def db(request):
    # If you encounter errors visiting the `/db/` page on the example app, check that:
    #
    # When running the app on Heroku:
    #   1. You have added the Postgres database to your app.
    #   2. You have uncommented the `psycopg` dependency in `requirements.txt`, and the `release`
    #      process entry in `Procfile`, git committed your changes and re-deployed the app.
    #
    # When running the app locally:
    #   1. You have run `./manage.py migrate` to create the `hello_greeting` database table.

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, "db.html", {"greetings": greetings})
