from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0004_remove_chat_room_url"),
        ("chat", "0009_room_protected"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="chat_room",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="task",
                to="chat.room",
                verbose_name="chat room",
            ),
        ),
    ]
