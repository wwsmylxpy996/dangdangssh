"""emp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
#http://127.0.0.1:8000/emp_app/regist/
from django.contrib import admin
from django.urls import path
from dangapp import views
app_name='dangapp'
urlpatterns = [

    # 用户注册 登录 登出 start=======
    path('login/', views.login, name='login'),
    path('loginlogic/', views.loginlogic, name='loginlogic'),
    path('regist/', views.regist, name='regist'),
    path('registlogic/', views.registlogic, name='registlogic'),
    path('logout/', views.logout,name='logout'),
    path('confirm/', views.user_confirm),
    # 用户注册 登录 登出 end============

    #验证码
    path('getcaptcha/', views.getcaptcha,name='getcaptcha'),
    #用户名校验
    path('checkname/', views.checkname, name="checkname"),
    #验证码校验
    path('checkcode/', views.checkcode, name="checkcode"),

    #图书列表============
    #首页
    path('index/', views.index,name='index'),
    #详情页
    path('details/', views.details,name='details'),
    #图书分类
    path('category/', views.category_page,name='category'),
    #图书列表============


    #购物车=====start
    #添加，更新，删除
    path('addbook/', views.add_book_inCart, name='addbook'),
    path('updatecart/', views.update_cart, name='updatecart'),
    path('deletebook/', views.delete_book_inCart, name='deletebook'),
    #购物车展示
    path('gotocart/', views.gotocart, name='gotocart'),
    path('shopingcart/', views.shopingcart, name='shopingcart'),
    path('shopingdelcart/', views.shopingdelcart, name='shopingdelcart'),
    #购物车=====end

    #订单结算
    path('budget/', views.budget, name='budget'),
    path('submitorder/', views.submitorder, name='submitorder'),
    #获取地址
    # path('getAdress/', views.getAdress, name='getAdress'),





]
