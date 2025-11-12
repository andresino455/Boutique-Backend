# utils/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class OptionalPagination(PageNumberPagination):
    page_size = 10  # Tamaño por defecto
    page_size_query_param = 'page_size'

    def paginate_queryset(self, queryset, request, view=None):
        if request.query_params.get('no_paginate') == 'true':
            return None  # Sin paginación
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return super().get_paginated_response(data)
