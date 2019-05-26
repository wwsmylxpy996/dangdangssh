import hashlib
import random, string, time

from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from datetime import datetime
from captchaapp.captcha.image import ImageCaptcha
from dangapp.models import *
from dangapp.cart import *
from django.core.paginator import Paginator

from dangdang import settings


def user_confirm(request):
    """
    用户处理用户发起邮箱验证的请求
    :param request: 用户发来的验证码
    :return:
    """
    try:
        user_code = request.GET.get('code')
        flag = request.GET.get("flag")
        confirm = TConfirmString.objects.filter(code=user_code)
        if confirm:
            # 将用户状态改为可登陆
            confir = confirm[0]
            user = TUser.objects.get(user_id=confir.user_id)
            user.user_status = 1
            user.save()
            confirm = TConfirmString.objects.get(code=user_code)
            confirm.code = ''
            confirm.save()
            if not flag:
                flag = request.session.get('flag')
            if flag == 'index':
                return redirect("dangapp:index")
            elif flag == 'details':
                return redirect("dangapp:details")
            elif flag == 'cart':
                addr = TAddress.objects.filter(user=user)
                return render(request, "dang/indent.html", {"addr": addr})
            # return HttpResponse("成功")
            # 删除验证码
        else:
            return HttpResponse("失败")
    except Exception as e:
        print(e)
        return HttpResponse("失败")


def hash_code(name, now):
    """
    谁调此方法就为谁返回一个随机的验证码
    :param name:
    :param now:
    :return:
    """
    h = hashlib.md5()
    name += now
    h.update(name.encode())
    return h.hexdigest()


def make_confirm_string(new_user):
    """
    为用户生成随机验证码并将验证码保存在数据库中
    :param new_user:
    :return:
    """
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    code = hash_code(new_user.user_name, now)
    TConfirmString.objects.create(code=code, user=new_user)
    return code


def send_email(email, code, flag):
    subject = 'python157'
    text_content = '欢迎访问www.baidu.com，祝贺你收到了我的邮件，有幸收到我的邮件说明你及其幸运'
    html_content = '<p>感谢注册<a href="http://{}/confirm/?code={}&flag={}"target = blank > www.baidu.com < / a >，\欢迎你来验证你的邮箱，验证结束你就可以登录了！ < / p > '.format(
        '127.0.0.1:8000/dangapp', code, flag)
    # 发送邮件所执行的方法以及所需的参数
    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    # 发送的heml文本的内容
    msg.attach_alternative(html_content, "text/html")
    msg.send()


# Create your views here.
# 用户信息 （注册，登录，登出）
def regist(request):
    flag = request.GET.get('flag')
    request.session['flag'] = flag
    return render(request, "dang/register.html")


# 处理登录逻辑
def registlogic(request):
    try:
        with transaction.atomic():
            # if request.method == "POST":
            text_name = request.POST.get('txt_username')  # 手机号或者邮箱
            pwd = request.POST.get('txt_password')
            number = str(request.POST.get('txt_vcode')).lower()  # 页面用书输入验证码
            flag = request.session["flag"]
            num = str(request.session.get('code')).lower()  # 验证码
            # 对pwd加密
            pwd_j = make_password(pwd)

            # return render(request,"dang/index.html")
            # 如果输入验证码与生成验证码相同，保存数据，status：（1 注册，2 登录，0 登出）
            if num == number:
                new_user = TUser.objects.create(user_email=text_name, user_password=pwd_j, user_status=0)
                code = make_confirm_string(new_user)
                send_email(text_name, code, flag)
                request.session["user"] = new_user
                return HttpResponse(
                    "注册成功，请登录注册邮箱验证<a href='https://m0.mail.sina.com.cn'>https://m0.mail.sina.com.cn</a>")
            else:
                return render(request, "dang/register.html")
    except Exception as e:
        print(e)
        return HttpResponse("注册失败")


def login(request):
    flag = request.GET.get('flag')
    request.session['flag'] = flag
    return render(request, "dang/login.html")


