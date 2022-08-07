from django.urls import path
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = 'cv'

urlpatterns = [
    path('', views.home, name='home'),
    path('<int:position_id>/', views.detail, name='detail'),
    path('courses/', views.all_courses, name='all_courses'),
    path('education/', views.education, name='education'),
    path('personal/', views.personal, name='personal'),
    path('equality/', views.equality_act, name='equality_act'),
    ]

urlpatterns += staticfiles_urlpatterns()
