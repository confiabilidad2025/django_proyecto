import jwt
import requests
from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth.models import User

EXTERNAL_AUTH_VERIFY_URL = "https://mantenimiento.miteleferico.bo/api/v1/auth/sign-in/"
EXTERNAL_PUBLIC_KEY = None

class ExternalJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')

        if not auth_header:
            return None

        try:
            scheme, token = auth_header.split()
        except ValueError:
            raise exceptions.AuthenticationFailed('Encabezado de autorización mal formado')

        if scheme.lower() != 'bearer':
            raise exceptions.AuthenticationFailed('Esquema de autorización incorrecto. Debe ser Bearer.')

        return self.authenticate_credentials(request, token)

    def authenticate_credentials(self, request, token):
        try:
            # Opción 1: Verificar el token localmente
            if EXTERNAL_PUBLIC_KEY:
                payload = jwt.decode(token, EXTERNAL_PUBLIC_KEY, algorithms=['RS256'])
                user_id = payload.get('user_id')
                username = payload.get('username')
                if not user_id or not username:
                    raise exceptions.AuthenticationFailed('Payload del token inválido')
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    raise exceptions.AuthenticationFailed('Usuario no encontrado')
                return (user, token)

            # Opción 2: Intentar autenticar contra la API externa
            elif EXTERNAL_AUTH_VERIFY_URL:
                headers = {'Authorization': f'Bearer {token}'}
                response = requests.post(EXTERNAL_AUTH_VERIFY_URL, headers=headers)
                response.raise_for_status()  # Lanza excepción para códigos de error HTTP

                # Si llegamos aquí, la conexión fue exitosa (código 200)
                verification_data = response.json()
                user_id = verification_data.get('user_id')
                username = verification_data.get('username')

                if not user_id or not username:
                    raise exceptions.AuthenticationFailed('Datos de respuesta de autenticación inválidos')

                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    raise exceptions.AuthenticationFailed('Usuario no encontrado')
                return (user, token)

            else:
                raise exceptions.AuthenticationFailed('No se configuró la clave pública ni la URL de verificación externa')

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expirado')
        except jwt.InvalidSignatureError:
            raise exceptions.AuthenticationFailed('Firma del token inválida')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Error al decodificar el token')
        except requests.exceptions.RequestException as e:
            # Interceptamos el error de conexión y devolvemos un mensaje simplificado
            raise exceptions.AuthenticationFailed('Usuario no encontrado')
        except (KeyError, ValueError, TypeError):
            raise exceptions.AuthenticationFailed('Error al procesar la respuesta de la API')