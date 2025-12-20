from django.apps import AppConfig


class HomeConfig(AppConfig):
    name = 'home'

    def ready(self):
        import os
        from django.db.models.signals import post_migrate
        from django.dispatch import receiver
        
        @receiver(post_migrate)
        def update_site_domain(sender, **kwargs):
            """Update Site domain from environment variables after migrations."""
            from django.contrib.sites.models import Site
            
            site_domain = os.getenv('SITE_DOMAIN')
            site_name = os.getenv('SITE_NAME')
            
            if site_domain:
                try:
                    site = Site.objects.get(id=1)
                    if site.domain != site_domain or (site_name and site.name != site_name):
                        site.domain = site_domain
                        if site_name:
                            site.name = site_name
                        site.save()
                except Site.DoesNotExist:
                    Site.objects.create(id=1, domain=site_domain, name=site_name or site_domain)
                except Exception:
                    pass
