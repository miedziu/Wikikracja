# Standard library imports
import json
import logging

# Third party imports
from django.conf import settings
from django.http import HttpRequest

# First party imports
from board.models import Post

log = logging.getLogger(__name__)


def footer(request: HttpRequest):
    footer = Post.objects.filter(title__iexact='Footer').order_by('-updated').first()
    return {
        'footer': footer
    }


def site_description(request):
    return {
        'site_description': settings.SITE_DESCRIPTION
    }


def vapid_public_key(request):
    return {
        'vapid_public_key': settings.PUSH_NOTIFICATIONS['WEBPUSH'].get('VAPID_PUBLIC_KEY', '')
    }


def firebase_config(request):
    # Convert Firebase config dict to JSON string for safe embedding in HTML
    return {
        'firebase_config': json.dumps(settings.FIREBASE_CONFIG or {})
    }
