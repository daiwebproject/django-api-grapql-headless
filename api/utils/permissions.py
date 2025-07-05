from functools import wraps
from graphql import GraphQLError

def login_required(f):
    @wraps(f)
    def wrapper(self, info, *args, **kwargs):
        if not info.context.user.is_authenticated:
            raise GraphQLError('Authentication required')
        return f(self, info, *args, **kwargs)
    return wrapper

def staff_required(f):
    @wraps(f)
    def wrapper(self, info, *args, **kwargs):
        if not info.context.user.is_authenticated or not info.context.user.is_staff:
            raise GraphQLError('Staff permission required')
        return f(self, info, *args, **kwargs)
    return wrapper