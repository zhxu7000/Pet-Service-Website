import os
import time

from django.contrib import messages
from django.db.models import Q
import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.formats import date_format
# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from main.settings import MEDIA_URL
from pets.models import Goods, OrderComment, User, Services, Forum, Community, GoodsCategory
from django.shortcuts import render
from django.http import JsonResponse

def chatbot_request(request):
    user_message = request.GET.get('message', None)
    if not user_message:
        return JsonResponse({'error': 'Message not provided'}, status=400)

    access_token = "SXBUSFSNZIV3QCSBAIFYMG6HR7623HUX"  # 使用Server Access Token
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }

    response = requests.get(f'https://api.wit.ai/message?v=20201005&q={user_message}', headers=headers)
    if response.status_code != 200:
        return JsonResponse({'error': 'Failed to get response from chatbot'}, status=500)

    data = response.json()

    reply = data.get('text', 'Sorry, I did not understand that.')

    return JsonResponse({'reply': reply})

def our_team(request):
    return render(request,
                  'our_team.html',
                  context={})


def index(request):
    """index"""

    # ———— 查看是否登录 ————
    cart_info = {}
    if 'user' in request.session:  # 已登录
        user_info = request.session['user']
        db_user = User.objects.filter(pk=user_info['id']).first()
        cart_info = db_user.get_cart_info()

    # 最新商品列表
    li_goods = Goods.objects.order_by('-id')[:8]

    return render(request,
                  'index.html',
                  context={
                      'cart_info': cart_info,
                      # 最新商品列表
                      'li_goods': li_goods
                  })


def services(request):
    """服务列表"""

    # ———— 查看是否登录 ————
    cart_info = {}
    if 'user' in request.session:  # 已登录
        user_info = request.session['user']
        db_user = User.objects.filter(pk=user_info['id']).first()
        cart_info = db_user.get_cart_info()

    keyword = request.GET.get('keyword', '')
    category_name = request.GET.get('category_name', '')
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))

    start = (page - 1) * size
    end = start + size

    res = Services.objects.filter(
        Q(title__icontains=keyword)
        |
        Q(desc__icontains=keyword)
    )

    if category_name:
        res = res.filter(
            category_name=category_name
        )

    return render(request,
                  'services.html',
                  context={
                      'services': {
                          'count': res.count(),
                          'list': res.order_by('-id')[start:end]
                      },
                      'cart_info': cart_info
                  })


def shop(request):
    """shop"""

    # ———— 查看是否登录 ————
    cart_info = {}
    if 'user' in request.session:  # 已登录
        user_info = request.session['user']
        db_user = User.objects.filter(pk=user_info['id']).first()
        cart_info = db_user.get_cart_info()

    keyword = request.GET.get('keyword', '')
    category = request.GET.get('category', '')

    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))

    start = (page - 1) * size
    end = start + size

    res = Goods.objects.filter(
        Q(title__icontains=keyword)
        |
        Q(desc__icontains=keyword)
    )
    if category:
        res = res.filter(category__name=category)

    count_goods = res.count()
    li_goods = res.order_by('-id')[start:end]

    return render(request,
                  'shop.html',
                  context={
                      'count_goods': count_goods,
                      'li_goods': li_goods,
                      'cart_info': cart_info,
                      'li_category': GoodsCategory.objects.all()
                  })


def shop_details(request, pk):
    """商城-详情"""

    # ———— 查看是否登录 ————
    cart_info = {}
    if 'user' in request.session:  # 已登录
        user_info = request.session['user']
        db_user = User.objects.filter(pk=user_info['id']).first()
        cart_info = db_user.get_cart_info()

    # good_id = request.GET.get('id')

    db_good = Goods.objects.filter(pk=pk).first()

    # 找出 所有评论
    res_comment = OrderComment.objects.filter(
        goods_id=pk,  # 筛选当前商品
    ).order_by('-id')
    count_comment = res_comment.count()
    li_comment = res_comment[:20]

    return render(request,
                  'shop_details.html',
                  context={
                      'details': db_good,
                      'count_comment': count_comment,
                      'li_comment': li_comment,
                      # ———— 购物车按钮数据 ————
                      'cart_info': cart_info
                  })


