import graphene
import graphql_jwt
from django.contrib.auth import get_user_model
from api.types.user import UserType

User = get_user_model()

class RegisterUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        first_name = graphene.String()
        last_name = graphene.String()
    
    user = graphene.Field(UserType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, username, email, password, first_name=None, last_name=None):
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name or '',
                last_name=last_name or ''
            )
            return RegisterUser(user=user, success=True, errors=[])
        except Exception as e:
            return RegisterUser(user=None, success=False, errors=[str(e)])

class AuthMutation:
    register = RegisterUser.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()