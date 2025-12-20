from django.urls import path
from . import views as v

app_name = 'glosowania'

urlpatterns = (
    # path('status/<int:pk>/', v.status, name='status'),
    # http://127.0.0.1:8000/glosowania/details/89/
    path('details/<int:pk>/', v.details, name='details'),
    path('edit/<int:pk>/', v.edit, name='edit'),
    path('nowy/', v.dodaj, name='dodaj_nowy'),
    path('proposition/', v.proposition, name='proposition'),
    path('discussion/', v.discussion, name='discussion'),
    path('referendum/', v.referendum, name='referendum'),
    path('rejected/', v.rejected, name='rejected'),
    path('approved/', v.approved, name='approved'),
    path('parameters/', v.parameters, name='parameters'),
)
