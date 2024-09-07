# Generated by Django 4.2.11 on 2024-08-31 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("friends", "0002_customuser_first_name_customuser_last_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="role",
            field=models.CharField(
                choices=[("user", "User"), ("admin", "Admin")],
                default="user",
                max_length=20,
            ),
        ),
    ]
