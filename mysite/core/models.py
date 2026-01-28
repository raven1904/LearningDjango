from django.db import models
'''Database tables (ORM), Each class = one table'''

class Student(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()

    def __str__(self):
        return self.name

