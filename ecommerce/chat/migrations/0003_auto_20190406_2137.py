# Generated by Django 2.1.7 on 2019-04-06 16:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_message_room'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='room',
        ),
        migrations.RemoveField(
            model_name='message',
            name='timestamp',
        ),
    ]
