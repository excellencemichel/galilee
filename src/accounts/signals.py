from django.dispatch import Signal

user_logged_in = Signal(providing_args = ["intance", "request"])