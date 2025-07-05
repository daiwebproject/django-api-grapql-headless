import graphene
from graphene import relay
from graphene_django import DjangoObjectType

# ✅ PageInfoType tự định nghĩa
class PageInfoType(graphene.ObjectType):
    has_next_page = graphene.Boolean()
    has_previous_page = graphene.Boolean()
    start_cursor = graphene.String()
    end_cursor = graphene.String()
    current_page = graphene.Int()
    total_pages = graphene.Int()
    total_count = graphene.Int()
    page_size = graphene.Int()

# ✅ Kết nối có tổng số phần tử
class CountableConnection(relay.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()

    def resolve_total_count(self, info, **kwargs):
        return self.length

# ✅ Kết nối mở rộng, KHÔNG cần edges nếu không tuỳ chỉnh
class ExtendedConnection(CountableConnection):
    class Meta:
        abstract = True

    page_info = graphene.Field(graphene.NonNull(relay.PageInfo))

# ✅ Input cho phân trang và sắp xếp
class PaginationInput(graphene.InputObjectType):
    page = graphene.Int(default_value=1)
    page_size = graphene.Int(default_value=20)

class SortInput(graphene.InputObjectType):
    field = graphene.String(required=True)
    direction = graphene.Enum('SortDirection', [('ASC', 'asc'), ('DESC', 'desc')])()

# ✅ Hàm tạo dynamic Paginated Type
def create_paginated_type(object_type, name):
    meta_class = type("Meta", (), {"name": f"Paginated{name}"})

    fields = {
        "Meta": meta_class,
        "results": graphene.List(object_type),
        "page_info": graphene.Field(graphene.NonNull(PageInfoType)),  # ✅ dùng class đã định nghĩa
    }

    return type(f"Paginated{name}", (graphene.ObjectType,), fields)

# ✅ Hàm phân trang queryset
def paginate_queryset(queryset, page=1, page_size=20):
    from django.core.paginator import Paginator

    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)

    return {
        'results': page_obj.object_list,
        'page_info': {
            'has_next_page': page_obj.has_next(),
            'has_previous_page': page_obj.has_previous(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
            'page_size': page_size,
            'start_cursor': f"cursor:{(page - 1) * page_size}",
            'end_cursor': f"cursor:{page * page_size - 1}",
        }
    }
