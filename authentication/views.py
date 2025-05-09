# authentication/views.py
from django.shortcuts import render, redirect
from django.urls import reverse
import requests
import json
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth.models import User
from .forms import LoginForm  # Importa tu formulario

EXTERNAL_AUTH_URL = "https://mantenimiento.miteleferico.bo/api/v1/auth/sign-in"

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']  # 'username' contiene el email completo
            password = form.cleaned_data['password']
            data = {'email': email, 'password': password}
            headers = {'Content-Type': 'application/json'}

            try:
                response = requests.post(EXTERNAL_AUTH_URL, headers=headers, json=data)
                response.raise_for_status()
                auth_data = response.json()
                token_data = auth_data.get('data', {})
                token = token_data.get('token')
                user_info = token_data.get('user', {})

                if token and user_info:
                    username = user_info.get('username', user_info.get('email'))
                    try:
                        user = User.objects.get(username=username)
                    except User.DoesNotExist:
                        user = User.objects.create_user(username=username, email=user_info.get('email'), password=username)

                    django_login(request, user)
                    request.session['jwt_token'] = token
                    return redirect('/application/dashboard_ots/')
                else:
                    return render(request, 'authentication/login.html', {'form': form, 'error_message': 'Inicio de sesión fallido: no se recibió token o información del usuario.'})

            except requests.exceptions.RequestException as e:
                # Aquí modificamos el mensaje de error para el usuario
                return render(request, 'authentication/login.html', {'form': form, 'error_message': 'Usuario o contraseña incorrectos'})
            except ValueError:
                return render(request, 'authentication/login.html', {'form': form, 'error_message': 'Respuesta inválida de la API externa.'})
        else:
            return render(request, 'authentication/login.html', {'form': form, 'error_message': 'Por favor, corrige los errores del formulario.'})
    else:
        form = LoginForm()
        return render(request, 'authentication/login.html', {'form': form})