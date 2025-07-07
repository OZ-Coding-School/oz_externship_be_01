from rest_framework.pagination import PageNumberPagination


class PaginationList(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

# def paginate_list(data: list, page: int, page_size: int) -> dict:
#     total_count = len(data)
#     total_pages = (total_count + page_size - 1) // page_size
#     start = (page - 1) * page_size
#     end = start + page_size
#     paged_data = data[start:end]
#     return {
#         "paged_data": paged_data,
#         "pagination": {
#             "page": page,
#             "page_size": page_size,
#             "total_count": total_count,
#             "total_pages": total_pages,
#         },
#     }

# result = paginate_list(submissions, filters.get("page", 1), filters.get("page_size", 10))
# paged_submissions = result["paged_data"]
# pagination_info = result["pagination"]
#
# serializer = self.serializer_class(paged_submissions, many=True)