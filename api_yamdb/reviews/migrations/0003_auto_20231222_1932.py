# Generated by Django 3.2 on 2023-12-22 12:32

import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("reviews", "0002_auto_20231222_1352"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="customuser",
            name="confirmation_code",
        ),
        migrations.AlterField(
            model_name="customuser",
            name="email",
            field=models.EmailField(
                help_text="Введите email, не более 254 символа",
                max_length=254,
                unique=True,
                verbose_name="Почта",
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="first_name",
            field=models.CharField(
                blank=True,
                help_text="Введите имя, не более 150 символов",
                max_length=150,
                verbose_name="Имя",
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="last_name",
            field=models.CharField(
                blank=True,
                help_text="Введите фамилию, не более 150 символов",
                max_length=150,
                verbose_name="Фамилия",
            ),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="username",
            field=models.CharField(
                help_text="Введите уникальный логин, не более 150 символов",
                max_length=150,
                unique=True,
                validators=[
                    django.contrib.auth.validators.UnicodeUsernameValidator()
                ],
                verbose_name="Имя пользователя",
            ),
        ),
        migrations.AlterField(
            model_name="title",
            name="name",
            field=models.CharField(
                help_text="Введите название произведения, не более 256 символов",
                max_length=256,
                verbose_name="Название",
            ),
        ),
        migrations.AlterField(
            model_name="title",
            name="year",
            field=models.PositiveSmallIntegerField(
                db_index=True, verbose_name="Год"
            ),
        ),
    ]
