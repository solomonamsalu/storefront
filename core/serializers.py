from djoser.serializers import UserSerializer as BaseUserserializer, UserCreateSerializer as BaseUserCreateSerializer

class UserCreateSerializer(BaseUserCreateSerializer):
      class Meta(BaseUserCreateSerializer.Meta):
            fields=['id','username','password','email','first_name','last_name']


class UserSerializer(BaseUserserializer,):
      class Meta(BaseUserserializer.Meta):
            fields=['id','username','email','first_name','last_name']


