from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Custom pagination class for API responses using page number pagination.

    Attributes:
    - page_size: Default number of items per page (2).
    - page_size_query_param: Query parameter for specifying the number of items per page (default is 'page_size').
    - max_page_size: Maximum number of items allowed per page (100).
    """
    page_size = 4
    page_size_query_param = "page_size"
    max_page_size = 100
