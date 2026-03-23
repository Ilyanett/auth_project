from django.http import JsonResponse
from django.views import View
from .permissions import has_permission
import json
from .models import AccessRule, UserRole
from users.models import User

MOCK_ORDERS = [
    {'id': 1, 'product': 'Ноутбук', 'amount': 50000, 'owner_id': 2},
    {'id': 2, 'product': 'Телефон', 'amount': 30000, 'owner_id': 1},
    {'id': 3, 'product': 'Планшет', 'amount': 20000, 'owner_id': 3},
]

MOCK_PRODUCTS = [
    {'id': 1, 'name': 'Ноутбук', 'price': 50000},
    {'id': 2, 'name': 'Телефон', 'price': 30000},
    {'id': 3, 'name': 'Планшет', 'price': 20000},
]


class OrdersView(View):

    def get(self, request):

        if not request.user_obj:
            return JsonResponse({'error': 'Необходима авторизация'}, status=401)

        user = request.user_obj

        can_read_all = has_permission(user, 'orders', 'read_all_permission')
        can_read = has_permission(user, 'orders', 'read_permission')

        if not can_read and not can_read_all:
            return JsonResponse({'error': 'Нет доступа'}, status=403)

        if can_read_all:

            return JsonResponse({'orders': MOCK_ORDERS})
        else:

            my_orders = [o for o in MOCK_ORDERS if o['owner_id'] == user.id]
            return JsonResponse({'orders': my_orders})

    def post(self, request):
        if not request.user_obj:
            return JsonResponse({'error': 'Необходима авторизация'}, status=401)

        if not has_permission(request.user_obj, 'orders', 'create_permission'):
            return JsonResponse({'error': 'Нет доступа'}, status=403)

        return JsonResponse({'message': 'Заказ создан (Mock)'}, status=201)


class ProductsView(View):

    def get(self, request):
        if not request.user_obj:
            return JsonResponse({'error': 'Необходима авторизация'}, status=401)

        can_read = has_permission(request.user_obj, 'products', 'read_permission')
        can_read_all = has_permission(request.user_obj, 'products', 'read_all_permission')

        if not can_read and not can_read_all:
            return JsonResponse({'error': 'Нет доступа'}, status=403)

        return JsonResponse({'products': MOCK_PRODUCTS})

    def post(self, request):
        if not request.user_obj:
            return JsonResponse({'error': 'Необходима авторизация'}, status=401)

        if not has_permission(request.user_obj, 'products', 'create_permission'):
            return JsonResponse({'error': 'Нет доступа'}, status=403)

        return JsonResponse({'message': 'Продукт создан (Mock)'}, status=201)


class AdminAccessRulesView(View):

    def _is_admin(self, user):

        if not user:
            return False
        return UserRole.objects.filter(user=user, role__name='admin').exists()

    def get(self, request):

        if not request.user_obj:
            return JsonResponse({'error': 'Необходима авторизация'}, status=401)

        if not self._is_admin(request.user_obj):
            return JsonResponse({'error': 'Только для администратора'}, status=403)

        rules = AccessRule.objects.select_related('role', 'element').all()
        data = []
        for rule in rules:
            data.append({
                'id': rule.id,
                'role': rule.role.name,
                'element': rule.element.name,
                'read_permission': rule.read_permission,
                'read_all_permission': rule.read_all_permission,
                'create_permission': rule.create_permission,
                'update_permission': rule.update_permission,
                'update_all_permission': rule.update_all_permission,
                'delete_permission': rule.delete_permission,
                'delete_all_permission': rule.delete_all_permission,
            })

        return JsonResponse({'rules': data})

    def patch(self, request):

        if not request.user_obj:
            return JsonResponse({'error': 'Необходима авторизация'}, status=401)

        if not self._is_admin(request.user_obj):
            return JsonResponse({'error': 'Только для администратора'}, status=403)

        data = json.loads(request.body)
        rule_id = data.get('rule_id')

        try:
            rule = AccessRule.objects.get(id=rule_id)
        except AccessRule.DoesNotExist:
            return JsonResponse({'error': 'Правило не найдено'}, status=404)

        permissions = [
            'read_permission', 'read_all_permission', 'create_permission',
            'update_permission', 'update_all_permission',
            'delete_permission', 'delete_all_permission',
        ]
        for perm in permissions:
            if perm in data:
                setattr(rule, perm, data[perm])

        rule.save()
        return JsonResponse({'message': 'Правило обновлено'})


class AdminUsersView(View):

    def get(self, request):
        if not request.user_obj:
            return JsonResponse({'error': 'Необходима авторизация'}, status=401)

        if not UserRole.objects.filter(user=request.user_obj, role__name='admin').exists():
            return JsonResponse({'error': 'Только для администратора'}, status=403)

        users = User.objects.all().values('id', 'email', 'first_name', 'last_name', 'is_active')
        return JsonResponse({'users': list(users)})
