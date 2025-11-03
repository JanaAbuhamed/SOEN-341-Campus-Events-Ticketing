# from .models import User, Event
# add other models if you have them

from main.models.models import User, Event

# main/models/__init__.py
from .models import User, Event, SavedEvent, Payment

__all__ = ["User", "Event", "SavedEvent" , "Payment"]
