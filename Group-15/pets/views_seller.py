import os
import time

from django.contrib import messages
from django.db.models import Q, Sum
from django.shortcuts import render, redirect

from main.settings import MEDIA_URL
from pets.models import Goods, Seller, Order, GoodsCategory, Services, Bookings, LI_ORDER_STATUS, LI_BOOKINGS_STATUS


def seller_register(request):
    """卖家-注册"""

    if request.method == 'POST':
        # 注册操作
        params = request.POST

        username = params.get('username', '')
        password = params.get('password', '')
        confirm_password = params.get('confirm_password', '')
        email = params.get('email', '')
        age = params.get('age', '')

  

        # 校验
        if not all([username, password, confirm_password, email, age]):
            messages.error(request, 'Illegal Params')
            return redirect('seller/register')

        # 密码
        if password != confirm_password:
            messages.error(request, 'Password Inconsistency')
            return redirect('/user/register')

        # 查看用户名是否存在
        if Seller.objects.filter(username=username).first():
            messages.error(request, 'Username Already Exists')
            return redirect('/user/register')

        # ———— 创建用户 ————
        Seller.objects.create(
            username=username,
            password=password,
            email=email,
            age=age
        )

        messages.success(request, 'Register Successfully')
        return redirect('/user/login')


def seller_login(request):
    """卖家-登录"""

    if request.method == 'POST':  # 登录操作

        # 登录操作
        params = request.POST
        account = params.get('account')
        password = params.get('password')

        if not all([account, password]):
            messages.error(request, 'Illegal Params')
            return redirect('/user/login')

        db_seller = Seller.objects.filter(
            Q(
                username=account,
                password=password
            )
            |
            Q(
                email=account,
                password=password
            )
        ).first()
        if not db_seller:
            messages.error(request, 'Account Or Password Error')
            return redirect('/user/login')

        # 登录成功
        request.session['seller'] = db_seller.get_seller_info()
        messages.success(request, 'Login Success !')
        return redirect('/seller')


def seller_logout(request):
    """卖家-注销"""

    # 清楚session
    if 'seller' in request.session:
        del request.session['seller']

    # 重定向到登录
    messages.success(request, 'Logout...')
    return redirect('/user/login')

def seller_account(request):
    """卖家-主页"""

    # ———— 检查登录 ————
    if 'seller' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    seller_info = request.session['seller']
    seller_id = seller_info['id']

    return render(request,
                  'seller/seller_account.html',
                  context={
                  })

def seller_update(request):
    """卖家信息-修改"""

    # ———— 检查登录 ————
    if 'seller' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    seller_info = request.session['seller']
    seller_id = seller_info['id']
    db_seller = Seller.objects.filter(pk=seller_id).first()

    if request.method == 'POST':
        params = request.POST

        password = params.get('password')
        email = params.get('email')
        age = params.get('age')

        db_seller.email = email
        db_seller.age = age

        if password:  # 有密码才修改
            db_seller.password = password

        db_seller.save()

        # 覆盖 session
        request.session['seller'] = db_seller.get_seller_info()

        messages.success(request, 'Successfully Update')
        return redirect('/seller/seller_account/')

def seller_index(request):
    """卖家-主页"""

    # ———— 检查登录 ————
    if 'seller' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    seller_info = request.session['seller']
    seller_id = seller_info['id']

    # 计算 数据

    # ———— 商品 ————
    count_goods = Goods.objects.filter(seller_id=seller_id).count()  # 商品-上架数量
    count_goods_orders = Order.objects.filter(seller_id=seller_id).count()  # 商品-订单数量
    total_price = Order.objects.filter(seller_id=seller_id).aggregate(
        total=Sum('total_price')
    )  # 总金额

    # ———— 服务 ————
    count_service = Services.objects.filter(seller_id=seller_id).count()  # 服务-上架数量
    count_service_bookings = Bookings.objects.filter(seller_id=seller_id).count()  # 服务-预订数量
    total_price_service = Bookings.objects.filter(seller_id=seller_id).aggregate(
        total=Sum('total_price')
    )  # 总金额

    return render(request,
                  'seller/index.html',
                  context={
                      'goods': {
                          'on_shelf': count_goods,
                          'orders': count_goods_orders,
                          'total_price': float(total_price['total'] or 0)
                      },
                      'services': {
                          'on_shelf': count_service,
                          'bookings': count_service_bookings,
                          'total_price': float(total_price_service['total'] or 0),
                      }
                  })


def seller_good_del(request, pk):
    """商品-删除"""

    # ———— 检查登录 ————
    if 'seller' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    seller_info = request.session['seller']

    db_goods = Goods.objects.filter(
        pk=pk,
        seller_id=seller_info['id']
    ).first()

    if not db_goods:
        messages.error(request, 'Goods Not Exist')
        return redirect('/seller/good_list/')

    # 删除
    db_goods.delete()

    messages.success(request, 'Delete Success')
    return redirect('/seller/good_list/')


