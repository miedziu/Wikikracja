"""
Project-wide utility functions
"""
from django.contrib.sites.models import Site


def get_site_domain():
    """
    Get the current site's domain from the django_site table.
    Falls back to 'localhost' if Site is not configured.
    
    Returns:
        str: The domain of the current site (e.g., 'test.wikikracja.pl')
    """
    try:
        return Site.objects.get_current().domain
    except Exception:
        return 'localhost'
