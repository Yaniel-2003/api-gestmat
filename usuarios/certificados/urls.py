from django.urls import path
from .views import CertificadoMatriculaView

urlpatterns = [
    path('matricula/<int:id>/certificado/', CertificadoMatriculaView.as_view(), name='certificado-matricula'),
]