def seller_good_update(request, pk):
    """商品-修改"""

    # ———— 检查登录 ————
    if 'seller' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    seller_info = request.session['seller']

    if request.method == 'GET':  # 获取页面

        goods = Goods.objects.filter(pk=pk).first()

        return render(request,
                      'seller/good_update.html',
                      context={
                          'goods': goods,
                          'li_category': GoodsCategory.objects.order_by('-id')
                      })

    # 修改操作
    params = request.POST
    title = params.get('title')
    desc = params.get('desc')
    price = float(params.get('price'))
    category_id = params.get('category')

    image = request.FILES.get('image_file')

    # 校验
    if not all([title, desc, price]):
        messages.error(request, 'Illegal Params')
        return redirect(f'/seller/good_update/{pk}')

    # 查询 pk
    db_goods = Goods.objects.filter(pk=pk).first()

    if image:
        # 保存文件
        dir_name = 'seller/goods/'
        file_dir_path = os.path.join(MEDIA_URL, dir_name)
        if not os.path.exists(file_dir_path):
            os.makedirs(file_dir_path)

        # 文件路径
        tmp = str(int(time.time()))
        file_real_name = f'{tmp}-{image.name}'
        file_path = os.path.join(file_dir_path, file_real_name)

        # 保存到本地
        with open(file_path, 'wb+') as f:
            for chunk in image.chunks():
                f.write(chunk)

        db_goods.image = os.path.join(dir_name, file_real_name)

    db_goods.title = title
    db_goods.desc = desc
    db_goods.price = price
    db_goods.seller_id = seller_info['id']
    db_goods.category_id = category_id
    db_goods.save()

    messages.success(request, 'Update Success')
    return redirect('/seller/good_list/')


def seller_good_add(request):
    """商品-添加"""

    # ———— 检查登录 ————
    if 'seller' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    seller_info = request.session['seller']

    if request.method == 'GET':  # 获取页面
        return render(request,
                      'seller/good_add.html',
                      context={
                          'li_category': GoodsCategory.objects.order_by('-id')
                      })

    # 添加操作
    params = request.POST
    title = params.get('title')
    desc = params.get('desc')
    price = params.get('price')
    category_id = params.get('category')

    try:
        price = float(price)
    except:
        messages.error(request, 'Illegal Price')
        return redirect('/seller/good_add')

    image = request.FILES.get('image_file')

    # 校验
    if not all([title, desc, price, image]):
        messages.error(request, 'Illegal Params')
        return redirect('/seller/good_add')

    # 保存文件
    dir_name = 'seller/goods/'
    file_dir_path = os.path.join(MEDIA_URL, dir_name)
    if not os.path.exists(file_dir_path):
        os.makedirs(file_dir_path)

    # 文件路径
    tmp = str(int(time.time()))
    file_real_name = f'{tmp}-{image.name}'
    file_path = os.path.join(file_dir_path, file_real_name)

    # 保存到本地
    with open(file_path, 'wb+') as f:
        for chunk in image.chunks():
            f.write(chunk)

    # 添加数据库
    Goods.objects.create(
        title=title,
        desc=desc,
        price=price,
        image=os.path.join(dir_name, file_real_name),
        seller_id=seller_info['id'],
        category_id=category_id
    )

    messages.success(request, 'Add Success')
    return redirect('/seller/good_list/')


def seller_good_list(request):
    """商品-列表"""

    page = int(request.GET.get('page', 1))
    limit = 10

    start = (page - 1) * limit

    # ———— 检查登录 ————
    if 'seller' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    seller_info = request.session['seller']

    res_goods = Goods.objects.filter(seller_id=seller_info['id']).order_by('-id')
    count_goods = res_goods.count()
    li_goods = res_goods[start:start + limit]

    if request.method == 'GET':  # 获取页面
        return render(request,
                      'seller/good_list.html',
                      context={
                          'goods': {
                              'count': count_goods,
                              'list': li_goods
                          }
                      })


def seller_service_list(request):
    """服务列表"""

    # ———— 检查登录 ————
    if 'seller' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    seller_info = request.session['seller']

    page = int(request.GET.get('page', 1))
    limit = 10

    start = (page - 1) * limit

    res_service = Services.objects.filter(seller_id=seller_info['id']).order_by('-id')

    return render(request,
                  'seller/service_list.html',
                  context={
                      'service': {
                          'count': res_service.count(),
                          'list': res_service[start:start + limit]
                      }
                  })


def seller_service_add(request):
    """服务-添加"""

    # ———— 检查登录 ————
    if 'seller' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    seller_info = request.session['seller']

    if request.method == 'GET':  # 获取页面
        return render(request,
                      'seller/service_add.html',
                      context={
                          # 'li_category': GoodsCategory.objects.order_by('-id')
                      })

    # 添加操作
    params = request.POST
    title = params.get('title')
    desc = params.get('desc')
    price = params.get('price')
    category_name = params.get('category_name')

    try:
        price = float(price)
    except:
        messages.error(request, 'Illegal Price')
        return redirect('/seller/good_add')

    image = request.FILES.get('image_file')

    # 校验
    if not all([title, desc, price, image]):
        messages.error(request, 'Illegal Params')
        return redirect('/seller/service_add')

    # 保存文件
    dir_name = 'seller/services/'
    file_dir_path = os.path.join(MEDIA_URL, dir_name)
    if not os.path.exists(file_dir_path):
        os.makedirs(file_dir_path)

    # 文件路径
    tmp = str(int(time.time()))
    file_real_name = f'{tmp}-{image.name}'
    file_path = os.path.join(file_dir_path, file_real_name)

    # 保存到本地
    with open(file_path, 'wb+') as f:
        for chunk in image.chunks():
            f.write(chunk)

    # 添加数据库
    Services.objects.create(
        title=title,
        desc=desc,
        price=price,
        image=os.path.join(dir_name, file_real_name),
        seller_id=seller_info['id'],
        category_name=category_name,
    )

    messages.success(request, 'Add Success')
    return redirect('/seller/service_list/')


