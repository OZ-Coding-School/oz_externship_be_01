def sort_by_total_score(queryset, ordering: str):
    if ordering == "total_score_desc":
        return queryset.order_by("-score")
    elif ordering == "total_score_asc":
        return queryset.order_by("score")
    else:
        return queryset.order_by("-created_at")
