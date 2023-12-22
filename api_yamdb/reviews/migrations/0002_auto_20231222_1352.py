# Generated by Django 3.2 on 2023-12-22 06:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("reviews", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="genretitle",
            options={
                "ordering": ("title",),
                "verbose_name": "произведение-жанр",
                "verbose_name_plural": "Произведения-жанры",
            },
        ),
        migrations.AlterField(
            model_name="customuser",
            name="role",
            field=models.CharField(
                choices=[
                    ("user", "пользователь"),
                    ("moderator", "модератор"),
                    ("admin", "администратор"),
                ],
                default="user",
                max_length=9,
                verbose_name="Роль",
            ),
        ),
        migrations.AlterField(
            model_name="genretitle",
            name="genre",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="reviews.genre",
                verbose_name="Жанр",
            ),
        ),
        migrations.AlterField(
            model_name="genretitle",
            name="title",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="reviews.title",
                verbose_name="Произведение",
            ),
        ),
    ]