def seller_service_update(request, pk):
    """服务-修改"""

    # ———— 检查登录 ————
    if 'seller' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    seller_info = request.session['seller']

    if request.method == 'GET':  # 获取页面

        service = Services.objects.filter(pk=pk).first()
        if not service:
            messages.error(request, 'Service Not Exist')
            return redirect(('/seller/service_list/'))

        return render(request,
                      'seller/service_update.html',
                      context={
                          'service': service
                      })

    # 修改操作
    params = request.POST
    title = params.get('title')
    desc = params.get('desc')
    price = params.get('price')

    image = request.FILES.get('image_file')

    # 校验
    if not all([title, desc, price]):
        messages.error(request, 'Illegal Params')
        return redirect(f'/seller/service_update/{pk}')

    # 查询 pk
    db_service = Services.objects.filter(pk=pk).first()

    if image:
        # 保存文件
        dir_name = 'seller/services/'
        file_dir_path = os.path.join(MEDIA_URL, dir_name)
        if not os.path.exists(file_dir_path):
            os.makedirs(file_dir_path)

        # 文件路径
        tmp = str(int(time.time()))
        file_real_name = f'{tmp}-{image.name}'
        file_path = os.path.join(file_dir_path, file_real_name)

        # 保存到本地
        with open(file_path, 'wb+') as f:
            for chunk in image.chunks():
                f.write(chunk)

        db_service.image = os.path.join(dir_name, file_real_name)

    db_service.title = title
    db_service.desc = desc
    db_service.price = price
    db_service.seller_id = seller_info['id']
    db_service.save()

    messages.success(request, 'Update Success')
    return redirect('/seller/service_list/')


def seller_service_del(request, pk):
    """服务-删除"""

    # ———— 检查登录 ————
    if 'seller' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    seller_info = request.session['seller']

    db_service = Services.objects.filter(
        pk=pk,
        seller_id=seller_info['id']
    ).first()

    if not db_service:
        messages.error(request, 'Service Not Exist')
        return redirect('/seller/service_list/')

    # 删除
    db_service.delete()

    messages.success(request, 'Delete Success')
    return redirect('/seller/service_list/')


def service_booking_status_update(request):
    """服务-预约-订单-状态-修改"""

    if 'seller' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')

    booking_id = request.POST.get('booking_id')
    status = int(request.POST.get('status'))

    # 修改
    Bookings.objects.filter(pk=booking_id).update(
        status=status
    )
    messages.success(request, 'Successfully Update Status')
    return redirect('/seller/service_bookings_list/')


def seller_service_bookings_list(request):
    """服务-预约-订单-列表"""

    # ———— 检查登录 ————
    if 'seller' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    seller_info = request.session['seller']

    page = int(request.GET.get('page', 1))
    limit = 10

    start = (page - 1) * limit

    res_service_bookings = Bookings.objects.filter(seller_id=seller_info['id']).order_by('-id')

    return render(request,
                  'seller/service_bookings_list.html',
                  context={
                      'bookings': {
                          'count': res_service_bookings.count(),
                          'list': [
                              item.get_bookings_info()
                              for item in res_service_bookings[start:start + limit]
                          ],
                          'choices_status': LI_BOOKINGS_STATUS
                      }
                  })


def good_orders_status_update(request):
    """商品-订单-状态修改"""

    if 'seller' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')

    order_id = request.POST.get('order_id')
    status = int(request.POST.get('status'))

    # 修改
    Order.objects.filter(pk=order_id).update(
        status=status
    )
    messages.success(request, 'Successfully Update Status')
    return redirect('/seller/good_orders_list/')


def good_orders_list(request):
    """商品-购买-订单-列表"""

    if 'seller' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    seller_info = request.session['seller']
    db_seller = Seller.objects.filter(pk=seller_info['id']).first()

    # keyword = request.GET.get('keyword', '')
    page = int(request.GET.get('page', 1))
    limit = 10

    start = (page - 1) * limit

    res_orders = Order.objects.filter(seller_id=seller_info['id']).order_by('-id')

    return render(request,
                  'seller/good_orders_list.html',
                  context={
                      'orders': {
                          'count': res_orders.count(),
                          'list': [
                              item.order_info()
                              for item in res_orders[start:start + limit]
                          ],
                          'choices_status': LI_ORDER_STATUS
                      }
                  })
