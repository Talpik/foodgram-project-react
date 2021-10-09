import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient, ProductCategory


class Command(BaseCommand):
    help = 'Load ingredients in DataBase'

    def handle(self, *args, **options):
        with open('data/ingredients.csv') as file:
            file_reader = csv.reader(file)
            # TODO update fixture's data by category information
            # ProductCategory.objects.all().delete()
            Ingredient.objects.all().delete()
            for row in file_reader:
                name, measurement_unit = row[0], row[1]
                # category_name = row_list[2]
                # category = ProductCategory.objects.get_or_create(name=category_name)[0]
                ingredient = Ingredient(name=name, measurement_unit=measurement_unit)
                ingredient.save()