def loginlogic(request):
    try:
        username = request.GET.get('username')
        password = request.GET.get('password')
        number = str(request.GET.get('imgVcode')).upper()
        flag = request.session.get('flag')
        num = str(request.session.get('code')).upper()  # 验证码

        if num != number:
            return render(request, "dang/login.html")

        userlist = TUser.objects.filter(user_email=username, user_status=1)
        for user in userlist:
            user_password = user.user_password
            request.session["user"] = user
            checkpwd = check_password(password, user_password)
            if checkpwd:
                if flag == 'index':
                    if len(userlist) > 0:
                        del request.session['flag']
                        return redirect("dangapp:index")
                elif flag == 'cart':
                    addr = TAddress.objects.filter(user=user)
                    return render(request, "dang/indent.html", {"addr": addr})

        return render(request, "dang/login.html")
    except Exception as e:
        print(e)
        del request.session['user']
        return render(request, "dang/login.html")


def logout(request):
    del request.session['user']
    return HttpResponse("ok")


# 验证码
def getcaptcha(request):
    image = ImageCaptcha()
    rand_code = random.sample(string.ascii_letters + string.digits, 4)
    rand_code = "".join(rand_code)
    request.session['code'] = rand_code
    print(rand_code)
    data = image.generate(rand_code)
    return HttpResponse(data, "image/png")


# 校验用户名
def checkname(request):
    username = None
    if request.method == "GET":
        username = request.GET.get("username")
    elif request.method == "POST":
        username = request.POST.get("username")
    print(username)
    re = TUser.objects.filter(user_email=username)
    if re:
        return HttpResponse("用户名已存在")
    return HttpResponse("用户名合法")


# 校验验证码
def checkcode(request):
    checkcode = None
    if request.method == "GET":
        checkcode = request.GET.get("checkcode")
    elif request.method == "POST":
        checkcode = request.POST.get("checkcode")
    code = request.session.get('code')
    print(code)
    if checkcode != code:
        return HttpResponse("验证码错误")
    return HttpResponse("验证码正确")


# 首页
def index(request):
    one_cate_list = DCategory.objects.filter(category_pid__isnull=True)
    two_cate_list = DCategory.objects.filter(category_pid__isnull=False)
    # 新书上架
    new_book_list = users = TBook.objects.raw("select * from t_book ORDER BY shelve_datetime DESC ")[0:8]
    # 热销图书
    hot_book_list = TBook.objects.order_by("-sales")[0:5]
    # 主编推荐 customer_socre
    recommend_book_list = TBook.objects.order_by("-customer_socre")[0:8]
    # 新书热卖榜
    buyer_book_list = TBook.objects.order_by("-sales")[0:8]

    return render(request, "dang/index.html", {"one_cate_list": one_cate_list,
                                               "two_cate_list": two_cate_list,
                                               "new_book_list": new_book_list,
                                               "hot_book_list": hot_book_list,
                                               "recommend_book_list": recommend_book_list,
                                               "buyer_book_list": buyer_book_list,
                                               })


# 图书详情页
def details(request):
    try:
        id = request.GET.get("id")
        book = TBook.objects.filter(book_id=id)[0]
        categroy = book.book_category
        one_cate_list = DCategory.objects.filter(category_pid__isnull=True)
    except Exception as e:
        print(e)
    return render(request, "dang/Bookdetails.html",
                  {"book": book, "category": categroy, "one_cate_list": one_cate_list})


# 图书分类分页展示
def category_page(request):
    try:
        first_id = request.GET.get("first_id")
        second_id = request.GET.get("second_id")
        number = request.GET.get("number")
        if not number:
            number = 1
        one_cate = DCategory.objects.filter(category_id=first_id)[
            0]
        print(one_cate.category_name)
        two_cate_list = DCategory.objects.filter(category_pid__isnull=False)
        if second_id is None:
            l = []
            second_category = DCategory.objects.filter(category_pid=first_id)
            for s in second_category:
                l.append(s.id)
            pg_book = TBook.objects.filter(book_category__in=l)

        else:
            pg_book = TBook.objects.filter(book_category=second_id)
        pagtor = Paginator(pg_book, per_page=4)
        page = pagtor.page(number)
    except Exception as e:
        print(e)
    return render(request, "dang/booklist.html", {"page": page,
                                                  "one_cate": one_cate,
                                                  "two_cate_list": two_cate_list,
                                                  "first_id": first_id,
                                                  "second_id": second_id,
                                                  })


