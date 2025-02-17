import urllib.request
from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse, JsonResponse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.db.models import Q

from .models import NewsPort, Topic, StuWarning, Student, Domitory, Loan, Leave, Certificate, StuFile
from .form import StudentForm, WarningForm, LoanForm, NewsForm, LeaveForm, CertificateForm, StuFileForm

import csv
import django_excel as excel
from django import forms
import pyexcel as pe


from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import io

from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

import zipfile
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
import os

# Create your views here.


def index(request):
    q = request.GET.get('q') if request.GET.get('q')!=None else ''

    topic = Topic.objects.all()
    newsports = NewsPort.objects.filter(
        Q(topic__name__contains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    context = {'posts': newsports,'topics': topic}
    return render(request, 'base/home.html', context)

def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, '用户不存在')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, '密码错误')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def newsPage(request, pk):
    page = NewsPort.objects.get(id=pk)

    if page.have_file:
        stu_q = request.GET.get('stu_q') if request.GET.get('stu_q') != None else ''
        
        if stu_q:
            stu_files = StuFile.objects.filter(Q(post=page) & Q(name__icontains=stu_q))
        else: stu_files = StuFile.objects.filter(post=page)

        count = stu_files.count()
        context = {'page': page, 'pk': pk, 'count': count, 'stu_files': stu_files}
        return render(request,'base/page.html', context)
    
    context = {'page': page}
    return render(request,'base/page.html', context)

def download_news_files(request, pk):
    #目前测试没有问题，可能会有其他潜在问题
    page = get_object_or_404(NewsPort, pk=pk)
    stufiles = page.file.all()

    """ response = HttpResponse(content_type='application/zip')
    zip_filename = f'{page.id}_files.zip'
    response['Content-Disposition'] = f'attachment; filename="{zip_filename}".zip' """

    s = io.BytesIO()
    
    with zipfile.ZipFile(s, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
        for stufile in stufiles:
            file_name = stufile.stufile.name
            
            """         local_path = os.path.join(temp.name, file_name)
                        urllib.request.urlretrieve(stufile.stufile.url, local_path)
                        zipf.write(local_path, file_name)
                s.seek(0)
                wrapper = FileWrapper(s)
                response = HttpResponse(wrapper, content_type='application/zip')
                zip_filename = f'{page.id}_files.zip'
                response['Content-Disposition'] = f'attachment; filename="{zip_filename}".zip'
            """
            if default_storage.exists(file_name):
                try:
                    with default_storage.open(file_name, 'rb') as f:
                        content = f.read()
                        arcname = os.path.basename(file_name)
                        zipf.writestr(arcname, content)
                        print(f"已添加: {arcname} (大小: {len(content)} 字节)")

                except Exception as e:
                    print(f"处理失败: {file_name}, 错误: {str(e)}")

    s.seek(0)
    response = HttpResponse(s.getvalue(), content_type='application/zip')
    
    response['Content-Disposition'] = f'attachment; filename="{page.id}.zip"'
    
    return response



@login_required(login_url='/login')
def updateNews(request, pk):
    news = NewsPort.objects.get(id=pk)
    form = NewsForm(instance=news)
    if request.user != news.host.user:
        return HttpResponse("您不是本条通知的所有者")
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        news.name = request.POST.get('name')
        news.topic = topic
        news.description = request.POST.get('description')
        check = request.POST.get('have')
        news.have_file = (check=='on')
        news.save()
        return redirect('home')
    context = {'form': form}
    return render(request, 'base/create/create_news.html',context)

@login_required(login_url='/login')
def updateStu(request, pk):
    page = 'update'
    stu = Student.objects.get(id=pk)
    form = StudentForm(instance=stu)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=stu)
        if form.is_valid():
            form.save()
        return redirect('home')
    context = {'form': form, "pk": pk, 'page': page}
    return render(request, 'base/create.html', context)

@login_required(login_url='/login')
def updateWarning(request, pk):
    warn = StuWarning.objects.get(id=pk)
    page = ''
    form = WarningForm(instance=warn)
    if request.method == 'POST':
        form = WarningForm(request.POST, instance=warn)
        if form.is_valid():
            form.save()
        return redirect('home')
    context = {'form': form, 'page': page}
    return render(request, 'base/create.html', context)

