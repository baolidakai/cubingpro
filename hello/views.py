from django.shortcuts import render, redirect, get_object_or_404

import markdown

from .models import Page, SolverFeedback
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

import csv
import os
import json

from .brain import *
import logging
logger = logging.getLogger(__name__)
logger.info('Here!')

# Create your views here.


def index(request):
    logger.debug("X-Forwarded-Proto: %s", request.META.get('HTTP_X_FORWARDED_PROTO'))
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

def yau(request):
    return render(request, "yau.html")


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
    

@csrf_exempt
def api_solver_feedback(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            feedback = body.get('feedback', '')
            solution = body.get('solution', '')
            if feedback:
                post_feedback(feedback, solution)
            return JsonResponse({'success': True})
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


def privacy(request):
    return render(request, "privacy.html")


def execute_sql(request):
    if request.method == 'POST':
        sql_query = request.POST.get('sql_query', '')

        # Basic validation: Allow only SELECT queries
        if not sql_query.lower().startswith("select"):
            return JsonResponse({'error': 'Only SELECT queries are allowed'}, status=400)

        # Prevent harmful SQL (basic example)
        if re.search(r'(drop|delete|update|insert|alter|truncate)', sql_query, re.IGNORECASE):
            return JsonResponse({'error': 'Unsafe query detected'}, status=400)

        # Prevent unsafe characters like semicolons or comment symbols
        # # is okay LOL
        if re.search(r"[;'\-\/]", sql_query):
            return JsonResponse({'error': 'Unsafe characters detected in query'}, status=400)

        # Safe execution of the query
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_query)  # Execute the query
                result = cursor.fetchall()
                columns = [col[0] for col in cursor.description]  # Get column names
                data = [dict(zip(columns, row)) for row in result]
                return render(request, 'execute_sql.html', {'result': data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return render(request, 'execute_sql.html')