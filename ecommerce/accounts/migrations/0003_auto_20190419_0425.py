# Generated by Django 2.1.7 on 2019-04-18 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_full_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guestemail',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
