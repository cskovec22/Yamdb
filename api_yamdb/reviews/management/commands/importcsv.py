import csv
from typing import Any
from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, GenreTitle, Genre, Review, Title, CustomUser


class Command(BaseCommand):
    help = 'Импортирует данные из csv в базу данных'

    def handle(self, *args: Any, **options: Any) -> str | None:
        with open('static/data/category.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for count, row in enumerate(reader):
                if count == 0:
                    continue
                Category.objects.create(id=row[0], name=row[1], slug=row[2])
            self.stdout.write(self.style.SUCCESS('Категории загружены'))

        with open('static/data/users.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for count, row in enumerate(reader):
                if count == 0:
                    continue
                CustomUser.objects.create(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    role=row[3],
                    bio=row[4],
                    first_name=row[5],
                    last_name=row[6]
                )
            self.stdout.write(self.style.SUCCESS('Пользователи загружены'))

        with open(
            'static/data/genre.csv',
            newline='',
            encoding='utf-8'
        ) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for count, row in enumerate(reader):
                if count == 0:
                    continue
                Genre.objects.create(id=row[0], name=row[1], slug=row[2])
            self.stdout.write(self.style.SUCCESS('Жанры загружены'))

        with open(
            'static/data/titles.csv',
            newline='',
            encoding='utf-8'
        ) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for count, row in enumerate(reader):
                if count == 0:
                    continue
                Title.objects.create(
                    id=row[0],
                    name=row[1],
                    year=row[2],
                    category_id=row[3]
                )
            self.stdout.write(self.style.SUCCESS('Произведения загружены'))

        with open(
            'static/data/genre_title.csv',
            newline='',
            encoding='utf-8'
        ) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for count, row in enumerate(reader):
                if count == 0:
                    continue
                GenreTitle.objects.create(
                    id=row[0],
                    title_id=row[1],
                    genre_id=row[2]
                )
            self.stdout.write(self.style.SUCCESS(
                'Таблица Genre-title загружена'
            ))

        with open(
            'static/data/review.csv',
            newline='',
            encoding='utf-8'
        ) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for count, row in enumerate(reader):
                if count == 0:
                    continue
                Review.objects.create(
                    id=row[0],
                    title_id=row[1],
                    text=row[2],
                    author_id=row[3],
                    score=row[4],
                    pub_date=row[5]
                )
            self.stdout.write(self.style.SUCCESS('Отзывы загружены'))

        with open(
            'static/data/comments.csv',
            newline='',
            encoding='utf-8'
        ) as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for count, row in enumerate(reader):
                if count == 0:
                    continue
                Comment.objects.create(
                    id=row[0],
                    review_id=row[1],
                    text=row[2],
                    author_id=row[3],
                    pub_date=row[4]
                )
            self.stdout.write(self.style.SUCCESS('Комментарии загружены'))
