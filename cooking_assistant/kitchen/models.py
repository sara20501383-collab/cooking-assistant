from django.db import models

class Recipe(models.Model):
    title = models.CharField(max_length=100, verbose_name="نام غذا")
    required_ingredients = models.TextField(verbose_name="مواد لازم (با کاما جدا شود)")
    steps = models.TextField(verbose_name="دستور پخت")

    def __str__(self):
        return self.title