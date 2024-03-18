from django.urls import path

from . import views, views_user, views_seller

urlpatterns = [

    # ———— 用户 ————
    path('', views.index, name='index'),  # 首页
    path('shop/', views.shop, name='shop'),  # 店铺-列表
    path('services/', views.services, name='services'),  # 服务-列表
    path('shop_details/<pk>', views.shop_details,name='shop_details'),  # 店铺-详情
    path('forum/', views.forum, name='forum'),  # 论坛
    path('forum/post_message/', views.post_message, name='post_message'),
    path('community_list/', views.community_list, name='community_list'),  # 社区-列表
    path('community_details/<pk>', views.community_details, name='community_details'),  # 社区-列表
    path('community_send/', views.community_send, name='community_send'),  # 社区-发表
    path('community_editor_image_upload/', views.community_editor_image_upload,name='community_editor_image_upload'),  # 社区-富文本-图片上传
    path('our_team/', views.our_team, name='our_team'),  # 关于我们

    path('user/register/', views_user.user_register, name='user_register'),  # 注册
    path('user/login/', views_user.login, name='login'),  # 登录
    path('user/logout/', views_user.user_logout, name='user_logout'),  # 注销

    path('account/', views_user.account, name='account'),  # 个人主页
    path('user_update/', views_user.user_update, name='user_update'),  # 账户
    path('pet_update/', views_user.pet_update, name='pet_update'),  # 宠物-修改
    path('pet_add/', views_user.pet_add, name='pet_add'),  # 宠物-修改

    # 购物车
    path('cart_add/', views_user.cart_add, name='cart_add'),  # 购物车-添加
    path('cart_del_jq/<pk>', views_user.cart_del_jq, name='cart_del_jq'),  # 购物车-删除
    path('cart_update_jq/<pk>', views_user.cart_update_jq, name='cart_update_jq'),  # 购物车-修改
    path('cart_list/', views_user.cart_list, name='cart_list'),  # 购物车-列表
    path('cart_list_jq/', views_user.cart_list_jq, name='cart_list_jq'),  # 购物车-列表

    # 收货信息
    path('delivery_add/', views_user.delivery_add, name='delivery_add'),  # 收货信息-添加
    path('delivery_update/', views_user.delivery_update, name='delivery_update'),  # 地址-修改

    path('checkout/', views_user.checkout, name='checkout'),  # 结算
    path('order/', views_user.order),  # 订单-列表/下单
    path('order_comment/', views_user.order_comment),  # 订单-评论

    # 服务
    path('service_booking/<pk>', views_user.service_booking),  # 服务-预约-渲染/下单
    path('bookings/', views_user.bookings_list),  # 我的预约

    # ———— 卖家 ————
    path('seller/', views_seller.seller_index,name='seller_index'),  # 卖家主页
    path('seller/register/', views_seller.seller_register,name='seller_register'),  # 注册
    path('seller/login/', views_seller.seller_login),  # 登录
    path('seller/seller_account/', views_seller.seller_account),  # 账户
    path('seller_update/', views_seller.seller_update),  # 更新账户
    path('seller/logout/', views_seller.seller_logout),  # 注销

    # 商品
    path('seller/good_list/', views_seller.seller_good_list),  # 商品列表
    path('seller/good_add/', views_seller.seller_good_add),  # 添加商品
    path('seller/good_update/<pk>', views_seller.seller_good_update),  # 添加商品
    path('seller/good_del/<pk>', views_seller.seller_good_del),  # 添加商品

    path('seller/good_orders_list/', views_seller.good_orders_list),  # 商品-订单-列表
    path('seller/good_orders_status_update/', views_seller.good_orders_status_update),  # 商品-订单-状态修改

    # 服务
    path('seller/service_list/', views_seller.seller_service_list),  # 商品-列表
    path('seller/service_add/', views_seller.seller_service_add),  # 服务-添加
    path('seller/service_update/<pk>', views_seller.seller_service_update),  # 添加商品
    path('seller/service_del/<pk>', views_seller.seller_service_del),  # 添加商品

    path('seller/service_bookings_list/', views_seller.seller_service_bookings_list),  # 预约-订单-列表
    path('seller/service_booking_status_update/', views_seller.service_booking_status_update),  # 预约-订单-列表

    # API
    path('api/chatbot/', views.chatbot_request, name='chatbot_request'),
]
