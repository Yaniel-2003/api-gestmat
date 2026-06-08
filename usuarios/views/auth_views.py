from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
import secrets
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from ..models import Usuario

from ..serializers import UsuarioLoginSerializer, UsuarioListSerializer


class LoginView(APIView): 
    permission_classes = [AllowAny]

    def post(self, request):
        # 1. Validamos los datos de entrada automáticamente
        serializer = UsuarioLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        # 2. Verificamos credenciales
        usuario = authenticate(username=username, password=password)

        if usuario is None:
            return Response(
                {'error': 'Usuario o contraseña incorrectos'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 3. Verificamos que el usuario esté activo
        if not usuario.is_active:
            return Response(
                {'error': 'Usuario inactivo'},
                status=status.HTTP_403_FORBIDDEN
            )

        # 4. Generamos los tokens
        refresh = RefreshToken.for_user(usuario)

        # 5. Retornamos tokens y datos
        return Response({
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'usuario': UsuarioListSerializer(usuario).data
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # 1. Obtenemos el token de la petición
            refresh_token = request.data.get('refresh')
            
            if not refresh_token:
                return Response(
                    {'error': 'Se requiere el token de refresh para cerrar sesión'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 2. Invalidamos el token (Blacklist)
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {'mensaje': 'Sesión cerrada correctamente'},
                status=status.HTTP_200_OK
            )
            
        except TokenError:
            # Capturamos específicamente errores de SimpleJWT (ej. token ya expirado o inválido)
            return Response(
                {'error': 'El token es inválido o ya ha expirado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'El correo electrónico es requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        # Buscamos el usuario por su correo
        usuario = Usuario.objects.filter(email=email).first()         
        if not usuario:
            return Response({'mensaje': 'Si el correo electrónico existe, se ha enviado un enlace de recuperación.'}, status=status.HTTP_200_OK)
        
        # Generamos un token único
        token = secrets.token_urlsafe(32)
        usuario.token_reset = token
        usuario.fecha_solicitud = timezone.now().date()
        usuario.token_bloqueado = False
        usuario.save(update_fields=['token_reset', 'fecha_solicitud', 'token_bloqueado'])
        # Enlace para el front
        reset_url = f"http://localhost:5173/recuperar-contrasena?token={token}&email={email}"

        # Cuerpo del correo electrónico 
        asunto = "Recuperación de contraseña - GestMat"
        mensaje = (
            f"Hola {usuario.get_full_name() or usuario.username},\n\n"
            f"Has solicitado restablecer tu contraseña en GestMat. Para continuar, haz clic en el siguiente enlace:\n"
            f"{reset_url}\n\n"
            f"Este enlace solo es válido durante el día de hoy.\n"
            f"Si no realizaste esta solicitud, por favor ignora este correo.\n\n"
            f"Atentamente,\nEl equipo de GestMat."
        )
        try:
            send_mail(
                asunto,
                mensaje,
                'yanielfer2018@gmail.com',
                [email],
                fail_silently=False
            )
        except Exception as e:
            return Response({'error': f'No se pudo enviar el correo: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'mensaje': 'Si el correo electrónico existe, se ha enviado un enlace de recuperación.'}, status=status.HTTP_200_OK)
    

class ConfirmPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not email or not token or not new_password:
            return Response({'error': 'Todos los campos (email, token, new_password) son requeridos.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscamos al usuario que coincida con el email, token y que no esté bloqueado
        usuario = Usuario.objects.filter(email=email, token_reset=token, token_bloqueado=False).first()

        if not usuario:
            return Response({'error': 'El enlace de recuperación es inválido o ya ha sido utilizado.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validamos que el token sea del día de hoy
        if usuario.fecha_solicitud != timezone.now().date():
            # Expiró, bloqueamos el token por seguridad
            usuario.token_bloqueado = True
            usuario.save(update_fields=['token_bloqueado'])
            return Response({'error': 'El enlace de recuperación ha expirado.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validamos la nueva contraseña con las reglas definidas en settings.py
        try:
            validate_password(new_password, user=usuario)
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)
        
        # Cambiamos la contraseña y bloqueamos/limpiamos el token
        usuario.set_password(new_password)
        usuario.token_reset = None
        usuario.token_bloqueado = True
        usuario.save(update_fields=['password', 'token_reset', 'token_bloqueado'])
        
        return Response({'mensaje': 'Tu contraseña ha sido restablecida correctamente.'}, status=status.HTTP_200_OK)