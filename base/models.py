from django.db import models
from django.contrib.auth.models import User

import os
# Create your models here.


class Domitory(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name


class Student(models.Model):
    name = models.CharField(max_length=10000)
    grade = models.CharField(max_length=200)
    major = models.CharField(max_length=10000)
    cla = models.CharField(max_length=10000)
    term = models.CharField(max_length=200)
    ethnic = models.CharField(max_length=10000)
    province = models.CharField(max_length=100000)
    city = models.CharField(max_length=100000)
    county = models.CharField(max_length=100000)
    room = models.ForeignKey(Domitory, on_delete=models.CASCADE, null=True, related_name="students")

    host = models.OneToOneField(User, on_delete=models.CASCADE, related_name='study', null=True)

    def __str__(self):
        return self.name
    
class StuWarning(models.Model):
    host = models.ForeignKey(Student, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    level = models.IntegerField(null=True, default=0)

    def __str__(self):
        return self.name
    
class Loan(models.Model):
    host = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    money  = models.CharField(max_length=200)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.host.name
    
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teach', null=True)
    teachname = models.CharField(max_length=100000)

    def __str__(self):
        return self.teachname

class Topic(models.Model):
    name = models.CharField(max_length=100000)

    def __str__(self):
        return self.name

class NewsPort(models.Model):
    host = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100000)
    description = models.TextField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    have_file = models.BooleanField(default=False)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name
    
class Leave(models.Model):
    host = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    begin_date = models.DateTimeField()
    end_date = models.DateTimeField()
    promise = models.BooleanField(default=False)
    cancel = models.BooleanField(default=False)
    cancel_f = models.BooleanField(default=True)
    name = models.CharField(max_length=200)

    overdue = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class Certificate(models.Model):
    pic = models.ImageField(upload_to='certificate', blank=True)
    host = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, related_name='certificate')
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
class StuFile(models.Model):

    def upload_to(instance, filename):
        path = os.path.join(str(instance.host_id), filename)
        return path

    stufile = models.FileField(upload_to=upload_to, default='')
    post = models.ForeignKey(NewsPort, on_delete=models.SET_NULL, null=True, related_name='file')
    name = models.CharField(max_length=200)
    host = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name