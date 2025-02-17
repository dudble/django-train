from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name= 'index'),

    path('home/', views.index, name= 'home'),

    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('page/<str:pk>', views.newsPage, name='newspage'),

    path('createStu/', views.createStu, name='create_stu'),
    path('create_warning/', views.createWarn, name='create_warning'),
    path('create_loan/', views.createLoan, name='create_loan'),
    path('create_news/', views.createNews, name='create_news'),
    path('create_leave/', views.createLeave, name='create_leave'),

    path('uploadWarning/', views.import_warning, name='upload_warning'),
    path('uploadStu/', views.import_stu, name='upload_stu'),
    path('uploadLoan/', views.import_loan, name='upload_loan'),

    path('backMid/', views.back_home, name='back_home'),

    path('updateStu/<str:pk>', views.updateStu, name='update_stu'),
    path('update_warning/<str:pk>', views.updateWarning, name='update_warning'),
    path('update_loan/<str:pk>', views.updateLoan, name='update_loan'),
    path('update_news/<str:pk>', views.updateNews, name='update_news'),

    re_path(r'^export/(.*)', views.export_data, name="export_data"),

    path('stulist/', views.stulist, name='stu_list'),
    path('warn_list/', views.warningList, name='warn_list'),
    path('loan_list/', views.loanList, name='loan_list'),
    path('stupdf/<str:pk>', views.pdfStu, name='stu_pdf'),

    path('delete_news/<str:pk>', views.deleteNews, name='delete_news'),
    path('delete_loan/<str:pk>', views.deleteLoan, name='delete_loan'),
    path('delete_stu/<str:pk>', views.deleteStu, name='delete_stu'),
    path('delete_warning/<str:pk>', views.deleteWarning, name='delete_warning'),

    path('approve/', views.approve, name='approve'),
    path('update_approve/', views.updateApprove, name='update_approve'),

    path('mid_cer/', views.mid_cer, name='mid_cer'),
    path('create_cer/', views.create_certificate, name='create_cer'),
    path('certificate_list', views.certificateList, name='cer_list'),

    path('upload_file/<str:pk>', views.upload_file, name='upload_file'),
    
    path('add_domitory/', views.add_domitory, name='add_domitory'),
    path('mid_domitory/', views.mid_domitory, name='mid_dom'),
    path('domitory_list', views.domitoryList, name='dom_list'),

    path('download/<str:pk>/', views.download_news_files, name='download_news_files'),
    path("export_dormitory", views.dormitoryExcel, name='export_dom')
]

