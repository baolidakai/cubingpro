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
    path("2x2x2/eg_intro/", hello.views.eg_intro, name="eg_intro"),
    path("2x2x2/eg_alg/", hello.views.eg_alg, name="eg_alg"),
    path("clock/7simul_flip_intro", hello.views.clock_7simul_flip_intro, name="7simul_flip_intro"),
    path("clock/7simul_flip_improved", hello.views.clock_7simul_flip_improved, name="7simul_flip_improved"),
    path("clock/7simul_flip_theory", hello.views.clock_7simul_flip_theory, name="7simul_flip_theory"),
    path("clock/7simul_flip_tool", hello.views.clock_7simul_flip_tool, name="7simul_flip_tool"),
    path("pyraminx/corner_first_intro", hello.views.pyraminx_corner_first_intro, name="corner_first_intro"),
    path("pyraminx/corner_first_alg", hello.views.pyraminx_corner_first_alg, name="corner_first_alg"),
    path("pyraminx/v_first_alg", hello.views.pyraminx_v_first_alg, name="v_first_alg"),
    path("skewb/sarah_beginner", hello.views.skewb_sarah_beginner, name="sarah_beginner"),
    path("skewb/sarah_intermediate", hello.views.skewb_sarah_intermediate, name="sarah_intermediate"),
]

