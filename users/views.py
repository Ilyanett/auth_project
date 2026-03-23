import json
from django.http import JsonResponse
from django.views import View
from .models import User
from .utils import generate_token
from .models import BlacklistedToken


class RegisterView(View):

    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        password_confirm = data.get('password_confirm')

        if not email or not password or not password_confirm:
            return JsonResponse(
                {'error': 'Email, пароль и подтверждение пароля обязательны'},
                status=400
            )

        if password != password_confirm:
            return JsonResponse(
                {'error': 'Пароли не совпадают'},
                status=400
            )

        if User.objects.filter(email=email).exists():
            return JsonResponse(
                {'error': 'Пользователь с таким email уже существует'},
                status=400
            )

        user = User(
            email=email,
            first_name=data.get('first_name', ''),
            middle_name=data.get('middle_name', ''),
            last_name=data.get('last_name', ''),
        )
        user.set_password(password)
        user.save()

        return JsonResponse(
            {'message': 'Пользователь создан', 'id': user.id},
            status=201
        )


class LoginView(View):

    def post(self, request):
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:

            return JsonResponse(
                {'error': 'Неверный email или пароль'},
                status=401
            )

        if not user.check_password(password):
            return JsonResponse(
                {'error': 'Неверный email или пароль'},
                status=401
            )

        token = generate_token(user.id)
        return JsonResponse({'token': token})


class ProfileView(View):

    def get(self, request):

        if not request.user_obj:
            return JsonResponse({'error': 'Необходима авторизация'}, status=401)

        user = request.user_obj
        return JsonResponse({
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'created_at': user.created_at.isoformat(),
        })

    def patch(self, request):

        if not request.user_obj:
            return JsonResponse({'error': 'Необходима авторизация'}, status=401)

        data = json.loads(request.body)
        user = request.user_obj

        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']

        user.save()
        return JsonResponse({'message': 'Профиль обновлён'})


class DeleteAccountView(View):

    def delete(self, request):
        if not request.user_obj:
            return JsonResponse({'error': 'Необходима авторизация'}, status=401)

        user = request.user_obj
        user.is_active = False
        user.save()

        return JsonResponse({'message': 'Аккаунт удалён'})


class LogoutView(View):

    def post(self, request):
        if not request.user_obj:
            return JsonResponse({'error': 'Необходима авторизация'}, status=401)

        token = request.current_token
        BlacklistedToken.objects.get_or_create(token=token)

        return JsonResponse({'message': 'Вы вышли из системы'})
