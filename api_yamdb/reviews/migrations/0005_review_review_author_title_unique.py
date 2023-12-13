# Generated by Django 3.2 on 2023-12-13 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_remove_review_review_author_title_unique'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='review',
            constraint=models.UniqueConstraint(fields=('author', 'title'), name='review_author_title_unique'),
        ),
    ]