def forum(request):
    """论坛"""

    if request.method == 'GET':  # 渲染论坛（免登陆）

        li_forum = Forum.objects.order_by('-id')[:50]

        return render(request,
                      'forum.html',
                      context={
                          'li_forum': li_forum
                      })

    # 发送评论（需要登录）
    # ———— 检查登录 ————
    if 'user' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    user_info = request.session['user']
    user_id = user_info['id']

    content = request.POST.get('content')
    to_user_id = request.POST.get('to_user_id', '')

    if not content:
        messages.error(request, 'Error: Content Is Null')
        return redirect('/forum')

    # 评论操作
    Forum.objects.create(
        from_user_id=user_id,
        to_user_id=to_user_id,
        content=content
    )
    messages.success(request, 'Successfully Send')
    return redirect('/forum')


def community_list(request):
    """社区（宠物故事分析）"""

    page = int(request.GET.get('page', 1))
    limit = 10

    start = (page - 1) * limit

    res = Community.objects.order_by('-id')

    return render(request,
                  'community_list.html',
                  context={
                      'community': {
                          'count': res.count(),
                          'list': res[start:start + limit]
                      }
                  })


def community_details(request, pk):
    """社区-详情"""

    db_community = Community.objects.filter(pk=pk).first()

    return render(request,
                  'community_details.html',
                  context={
                      'community': db_community
                  })


def community_send(request):
    """社区-发表"""

    # ———— 检查登录 ————
    if 'user' not in request.session:
        messages.error(request, 'Please Login...')
        return redirect('/user/login')
    user_info = request.session['user']

    # 渲染
    if request.method == 'GET':
        return render(request,
                      'community_send.html',
                      context={})

    # 发表
    title = request.POST.get('title')
    content = request.POST.get('content')

    # 保存 db
    Community.objects.create(title=title,
                             content=content,
                             user_id=user_info['id'])

    messages.success(request, 'Successfully Post')
    return redirect('/community_list')


@csrf_exempt
def community_editor_image_upload(request):
    """社区-富文本-图片-上传"""

    img_file = request.FILES.get('file')

    # 保存文件
    dir_name = 'community/editor/img/'
    file_dir_path = os.path.join(MEDIA_URL, dir_name)
    if not os.path.exists(file_dir_path):
        os.makedirs(file_dir_path)

    # 文件路径
    tmp = int(time.time())
    file_real_name = f'{tmp}-{img_file.name}'
    file_path = os.path.join(file_dir_path, file_real_name)

    # 保存到本地
    with open(file_path, 'wb+') as f:
        for chunk in img_file.chunks():
            f.write(chunk)

    img_path = os.path.join('/', MEDIA_URL, dir_name, file_real_name)

    return JsonResponse(
        {'location': img_path}
    )


@csrf_exempt
def post_message(request):
    if request.method == 'POST':
        # 从POST请求中获取数据
        content = request.POST.get('content', '')
        to_user_id = request.POST.get('to_user_id', None)

        # 检查用户是否已登录（使用与其他视图相同的方法）
        if 'user' not in request.session:
            return JsonResponse({'success': False, 'error_message': 'User not authenticated'})

        # 从会话中获取用户信息
        user_info = request.session['user']
        user_id = user_info['id']
        db_user = User.objects.filter(pk=user_id).first()

        # 创建新的消息对象
        message = Forum(
            from_user=db_user,
            content=content,
        )

        # 如果有接收用户ID，则设置接收用户
        if to_user_id:
            try:
                to_user_id = int(to_user_id)
                message.to_user_id = to_user_id
            except ValueError:
                return JsonResponse({'success': False, 'error_message': 'Invalid to_user_id'})

        # 保存消息到数据库
        message.save()

        # 获取用户名和时间等信息
        username = message.from_user.username
        created_at = date_format(message.created_at, "Y-m-d H:i:s")

        # 构建新消息的HTML片段（根据实际HTML结构进行调整）
        new_message_html = f"""<li class="list-group-item">
            <div class="msg_time">{created_at}</div>
            <div class="msg_block_control">
                <span class="msg_name">{username}</span>
                :
                <div class="msg_content">{message.content}</div>
            </div>
        </li>"""
        return JsonResponse({'success': True, 'html': new_message_html})

    return JsonResponse({'success': False, 'error_message': 'Invalid request method'})
