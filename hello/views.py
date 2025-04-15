from django.shortcuts import render

from .models import Greeting
from django.conf import settings

import csv
import os

# Create your views here.


def index(request):
    return render(request, "index.html")


def eg_intro(request):
    return render(request, "eg_intro.html")


import re


def preprocess(alg):
    pattern = r"[RLUDFB][2']?"
    moves = re.findall(pattern, alg)
    return ' '.join(moves)


def read_csv_data():
    data = []
    csv_path = os.path.join(settings.BASE_DIR, 'hello/algorithms', 'eg.csv')

    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Example: convert values and calculate something if needed
            for method in ['CLL', 'EG1', 'EG2']:
                row[f'{method}_viz'] = preprocess(row[f'{method}_alg'])
            data.append(row)

    return data


def eg_alg(request):
    table_data = read_csv_data()
    return render(request, "eg_alg.html", {'table_data': table_data})


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