@login_required(login_url='/login')
def updateLoan(request, pk):
    loan = Loan.objects.get(id=pk)
    page = ''
    form = LoanForm(instance=loan)
    if request.method == 'POST':
        form = LoanForm(request.POST, instance=loan)
        if form.is_valid():
            form.save()
        return redirect('home')
    context = {'form': form, 'page': page}
    return render(request, 'base/create.html', context)





@login_required(login_url='/login')
def createStu(request):
    page = 'create'
    form = StudentForm()
    rooms = Domitory.objects.all()
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            stu = form.save(commit=False)
            stu.save()
            return redirect('home')
    context = {'form': form, 'rooms': rooms, 'page': page}
    return render(request, 'base/create/create.html', context)

@login_required(login_url='/login')
def createWarn(request):
    form = WarningForm()
    if request.method == 'POST':
        form = WarningForm(request.POST)
        if form.is_valid():
            warning = form.save(commit=False)
            warning.name = warning.host.name
            warning.save()           
            return redirect('home')
    context = {'form': form, 'page': ''}
    return render(request, 'base/create/create.html', context)

@login_required(login_url='/login')
def createLoan(request):
    form = LoanForm()
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.name = loan.host.name
            loan.save()
            return redirect('home')
    context = {'form': form, 'page': ''}
    return render(request, 'base/create/create.html', context)

def createLeave(request):
    form = LeaveForm()
    stus = Student.objects.all()
    if request.method == 'POST':
        host_name = request.POST.get('stu')
        host = Student.objects.get(name=host_name)
        Leave.objects.create(
            host=host,
            name=request.POST.get('name'),
            begin_date=request.POST.get('start'),
            end_date=request.POST.get('end')
        )
        return redirect('home')
    context = {'form': form, 'stus': stus}
    return render(request, 'base/create/create_leave.html', context)

@login_required(login_url='/login')
def createNews(request):
    form = NewsForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        NewsPort.objects.create(
            host=request.user.teach,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            have_file=(request.POST.get('have')=='on')
        )
        return redirect('home')
    context = {'form': form,'topics': topics}
    return render(request,'base/create/create_news.html',context)

@csrf_exempt
def mid_cer(request):
    if request.method == 'POST':
        stu_name = request.POST.get('host')
        host = Student.objects.get(name=stu_name)
        Certificate.objects.create(
            host = host,
            pic = request.FILES.get('pic'),
            name = request.POST.get('name')
        )
        return JsonResponse({'success': True})
    else: return JsonResponse({'success': False})


def create_certificate(request):
    students = Student.objects.all()
    form = CertificateForm()
    context = {'form': form, 'students': students}
    return render(request, 'base/create/create_certificate.html', context)

@login_required(login_url='/login')
def upload_file(request, pk):
    form = StuFileForm()
    students = Student.objects.all()
    if request.method == 'POST':
        form = StuFileForm(request.POST, request.FILES)
        stu_name = request.POST.get('host')
        host = Student.objects.get(name=stu_name)
        post = NewsPort.objects.get(id=pk)
        name = host.name + '_' + post.name
        file = request.FILES.get('file')
        StuFile.objects.create(
            stufile=file,
            name=name,
            host=host,
            post=post
        )
        return redirect('back_home')
        

    context = {'form': form, 'students': students}
    return render(request, 'base/create/create_file.html', context)
    
            



def pdfStu(request, pk):
    stu = Student.objects.get(id=pk)
    butter = io.BytesIO()
    pdfmetrics.registerFont(TTFont('宋体', 'simsun.ttc'))
    p = canvas.Canvas(butter)
    p.setFont('宋体', 36)
    p.drawString(10, 800, "姓名："+stu.name)
    p.drawString(10, 750, "年级："+stu.grade)
    p.drawString(10, 700, "专业："+stu.major)
    p.drawString(10, 650, "班级："+stu.cla)
    p.drawString(10, 600, "宿舍："+stu.room.name)
    p.drawString(10, 550, "民族："+stu.ethnic)
    p.drawString(10, 500, "省："+stu.province)
    p.drawString(10, 450, "市："+stu.city)
    p.drawString(10, 400, "县："+stu.county)
    p.showPage()
    p.save()
    butter.seek(0)
    return FileResponse(butter, as_attachment=True, filename="hallo.pdf")

    





