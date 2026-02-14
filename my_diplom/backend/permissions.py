from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение, предоставляющее полный доступ владельцу объекта
    и только чтение для всех остальных пользователей.

    Наследуется от `permissions.BasePermission` и предназначено для
    использования в Django REST Framework.

    Для небезопасных методов (POST, PUT, PATCH, DELETE) доступ разрешён,
    только если текущий пользователь совпадает с `id_user` объекта.
    Безопасные методы (GET, HEAD, OPTIONS) разрешены всем.
    """

    def has_object_permission(self, request, view, obj):
        """
        Определяет, имеет ли пользователь право на операцию с объектом.

        Args:
            request (HttpRequest): Объект HTTP-запроса.
            view (View): Экземпляр view, выполняющий проверку.
            obj (Model): Объект модели (например, Publication или Comment).

        Returns:
            bool: True, если доступ разрешён, иначе False.

        Raise:
            Не обрабатываются
        """

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.id_user == request.user
