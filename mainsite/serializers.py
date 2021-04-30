from django.conf import settings
from django.contrib.auth import authenticate, login
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from rest_framework import serializers


class AuthTokenSerializerWithoutPassword(serializers.Serializer):
    username = serializers.CharField(label=_("Username"))

    def validate(self, attrs):
        username = attrs.get('username')

        if username:
            user = User.objects.get(email=username)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs