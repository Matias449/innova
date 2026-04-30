from django.contrib.auth.models import User

users_data = [
    {'username': 'superadmin', 'email': 'admin@innova.cl', 'password': 'password123', 'first_name': 'Dev', 'last_name': 'Superadmin', 'is_superuser': True, 'is_staff': True},
    {'username': 'directora', 'email': 'ana@innova.cl', 'password': 'password123', 'first_name': 'Ana', 'last_name': 'Directora', 'is_superuser': False, 'is_staff': True},
    {'username': 'admin', 'email': 'carlos@innova.cl', 'password': 'password123', 'first_name': 'Carlos', 'last_name': 'Administrador', 'is_superuser': False, 'is_staff': True},
    {'username': 'educadora', 'email': 'laura@innova.cl', 'password': 'password123', 'first_name': 'Laura', 'last_name': 'Educadora', 'is_superuser': False, 'is_staff': False},
]

for user_data in users_data:
    if not User.objects.filter(username=user_data['username']).exists():
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )
        user.is_superuser = user_data['is_superuser']
        user.is_staff = user_data['is_staff']
        user.save()
        print(f"Usuario {user.username} creado.")
    else:
        print(f"Usuario {user.username} ya existe.")