# 购物车信息
def add_book_inCart(request):
    try:
        with transaction.atomic():
            bookid = request.POST.get("bookId")
            cart = request.session.get('cart')
            num = int(request.POST.get("num"))
            if cart is None:
                cart = Cart()
                cart.add_book_toCart(bookid, num)
            else:
                cart.add_book_toCart(bookid, num)
            request.session["cart"] = cart
            user = request.session.get("user")
            if user:
                addrs = TAddress.objects.filter(user_id=user.user_id)
                if addrs:
                    addr = addrs[0]
                    return HttpResponse({"addr": addr})
            return HttpResponse("add")
    except Exception as e:
        print(e)
        del request.session['cart']
        return HttpResponse("添加失败")


# 修改购物车
def update_cart(request):
    try:
        cart = request.session.get("cart")
        amount = request.POST.get("amount")
        bookId = request.POST.get("bookId")
        cart.modify_cart(bookId, amount)
        return HttpResponse("modify")
    except Exception as e:
        print(e)
        return HttpResponse("修改失败")


# 删除购物车
def delete_book_inCart(request):
    try:
        cart = request.session.get("cart")
        bookId = int(request.POST.get("bookId"))
        flag = request.POST.get("flag")
        num = int(request.POST.get("num"))
        cart = request.session.get("cart")
        delcart = request.session.get("delcart")
        if delcart is None:
            delcart = Cart()
        if flag == "del":
            cart.delete_book(bookId)
            delcart.add_book_toCart(bookId, num)
            request.session["delcart"] = delcart
            request.session["cart"] = cart
        elif flag == "back":
            delcart.delete_book(bookId)
            cart.add_book_toCart(bookId, num)
            request.session["cart"] = cart
            request.session["delcart"] = delcart
        return render(request, "dang/shop_car.html", {"cart": cart, "delcart": delcart})
    except Exception as e:
        print(e)
        return HttpResponse("删除失败")


def gotocart(request):
    try:
        cart = request.session.get('cart')
        return render(request, "dang/car.html", {"cart": cart})
    except Exception as e:
        print(e)


def shopingcart(request):
    try:
        cart = request.session.get('cart')
        return render(request, "dang/shop_car.html", {"cart": cart})
    except Exception as e:
        print(e)


def shopingdelcart(request):
    try:
        delcart = request.session.get('delcart')
        return render(request, "dang/shopdel_car.html", {"delcart": delcart})
    except Exception as e:
        print(e)


def budget(request):
    flag = request.GET.get("flag")
    user = request.session.get("user")
    if user:
        cart = request.session.get("cart")
        addr = TAddress.objects.filter(user=user)
        return render(request, "dang/indent.html", {"addr": addr, "cart": cart})

    else:
        request.session['flag'] = flag
        return render(request, "dang/login.html")


# 生成随机订单号
def getNum():
    cur = datetime.now()
    numStr = str(cur.year) + str(cur.month) + str(cur.day) + str(cur.hour) + str(cur.minute) + str(cur.second)
    ran = str(random.randint(1000, 9999))
    return numStr + ran


def submitorder(request):
    try:
        with transaction.atomic():
            ship_man = request.POST.get("ship_man")
            option = request.POST.get("address")
            zipcode = request.POST.get("zipcode")
            telephone = request.POST.get("telephone")
            user = request.session.get("user")
            mobile = request.POST.get("mobile")
            detail_address = request.POST.get("detail_address")
            user_id = user.user_id
            num = getNum()

            # 如果是新地址
            if option == 'new':
                # 保存地址信息
                addr = TAddress(name=ship_man, detail_address=detail_address,
                                zipcode=zipcode, telphone=telephone,
                                addr_mobile=mobile, user_id=user_id)
                addr.save()
            else:
                addr = TAddress.objects.get(id=option)
            # 生成订单
            cart = request.session.get("cart")
            # order=TOrder(num=num,price=cart.total_price,

            order = TOrder.objects.create(num=num, price=cart.total_price,
                                          order_addrid=addr, order_uid=user, status=1)
            # order.save()
            # 生成商品项目表
            for i in cart.cartItem:
                diterm = DOrderiterm(shop_bookid=i.book, shop_ordid=order,
                                     shop_num=i.amount, total_price=cart.total_price)
                diterm.save()
            # 清购物车数据
            del request.session['cart']
            return render(request, "dang/indent ok.html", {"num": num, "totalprice": cart.total_price})
    except Exception as e:
        print(e)
        return HttpResponse("失败")


