# Generated by Django 2.1.7 on 2019-04-06 16:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_auto_20190406_2137'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='author',
        ),
        migrations.DeleteModel(
            name='Message',
        ),
    ]