from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0003_task_chat_room_url"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="task",
            name="chat_room_url",
        ),
    ]
