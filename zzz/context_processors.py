from django.http import HttpRequest
from board.models import Post
import logging

logging.basicConfig(filename='/var/log/wiki.log', datefmt='%d-%b-%y %H:%M:%S', format='%(asctime)s %(levelname)s %(funcName)s() %(message)s', level=logging.INFO)

def footer(request: HttpRequest):
    footer = Post.objects.filter(title__iexact='Footer').order_by('-updated').first()
        
    return {'footer': footer}
