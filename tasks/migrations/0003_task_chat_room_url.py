from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0002_add_rejected_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="chat_room_url",
            field=models.URLField(
                blank=True,
                help_text="Link to chat room for discussing this task",
                max_length=500,
            ),
        ),
    ]
