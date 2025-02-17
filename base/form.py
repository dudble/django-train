from django.forms import ModelForm, Form
from .models import Student, StuWarning, Loan, NewsPort, Leave, Certificate, StuFile

class StudentForm(ModelForm):
    class Meta:
        model = Student
        fields = '__all__'

class WarningForm(ModelForm):
    class Meta:
        model = StuWarning
        fields = '__all__'
        exclude = ['name']

class LoanForm(ModelForm):
    class Meta:
        model = Loan
        fields = '__all__'
        exclude = ['name']

class NewsForm(ModelForm):
    class Meta:
        model = NewsPort
        fields = '__all__'
        exclude = ['host']

class LeaveForm(ModelForm):
    class Meta:
        model = Leave
        fields = '__all__'
        exclude = ['promise', 'cancel']

class CertificateForm(ModelForm):
    class Meta:
        model = Certificate
        fields = '__all__'

class StuFileForm(ModelForm):
    class Meta:
        model = StuFile
        fields = '__all__'
        exclude = ['host', 'post']