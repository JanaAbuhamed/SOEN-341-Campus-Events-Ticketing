from rest_framework import viewsets
from rest_framework.response import Response

class UserViewSet(viewsets.ViewSet):
    DUMMY_USERS = [
        {"user_id": 1, "name": "Jana", "email": "jana@example.com", "role": 0, "status": 1},
        {"user_id": 2, "name": "Ali", "email": "ali@example.com", "role": 1, "status": 0},
    ]

    def list(self, request):
        return Response(self.DUMMY_USERS)

    def retrieve(self, request, pk=None):
        user = next((u for u in self.DUMMY_USERS if u["user_id"] == int(pk)), None)
        if not user:
            return Response({"error": "User not found"}, status=404)
        return Response(user)

    def create(self, request):
        new_user = request.data
        new_user["user_id"] = len(self.DUMMY_USERS) + 1
        self.DUMMY_USERS.append(new_user)
        return Response(new_user, status=201)

    def update(self, request, pk=None):
        user = next((u for u in self.DUMMY_USERS if u["user_id"] == int(pk)), None)
        if not user:
            return Response({"error": "User not found"}, status=404)
        for key, value in request.data.items():
            user[key] = value
        return Response(user)

    def destroy(self, request, pk=None):
        user = next((u for u in self.DUMMY_USERS if u["user_id"] == int(pk)), None)
        if not user:
            return Response({"error": "User not found"}, status=404)
        self.DUMMY_USERS = [u for u in self.DUMMY_USERS if u["user_id"] != int(pk)]
        return Response(status=204)
