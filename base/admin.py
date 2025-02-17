from django.contrib import admin
from .models import Student, Domitory, StuWarning, Loan, Teacher, Topic, NewsPort, Leave, Certificate, StuFile
# Register your models here.

admin.site.register(Student)
admin.site.register(Domitory)
admin.site.register(StuWarning)
admin.site.register(Loan)
admin.site.register(Topic)
admin.site.register(Teacher)
admin.site.register(NewsPort)
admin.site.register(Leave)
admin.site.register(Certificate)
admin.site.register(StuFile)