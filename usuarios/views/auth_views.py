from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate

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