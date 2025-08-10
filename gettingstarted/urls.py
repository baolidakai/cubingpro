"""
URL configuration for gettingstarted project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# from django.contrib import admin
from django.urls import path
import os
from django.views.static import serve
from django.conf import settings
from django.urls import re_path

import hello.views

urlpatterns = [
    path("", hello.views.index, name="index"),
    re_path(r'ads.txt', serve, {
        'path': 'ads.txt',
        'document_root': os.path.join(settings.BASE_DIR, 'hello/static'),
    }),
    re_path(r'twitter.png', serve, {
        'path': 'twitter.png',
        'document_root': os.path.join(settings.BASE_DIR, 'hello/static'),
    }),
    re_path(r'app-ads.txt', serve, {
        'path': 'app-ads.txt',
        'document_root': os.path.join(settings.BASE_DIR, 'hello/static'),
    }),
    path("privacy", hello.views.privacy, name="privacy"),
    path("2x2x2/eg_intro/", hello.views.eg_intro, name="eg_intro"),
    path("2x2x2/eg_alg/", hello.views.eg_alg, name="eg_alg"),
    path("2x2x2/eg_trainer/", hello.views.eg_trainer, name="eg_trainer"),
    path("clock/7simul_flip_intro", hello.views.clock_7simul_flip_intro, name="7simul_flip_intro"),
    path("clock/7simul_flip_improved", hello.views.clock_7simul_flip_improved, name="7simul_flip_improved"),
    path("clock/7simul_flip_theory", hello.views.clock_7simul_flip_theory, name="7simul_flip_theory"),
    path("clock/7simul_flip_tool", hello.views.clock_7simul_flip_tool, name="7simul_flip_tool"),
    path("pyraminx/corner_first_intro", hello.views.pyraminx_corner_first_intro, name="corner_first_intro"),
    path("pyraminx/corner_first_alg", hello.views.pyraminx_corner_first_alg, name="corner_first_alg"),
    path("pyraminx/v_first_alg", hello.views.pyraminx_v_first_alg, name="v_first_alg"),
    path("skewb/sarah_beginner", hello.views.skewb_sarah_beginner, name="sarah_beginner"),
    path("skewb/sarah_intermediate", hello.views.skewb_sarah_intermediate, name="sarah_intermediate"),
    path("skewb/sarah_advanced", hello.views.skewb_sarah_advanced, name="sarah_advanced"),
    path("comp_visualization", hello.views.comp_visualization, name="comp_visualization"),
    path("mini_comp", hello.views.mini_comp, name="mini_comp"),
    path("mini_comp_submit/", hello.views.submit_solution, name="submit_solution"),
    path("mini_comp_results/", hello.views.get_results, name="get_results"),
    path("fmc/dr", hello.views.dr, name="dr"),
    path("3bld/memo", hello.views.memo, name="memo"),
    path("3bld/m2op", hello.views.m2op, name="m2op"),
    path("3bld/orozco", hello.views.orozco, name="orozco"),
    path("4bld/u2r2", hello.views.u2r2, name="u2r2"),
    path("3bld/exec_trainer", hello.views.exec_trainer, name="exec_trainer"),
    path("3bld/exec_trainer/generate_3_cycle_scramble", hello.views.generate_3_cycle_scramble, name="generate_3_cycle_scramble"),
    path("big_cube/yau", hello.views.yau, name="yau"),
    path("solver/", hello.views.solver, name="solver"),
    path("game/geoguesser", hello.views.geoguesser, name="geoguesser"),
    # Use a secret name so that not every one can easily guess.
    path("api_secret_name/solver/", hello.views.api_solver, name="api_solver"),
    path("api_secret_name/solver_feedback/", hello.views.api_solver_feedback, name="api_solver_feedback"),
    path("tutorial_editor/", hello.views.tutorial_editor, name="tutorial_editor"),
    path("tutorial_viewer/", hello.views.tutorial_viewer, name="tutorial_viewer"),
    path('page/<int:page_id>/', hello.views.view_page, name='view_page'),
    path('execute_sql/', hello.views.execute_sql, name='execute_sql'),
    # Fun project
    path('fetch_message/', hello.views.fetch_messages, name='fetch_messages'),
    path('send_message/', hello.views.send_message, name='send_message'),
    path('clear_chat/', hello.views.clear_chat, name='clear_chat'),
    path('send_message_to_llm_agent/', hello.views.send_message_to_llm_agent, name='send_message_to_llm_agent'),
    path('fmc/recon', hello.views.fmc_recon, name='fmc_recon'),
    path('sq1/cube_shape/', hello.views.cube_shape, name='cube_shape'),
    path('sq1/eo/', hello.views.sq1_eo, name='sq1_eo'),
    path('gemini-chat/', hello.views.chat_api, name='chat_api'),
]

