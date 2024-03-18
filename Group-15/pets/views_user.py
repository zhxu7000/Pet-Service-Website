import json
import os

from django.contrib import messages
from django.db.models import Q, Sum, F
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from main.settings import MEDIA_URL
from pets.models import User, Pet, Cart, Delivery, Order, Seller, OrderComment, Services, Bookings


def login(request):
    """登录"""

    if request.method == 'GET':  # 注册页面渲染
        return render(request,
                      'user/login.html',
                      context={})

    # 登录操作
    params = request.POST
    account = params.get('account')
    password = params.get('password')

    if not all([account, password]):
        messages.error(request, 'Illegal Params')
        return redirect('/user/login')

    db_user = User.objects.filter(
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
    if not db_user:
        messages.error(request, 'Account Or Password Error')
        return redirect('/user/login')

    # 登录成功
    request.session['user'] = db_user.get_user_info()
    messages.success(request, 'Login Success !')
    return redirect('/')


def user_logout(request):
    """用户-注销"""

    # 清楚session
    if 'user' in request.session:
        del request.session['user']

    # 重定向到登录
    messages.success(request, 'Logout...')
    return redirect('/user/login')


def user_register(request):
    """注册"""

    if request.method == 'GET':  # 注册页面渲染
        return render(request,
                      'user/register.html',
                      context={})

    # 注册操作
    params = request.POST

    username = params.get('username', '')
    password = params.get('password', '')
    email = params.get('email', '')
    age = params.get('age', '')

    name = params.get('name', '')
    breed = params.get('breed', '')
    weight = params.get('weight', '')
    hair = params.get('hair', '')
    food_preference = params.get('food_preference', '')
    temperament = params.get('temperament', '')

    photo = request.FILES.get('photo', '')

    # 校验
    if not all([username, password, email, age, name, photo]):
        messages.error(request, 'Illegal Params')
        return redirect('/user/register')

    # 查看用户名是否存在
    if User.objects.filter(username=username).first():
        messages.error(request, 'Username Already Exists')
        return redirect('/user/register')

    # ———— 创建用户 ————
    db_user = User.objects.create(
        username=username,
        password=password,
        email=email,
        age=age
    )

    # ———— 创建宠物 ————
    # 保存文件
    dir_name = 'user/pets/'
    file_dir_path = os.path.join(MEDIA_URL, dir_name)
    if not os.path.exists(file_dir_path):
        os.makedirs(file_dir_path)

    # 文件路径
    file_real_name = f'{username}-{name}.jpg'
    file_path = os.path.join(file_dir_path, file_real_name)

    # 保存到本地
    with open(file_path, 'wb+') as f:
        for chunk in photo.chunks():
            f.write(chunk)

    Pet.objects.create(
        owner=db_user,
        name=name,
        breed=breed,
        weight=weight,
        hair=hair,
        food_preference=food_preference,
        temperament=temperament,
        photo=os.path.join(dir_name, file_real_name)
    )

    messages.success(request, 'Register Successfully')
    return redirect('/user/login')


# ———————— 购物车 ————————

def cart_add(request):
    """添加到购物车"""

    # ———— 检查登录 ————
    if 'user' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    user_info = request.session['user']
    user_id = user_info['id']

    if request.method == 'POST':
        params = request.POST

        good_id = int(params.get('id'))
        count = int(params.get('count'))
        redirect_page = params.get('redirect_page')

        # 判断是否已经存在，是则 +1，否则添加
        db_cart_exist = Cart.objects.filter(goods_id=good_id, user_id=user_id).first()
        if db_cart_exist:  # 存在，+1
            db_cart_exist.count += 1
            db_cart_exist.save()
        else:  # 不存在，添加
            # 添加到 购物车
            Cart.objects.create(
                user_id=user_id,
                goods_id=good_id,
                count=count
            )

        messages.success(request, 'Successfully Add To Cart')
        if redirect_page:
            return redirect(redirect_page)

        return redirect('/cart_list/')


@csrf_exempt
def cart_del_jq(request, pk):
    """购物车-删除-ajax版"""
    # ———— 检查登录 ————
    if 'user' not in request.session:
        return JsonResponse({'success': False, 'msg': 'Please Login...'})

    # 删除
    Cart.objects.filter(pk=pk).delete()

    return JsonResponse({'success': True, 'msg': 'Successfully Delete!'})


@csrf_exempt
def cart_update_jq(request, pk):
    """修改-购物车数量-ajax版"""

    # ———— 检查登录 ————
    if 'user' not in request.session:
        return JsonResponse({'success': False, 'msg': 'Please Login...'})

    count = int(request.GET.get('count'))

    if count == 0:  # 删除
        Cart.objects.filter(pk=pk).delete()
        return JsonResponse({'success': True, 'msg': 'Successfully Delete!'})

    # 修改
    Cart.objects.filter(pk=pk).update(
        count=count
    )
    return JsonResponse({'success': True, 'msg': 'Successfully Update Count!'})


def cart_list(request):
    """购物车-列表"""

    # ———— 检查登录 ————
    if 'user' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    user_info = request.session['user']
    db_user = User.objects.filter(pk=user_info['id']).first()

    return render(request,
                  'user/cart_list.html',
                  context={
                      **get_cart_bill(user_info['id']),
                      'cart_info': db_user.get_cart_info()
                  })


@csrf_exempt
def cart_list_jq(request):
    # ———— 检查登录 ————
    if 'user' not in request.session:
        return JsonResponse({'success': False, 'msg': 'Please Login...'})

    user_info = request.session['user']
    db_user = User.objects.filter(pk=user_info['id']).first()

    return JsonResponse({
        'success': True,
        'data': {
            **get_cart_bill(user_info['id']),
        },
    })


def get_user_total_bill_price(user_id):
    # 用户-总账单金额
    total_amount = Cart.objects.filter(
        user_id=user_id
    ).aggregate(
        total=Sum(
            F('count') * F('goods__price')
        )
    )
    return float(total_amount['total'] or 0)


def get_cart_bill(user_id, seller_id=None):
    """获取 所有购物车商品，并计算总金额"""

    res = Cart.objects.filter(user_id=user_id)

    if seller_id:
        res = res.filter(goods__seller_id=seller_id)

    li_cart = res.order_by('-created_at').all()

    if not li_cart:
        return {
            'li_cart': [],
            'total_amount': 0
        }

    # 总金额
    total_amount = res.aggregate(
        total=Sum(
            F('count') * F('goods__price')
        )
    )

    return {
        'li_cart': [
            item.cart_info()
            for item in li_cart
        ],
        'total_amount': float(total_amount['total'] or 0)
    }


def delivery_add(request):
    """收货信息-添加"""

    # ———— 检查登录 ————
    if 'user' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    user_info = request.session['user']

    params = request.POST
    name = params.get('name')
    phone = params.get('phone')
    email = params.get('email')
    addr = params.get('addr')
    notes = params.get('notes')

    redirect_page = params.get('redirect_page')

    # 添加到 地址
    Delivery.objects.create(
        user_id=user_info['id'],
        name=name,
        phone=phone,
        email=email,
        addr=addr,
        notes=notes
    )
    messages.success(request, 'Successfully Add A Delivery Info')

    if redirect_page:
        return redirect(redirect_page)
    return redirect('/checkout/')


def _get_split_order_info_by_cart(user_id):
    """按照卖家不同，拆分 生成 订单"""

    # 找出 当前用户-购物车-所有商家
    li_seller = Cart.objects.filter(
        user_id=user_id  # 筛选 当前用户
    ).values('goods__seller_id').distinct()

    li_order = []
    for seller_item in li_seller:  # 按照 卖家，拆分订单
        seller_id = seller_item['goods__seller_id']

        db_seller = Seller.objects.filter(pk=seller_id).first()

        # 查找所有购物车商品
        li_order.append(
            {
                'seller': db_seller.get_seller_info(),
                'orders': get_cart_bill(user_id, seller_id)
            }
        )
    return li_order


def checkout(request):
    """购物车-结算"""

    # ———— 检查登录 ————
    if 'user' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    user_info = request.session['user']
    user_id = user_info['id']

    # 获取所有的 收货信息
    li_delivery = Delivery.objects.filter(
        user_id=user_id
    ).order_by('-id')

    # 拆分订单，需要按照不同 卖家，拆分多个订单
    li_orders = _get_split_order_info_by_cart(user_id)

    if not li_orders:
        messages.error(request, 'Error: No Goods In Cart')
        return redirect('/shop/')

    return render(request,
                  'user/checkout.html',
                  context={
                      'li_orders': li_orders,  # 订单
                      'total_price': get_user_total_bill_price(user_id),  # 总支付金额
                      'li_delivery': li_delivery
                  })


def account(request):
    """个人主页"""

    # ———— 检查登录 ————
    if 'user' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    user_info = request.session['user']
    user_id = user_info['id']
    db_user = User.objects.filter(pk=user_id).first()

    return render(request,
                  'user/account.html',
                  context={
                      # 用户-订单
                      'orders': db_user.get_user_orders(),
                      # 用户-预约
                      'bookings': db_user.get_user_bookings(),
                      # 用户-宠物
                      'li_pets': db_user.get_user_pets(),
                      # 用户-地址
                      'li_addr': db_user.get_user_addr(),
                      # 用户-购物车信息
                      'cart_info': db_user.get_cart_info()
                  })


def user_update(request):
    """用户信息-修改"""

    # ———— 检查登录 ————
    if 'user' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    user_info = request.session['user']
    user_id = user_info['id']
    db_user = User.objects.filter(pk=user_id).first()

    if request.method == 'POST':
        params = request.POST

        password = params.get('password')
        ck_password = params.get('ck_password')
        email = params.get('email')
        age = params.get('age')

        if password != ck_password:
            messages.error(request, 'Confirm password inconsistency！')
            return redirect('/account/')

        db_user.email = email
        db_user.age = age

        if password:  # 有密码才修改
            db_user.password = password

        db_user.save()

        # 覆盖 session
        request.session['user'] = db_user.get_user_info()

        messages.success(request, 'Successfully Update')
        return redirect('/account/')


def delivery_update(request):
    """发货信息修改"""

    # ———— 检查登录 ————
    if 'user' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    user_info = request.session['user']
    user_id = user_info['id']
    db_user = User.objects.filter(pk=user_id).first()

    if request.method == 'POST':
        params = request.POST
        pk = params.get('id')

        name = params.get('name')
        phone = params.get('phone')
        email = params.get('email')
        addr = params.get('addr')
        notes = params.get('notes')

        # 修改
        Delivery.objects.filter(pk=pk).update(
            name=name,
            phone=phone,
            email=email,
            addr=addr,
            notes=notes
        )
        messages.success(request, 'Successfully Update')
        return redirect('/account/')


def pet_update(request):
    """宠物信息-修改"""

    # ———— 检查登录 ————
    if 'user' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    user_info = request.session['user']
    user_id = user_info['id']
    db_user = User.objects.filter(pk=user_id).first()

    if request.method == 'POST':
        params = request.POST
        pk = params.get('id')
        # name = params.get('name')
        breed = params.get('breed')
        weight = params.get('weight')
        hair = params.get('hair')
        food_preference = params.get('food_preference')
        temperament = params.get('temperament')

        Pet.objects.filter(pk=pk).update(
            # name=name,
            breed=breed,
            weight=weight,
            hair=hair,
            food_preference=food_preference,
            temperament=temperament,
        )
        messages.success(request, 'Successfully Update')
        return redirect('/account/')


def pet_add(request):
    """添加-宠物"""

    # ———— 检查登录 ————
    if 'user' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    user_info = request.session['user']
    user_id = user_info['id']
    db_user = User.objects.filter(pk=user_id).first()

    if request.method == 'POST':
        params = request.POST
        name = params.get('name', '')
        breed = params.get('breed', '')
        weight = params.get('weight', '')
        hair = params.get('hair', '')
        food_preference = params.get('food_preference', '')
        temperament = params.get('temperament', '')

        photo = request.FILES.get('photo', '')

        # ———— 创建宠物 ————
        # 保存文件
        dir_name = 'user/pets/'
        file_dir_path = os.path.join(MEDIA_URL, dir_name)
        if not os.path.exists(file_dir_path):
            os.makedirs(file_dir_path)

        # 文件路径
        file_real_name = f'{db_user.username}-{name}.jpg'
        file_path = os.path.join(file_dir_path, file_real_name)

        # 保存到本地
        with open(file_path, 'wb+') as f:
            for chunk in photo.chunks():
                f.write(chunk)

        Pet.objects.create(
            owner=db_user,
            name=name,
            breed=breed,
            weight=weight,
            hair=hair,
            food_preference=food_preference,
            temperament=temperament,
            photo=os.path.join(dir_name, file_real_name)
        )
        return redirect('/account/')


def order(request):
    """订单/下单"""

    # ———— 检查登录 ————
    if 'user' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    user_info = request.session['user']
    user_id = user_info['id']
    db_user = User.objects.filter(pk=user_id).first()

    # ———— 订单-列表 ————
    if request.method == 'GET':
        page = int(request.GET.get('page', 1))
        limit = 10
        start = (page - 1) * limit

        res_orders = Order.objects.filter(user_id=user_id)

        li_orders = [
            item.order_info()
            for item in res_orders[start:start + limit]
        ]
        count_orders = res_orders.count()

        return render(request,
                      'user/order_list.html',
                      context={
                          # 获取 用户-订单
                          'orders': {
                              'list': li_orders,
                              'count': count_orders
                          }
                      })

    # ———— 下单操作 ————
    if request.method == 'POST':
        delivery_id = request.POST.get('delivery_id')
        if not delivery_id:
            messages.error(request, 'Please Chose A Delivery Info!')
            return redirect('/checkout/')
        db_delivery = Delivery.objects.filter(pk=delivery_id).first()

        # 获取 拆分的订单
        li_orders = _get_split_order_info_by_cart(user_id)
        # total_price = get_user_total_bill_price(user_id)  # 总金额

        if not li_orders:
            messages.error(request, 'Error: No Goods In Cart')
            return redirect('/shop/')

        for order_item in li_orders:
            seller_id = order_item['seller']['id']

            li_cart_info = order_item['orders']['li_cart']
            total_price = order_item['orders']['total_amount']

            # 添加订单
            Order.objects.create(
                user_id=user_id,
                seller_id=seller_id,
                goods_info_json_str=json.dumps(li_cart_info, ensure_ascii=False),
                delivery_info_json_str=json.dumps(db_delivery.delivery_info(), ensure_ascii=False),
                total_price=total_price
            )

        # 清空购物车
        Cart.objects.filter(
            user_id=user_id
        ).delete()

        # 返回 下单成功页面
        messages.success(request, 'Successfully Order')
        return redirect('/order/')


def order_comment(request):
    """订单评价"""

    # ———— 检查登录 ————
    if 'user' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    user_info = request.session['user']
    user_id = user_info['id']
    db_user = User.objects.filter(pk=user_id).first()

    if request.method == 'GET':
        order_id = int(request.GET.get('oid'))
        goods_id = int(request.GET.get('gid'))

        db_order = Order.objects.filter(pk=order_id).first()
        if not db_order:
            messages.success(request, 'Error: id not exist')
            return redirect('/order/')

        # 找出交易快照
        li_goods_info = json.loads(db_order.goods_info_json_str)
        for good_pay_info in li_goods_info:
            if good_pay_info['goods']['id'] == goods_id:  # 找到 需要评论的

                # db_goods = Goods.objects.filter(pk=goods_id).first()

                # 找出 当前用户-历史评论
                li_comment = OrderComment.objects.filter(
                    user_id=user_id,  # 筛选当前用户
                    goods_id=goods_id,  # 筛选当前商品
                ).order_by('-id')[:10]

                return render(request,
                              'user/order_comment.html',
                              context={
                                  'order': db_order,
                                  'good_pay_info': good_pay_info,
                                  'li_comment': li_comment
                              })

        messages.success(request, 'Error: id not exist')
        return redirect('/order/')

    if request.method == 'POST':
        params = request.POST

        good_id = params.get('good_id')
        order_id = params.get('order_id')
        content = params.get('content')

        OrderComment.objects.create(
            user_id=user_id,
            goods_id=good_id,
            order_id=order_id,
            content=content
        )
        messages.success(request, 'Successfully Comment')
        return redirect(f'/order_comment/?oid={order_id}&gid={good_id}')


def service_booking(request, pk):
    """服务-预约"""

    # ———— 检查登录 ————
    if 'user' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    user_info = request.session['user']
    user_id = user_info['id']
    db_user = User.objects.filter(pk=user_id).first()

    db_service = Services.objects.filter(id=pk).first()
    if not db_service:
        messages.error(request, 'Services Not Found')
        return redirect('/services/')

    if request.method == 'GET':
        return render(request,
                      'user/service_booking.html',
                      context={
                          'service': db_service,
                          'li_my_pets': db_user.get_user_pets()
                      })

    params = request.POST

    appointment_time = params.get('appointment_time')
    pet_id = params.get('pet_id')

    db_pet = Pet.objects.filter(pk=pet_id).first()

    # 保存 预约订单
    Bookings.objects.create(
        user_id=user_id,
        seller_id=db_service.seller.id,
        appointment_time=appointment_time,
        service_info_json_str=json.dumps(db_service.get_service_info(), ensure_ascii=False),
        pet_info_json_str=json.dumps(db_pet.get_pet_info(), ensure_ascii=False),
        total_price=float(db_service.price)
    )

    messages.success(request, 'Successfully Book')
    return redirect('/services/')


def bookings_list(request):
    """我的预约"""

    # ———— 检查登录 ————
    if 'user' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    user_info = request.session['user']
    user_id = user_info['id']
    db_user = User.objects.filter(pk=user_id).first()

    page = int(request.GET.get('page', 1))
    limit = 10
    start = (page - 1) * limit

    res_bookings = Bookings.objects.filter(user_id=user_id).order_by('-id')

    # ———— 预约-列表 ————
    return render(request,
                  'user/booking_list.html',
                  context={
                      # 获取 用户-预约
                      'bookings': {
                          'count': res_bookings.count(),
                          'list': [
                              item.get_bookings_info()
                              for item in res_bookings[start:start + limit]
                          ]
                      }
                  })