class UploadFileForm(forms.Form):
    file = forms.FileField()

def back_home(request):
    return render(request, 'base/back_home.html', {})

@login_required(login_url='/login')
def import_warning(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        def warning_func(row):
            stu = Student.objects.filter(name=row[0]).first()
            row[2] = stu
            return row

        if form.is_valid():
            request.FILES["file"].save_book_to_database(
                models=[StuWarning],
                initializers=[warning_func],
                mapdicts=[
                    {"student": "name", "level": "level", "host": "host"},
                ],
            )
            return redirect("back_home")
        else:
            return HttpResponse("文件格式错误")
    else:
        form = UploadFileForm()
    context = {'form': form}
    return render(request, 'base/upload_form.html', context)

@login_required(login_url='/login')
def import_loan(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        def loan_func(row):
            stu = Student.objects.filter(name=row[0]).first()
            row[2] = stu
            return row

        if form.is_valid():
            request.FILES["file"].save_book_to_database(
                models=[Loan],
                initializers=[loan_func],
                mapdicts=[
                    {"student": "name", "money": "money", "host": "host"},
                ],
            )
            return redirect("back_home")
        else:
            return HttpResponse("文件格式错误")
    else:
        form = UploadFileForm()
    context = {'form': form}
    return render(request, 'base/upload_form.html', context)

@login_required(login_url='/login')
def import_stu(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        def stu_func(row):
            room = Domitory.objects.filter(name=row[0]).first()
            row[0] = room
            return row

        if form.is_valid():
            file = request.FILES['file']
            file.save_book_to_database(
                models=[Student],
                initializers=[stu_func],
                mapdicts=[
                    ["room", "name", "grade", "major", "cla", "term", "ethnic", "province", "city", "county"]
                ],
            )
            return redirect("back_home")
        else:
            return HttpResponse("文件格式错误")
    else:
        form = UploadFileForm()
    context = {'form': form}
    return render(request, 'base/upload_form.html', context)

def export_data(request, atype):
    if atype == "student":
        return excel.make_response_from_a_table(
            Student, "xls", file_name="student"
        )
    elif atype == 'stu_warning':
        return excel.make_response_from_a_table(
            StuWarning, "xls", file_name="stuwaring"
        )
    elif atype == 'loan':
        return excel.make_response_from_a_table(
            Loan, "xls", file_name='loan'
        )
    elif atype == 'leave':
        return excel.make_response_from_a_table(
            Leave, 'xls', file_name='leave'
        )



def stulist(request):
    stu_q = request.GET.get('stu_q') if request.GET.get('stu_q') != None else ''
    stus = Student.objects.filter(Q(name__icontains=stu_q))
    count = stus.count()
    context = {'stus': stus, 'count': count}
    return render(request, 'base/list/stu_list.html', context)

def warningList(request):
    warn_q = request.GET.get('warn_q') if request.GET.get('warn_q') != None else ''
    warns = StuWarning.objects.filter(Q(name__icontains=warn_q) | Q(level__icontains=warn_q))
    count = warns.count()
    context = {'warns': warns, 'count': count}
    return render(request, 'base/list/warning_list.html', context)

def loanList(request):
    loan_q = request.GET.get('loan_q') if request.GET.get('loan_q') != None else ''
    loans = Loan.objects.filter(Q(name__icontains=loan_q))
    count = loans.count()
    context = {'loans': loans, 'count': count}
    return render(request, 'base/list/loan_list.html', context)



@login_required(login_url='/login')
def deleteStu(request, pk):
    student = Student.objects.get(id=pk)
    student.delete()
    return redirect('stu_list')
@login_required(login_url='/login')
def deleteWarning(request, pk):
    warning = StuWarning.objects.get(id=pk)
    warning.delete()
    return redirect('warn_list')
@login_required(login_url='/login')
def deleteLoan(request, pk):
    loan = Loan.objects.get(id=pk)
    loan.delete()
    return redirect('loan_list')
@login_required(login_url='/login')
def deleteNews(request, pk):
    port = NewsPort.objects.get(id=pk)
    port.delete()
    return redirect('home')




@csrf_exempt
def updateApprove(request):
    if request.method == 'POST':

        updated_data = {}
        
        for key, value in request.POST.items():
            if key.startswith('promise_'):
                promise_id = key.split('_')[1]
                promise_val = (value == 'on')
                leave = Leave.objects.get(id=promise_id)
                leave.promise = promise_val
                leave.save()
                updated_data[promise_id] = {'promise': promise_val}
            if key.startswith('cancel_'):
                cancel_id = key.split('_')[1]
                cancel_val = (value == 'on')
                leave = Leave.objects.get(id=cancel_id)
                leave.cancel = cancel_val
                if (timezone.now() > leave.end_date) & leave.cancel_f :
                    leave.overdue = True
                leave.save()
                updated_data[cancel_id] = {'cancel': cancel_val}

        return JsonResponse({'success': True, 'update_date': updated_data})
        
    else:
        return JsonResponse({'success': False})
        
@login_required(login_url='/login')
def approve(request):
    leave_q = request.GET.get('leave_q') if request.GET.get('leave_q') != None else ''
    leaves = Leave.objects.filter(Q(host__name__contains=leave_q) | Q(name__icontains=leave_q))
    context = {'leaves': leaves, 'leave_q': leave_q}
    return render(request, 'base/list/leave_list.html', context)

@csrf_exempt
def mid_domitory(request):
    if request.method == 'POST':
        room_name = request.POST.get('name')
        room, created = Domitory.objects.get_or_create(name=room_name)
        for key, value in request.POST.items():
            if key.startswith('stu-'):
                stu_name = value
                stu = Student.objects.get(name=stu_name)
                stu.room = room
                stu.save()

        return JsonResponse({'success': True})
    else: return JsonResponse({'success': False})

@login_required(login_url='/login')
def add_domitory(request):
    doms = Domitory.objects.all()
    stus = Student.objects.all()
    context = {'doms': doms, 'stus': stus}
    return render(request, 'base/add_dom.html', context)

def domitoryList(request):
    stu_q = request.GET.get('stu_q') if request.GET.get('stu_q') != None else ''
    if stu_q:
        doms = Domitory.objects.filter(students__name=stu_q)
    else: doms = Domitory.objects.all()
    dom_stus = {}
    for dom in doms:
        dom_stus[dom] = Student.objects.filter(Q(room=dom)& (Q(name__icontains=stu_q) | Q(grade__icontains=stu_q) | Q(major__icontains=stu_q) | Q(cla__icontains=stu_q) | Q(term__icontains=stu_q)))
    count = doms.count()
    context = {'doms': doms, 'dom_stus': dom_stus, 'count': count}
    return render(request, 'base/list/domitory_list.html', context)

def certificateList(request):
    cer_q = request.GET.get('cer_q') if request.GET.get('cer_q') != None else ''
    if cer_q:
        cers = Certificate.objects.filter(Q(host__name=cer_q) | Q(name__icontains=cer_q))
    else: cers = Certificate.objects.all()
    count = cers.count()
    context = {'cers': cers, 'count': count}
    return render(request, 'base/list/certificate_list.html', context)

def dormitoryExcel(request):
    doms = Domitory.objects.all()
    datas = [["宿舍名", "学生"]]
    for dom in doms:
        dom_name = str(dom.name)
        stus = Student.objects.filter(room=dom)
        data = [dom_name, ]
        for stu in stus:
            stu_name = str(stu.name)
            data.append(stu_name)
        datas.append(data)
    content = pe.save_as(array=datas, dest_file_type="xlsx")
        
    response = HttpResponse(content.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response["Content-Disposition"] = 'attachment; filename="books_export.xlsx"'
    return response