from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="status",
            field=models.CharField(
                choices=[
                    ("active", "Active"),
                    ("completed", "Completed"),
                    ("cancelled", "Cancelled"),
                    ("rejected", "Rejected"),
                ],
                default="active",
                max_length=16,
            ),
        ),
    ]
