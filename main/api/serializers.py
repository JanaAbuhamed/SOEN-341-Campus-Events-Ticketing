from rest_framework import serializers
from ..models import User, Event


# ---------- USER ----------
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['user_id', 'name', 'email', 'password', 'role', 'status', 'created_at', 'updated_at']
        read_only_fields = ['user_id', 'created_at', 'updated_at']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data, password=password)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# ---------- EVENT ----------
class EventSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    available_spots = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'date', 'time',
            'location', 'capacity', 'ticket_type', 'organizer',
            'attendees', 'created_at', 'available_spots'
        ]
        read_only_fields = ['organizer', 'attendees', 'created_at', 'available_spots']


class EventCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'time', 'location', 'capacity', 'ticket_type']
