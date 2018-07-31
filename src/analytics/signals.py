from django.dispatch import Signal

object_viewed_signal = Signal(providing_args = ["intance", "request"])