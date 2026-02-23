from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('obywatele', '0009_alter_uzytkownik_uid'),
    ]

    operations = [
        migrations.AddField(
            model_name='uzytkownik',
            name='onboarding_status',
            field=models.CharField(
                choices=[
                    ('email_entered', 'Email entered'),
                    ('email_confirmed', 'Email confirmed'),
                    ('form_completed', 'Form completed'),
                ],
                default='email_entered',
                max_length=32,
            ),
        ),
    ]
