from django.core.management.base import BaseCommand
from django.db import transaction
from chat.models import Room
from glosowania.models import Decyzja
from tasks.models import Task
import logging

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Update chat room relations for existing tasks and votes'

    def handle(self, *args, **options):
        self.stdout.write('Updating chat room relations...')
        
        # Update Decyzja chat room relations
        decyzje_updated = 0
        for decyzja in Decyzja.objects.all():
            # Try to find room by old title format
            old_title = f"Vote #{decyzja.pk}: {decyzja.title[:20]}"
            try:
                room = Room.objects.get(title=old_title)
                Decyzja.objects.filter(pk=decyzja.pk).update(chat_room=room)
                decyzje_updated += 1
                self.stdout.write(f'Linked Decyzja #{decyzja.pk} to room "{room.title}"')
            except Room.DoesNotExist:
                # Try new title format (without prefix)
                new_title = f"{decyzja.title[:20]}"
                try:
                    room = Room.objects.get(title=new_title)
                    Decyzja.objects.filter(pk=decyzja.pk).update(chat_room=room)
                    decyzje_updated += 1
                    self.stdout.write(f'Linked Decyzja #{decyzja.pk} to room "{room.title}"')
                except Room.DoesNotExist:
                    pass
        
        # Update Task chat room relations (should already be working, but let's check)
        tasks_updated = 0
        for task in Task.objects.all():
            if task.chat_room_id:
                tasks_updated += 1
            else:
                # Try to find room by old title format
                old_title = f"Task #{task.pk}: {task.title[:50]}"
                try:
                    room = Room.objects.get(title=old_title)
                    task.chat_room = room
                    task.save(update_fields=['chat_room'])
                    tasks_updated += 1
                    self.stdout.write(f'Linked Task #{task.pk} to room "{room.title}"')
                except Room.DoesNotExist:
                    # Try new title format (without prefix)
                    new_title = f"{task.title[:50]}"
                    try:
                        room = Room.objects.get(title=new_title)
                        task.chat_room = room
                        task.save(update_fields=['chat_room'])
                        tasks_updated += 1
                        self.stdout.write(f'Linked Task #{task.pk} to room "{room.title}"')
                    except Room.DoesNotExist:
                        pass
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully updated {decyzje_updated} Decyzja chat rooms and {tasks_updated} Task chat rooms'
            )
        )
