from django.conf import settings

def settings_processor(request):
    settings_dict = {
        'DEBUG': settings.DEBUG
    }

    return settings_dict
