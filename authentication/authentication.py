import jwt
import requests
from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth.models import User  # Importa el modelo User de Django

# URL de la API externa para verificar el token (si existe un endpoint)
# o la URL base para obtener la clave pública (si es necesario)
EXTERNAL_AUTH_VERIFY_URL = "https://mantenimiento.miteleferico.bo/api/v1/auth/verify-token/"  # REEMPLAZA CON LA URL REAL SI EXISTE

# Clave pública de la API externa (si utiliza firma asimétrica)
# Si utiliza firma simétrica, necesitarás la clave secreta.
EXTERNAL_PUBLIC_KEY = None  # REEMPLAZA CON LA CLAVE PÚBLICA SI APLICA

class ExternalJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')

        if not auth_header:
            return None  # No hay encabezado de autorización

        try:
            scheme, token = auth_header.split()
        except ValueError:
            raise exceptions.AuthenticationFailed('Encabezado de autorización mal formado')

        if scheme.lower() != 'bearer':
            raise exceptions.AuthenticationFailed('Esquema de autorización incorrecto. Debe ser Bearer.')

        return self.authenticate_credentials(request, token)

    def authenticate_credentials(self, request, token):
        try:
            # Opción 1: Verificar el token localmente (si tienes la clave pública)
            if EXTERNAL_PUBLIC_KEY:
                payload = jwt.decode(token, EXTERNAL_PUBLIC_KEY, algorithms=['RS256']) # Ajusta el algoritmo
                user_id = payload.get('user_id') # Ajusta la clave del ID de usuario
                username = payload.get('username') # Ajusta la clave del nombre de usuario
                # ... extraer otra información relevante del payload

                if not user_id or not username:
                    raise exceptions.AuthenticationFailed('Payload del token inválido')

                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    # Podrías crear un usuario local si lo necesitas
                    user = User.objects.create_user(username=username)
                return (user, token) # Retorna el usuario y el token

            # Opción 2: Enviar el token a un endpoint de verificación en la API externa
            elif EXTERNAL_AUTH_VERIFY_URL:
                headers = {'Authorization': f'Bearer {token}'}
                response = requests.get(EXTERNAL_AUTH_VERIFY_URL, headers=headers)
                response.raise_for_status()  # Lanza excepción si hay error HTTP

                verification_data = response.json()
                is_valid = verification_data.get('is_valid') # Ajusta la clave según la respuesta
                user_id = verification_data.get('user_id') # Ajusta la clave
                username = verification_data.get('username') # Ajusta la clave

                if is_valid:
                    if not user_id or not username:
                        raise exceptions.AuthenticationFailed('Datos de verificación inválidos')

                    try:
                        user = User.objects.get(username=username)
                    except User.DoesNotExist:
                        user = User.objects.create_user(username=username)
                    return (user, token)
                else:
                    raise exceptions.AuthenticationFailed('Token inválido según la API externa')

            else:
                raise exceptions.AuthenticationFailed('No se configuró la clave pública ni la URL de verificación externa')

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expirado')
        except jwt.InvalidSignatureError:
            raise exceptions.AuthenticationFailed('Firma del token inválida')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Error al decodificar el token')
        except requests.exceptions.RequestException as e:
            raise exceptions.AuthenticationFailed(f'Error al contactar la API externa: {e}')
        except (KeyError, ValueError, TypeError):
            raise exceptions.AuthenticationFailed('Respuesta de la API externa inesperada o error al procesar el token')