# Generated by Django 3.2.7 on 2021-09-27 19:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_alter_recipeingredients_recipe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredients',
            name='ingredients',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients_amounts', to='recipes.ingredient'),
        ),
    ]
