import datetime
import json
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
# Create your models here.
from django.db.models import Sum, F
from django.utils import timezone


class User(models.Model):
    username = models.CharField('username', max_length=255)
    password = models.CharField('password', max_length=255)
    email = models.CharField('email', max_length=255)
    age = models.IntegerField('age')
    created_at = models.DateTimeField('create time', default=timezone.now)
    last_login = models.DateTimeField('last login', null=True, blank=True)

    class Meta:
        verbose_name = verbose_name_plural = 'user'
        db_table = 'user'  # db table

    def __str__(self):
        return self.username
    
    def get_user_info(self):
        """用户信息"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'age': self.age,
            'created_at': str(self.created_at),
        }

    def get_user_pets(self):
        """用户-宠物"""

        return self.pet_set.order_by('-id').all()

    def get_user_addr(self):
        """用户-地址"""
        return self.delivery_set.order_by('-id').all()

    def get_user_orders(self):
        # 获取 用户的 最新5个订单
        res = Order.objects.filter(user_id=self.id)

        return {
            'count': res.count(),
            'list': [
                item.order_info()
                for item in res.order_by('-id')[:5]
            ]
        }

    def get_cart_info(self):
        """获取 购物车信息"""

        res = self.cart_set.order_by('-id')

        # 总金额
        total_amount = res.aggregate(
            total=Sum(
                F('count') * F('goods__price')
            )
        )

        return {
            'count': res.count(),
            'list': res[:10],
            'total': float(total_amount['total'] or 0)
        }

    def get_user_bookings(self):
        """获取 用户的最新5个预订"""

        res = Bookings.objects.filter(user_id=self.id)

        return {
            'count': res.count(),
            'list': [
                item.get_bookings_info()
                for item in res.order_by('-id')[:5]
            ]
        }


class Pet(models.Model):
    owner = models.ForeignKey(User, verbose_name='owner', on_delete=models.CASCADE)
    name = models.CharField('name', max_length=255)
    # age = models.IntegerField('age')

    breed = models.CharField('breed', max_length=255)  # 品种
    weight = models.DecimalField('weight', max_digits=10, decimal_places=2)  # 体重
    hair = models.CharField('hair', max_length=255)  # 发色
    food_preference = models.CharField('food_preference', max_length=255)  # 食物偏好
    temperament = models.CharField('temperament', max_length=255, default='')
    photo = models.ImageField('photo')

    class Meta:
        verbose_name = verbose_name_plural = 'pet'
        db_table = 'pet'  # db table

    def __str__(self):
        return self.name

    def get_pet_info(self):
        """宠物信息"""
        return {
            'name': self.name,
            'breed': self.breed,
            'weight': float(self.weight),
            'hair': self.hair,
            'food_preference': self.food_preference,
            'temperament': self.temperament,
            'photo': {
                'url': self.photo.url
            },
            'owner': self.owner.get_user_info()
        }


class Seller(models.Model):
    username = models.CharField('username', max_length=255)
    password = models.CharField('password', max_length=255)
    email = models.CharField('email', max_length=255)
    age = models.IntegerField('age')
    created_at = models.DateTimeField('create time', default=timezone.now)

    def save(self, *args, **kwargs):
            if not self.pk or 'password' in kwargs:  # When a user is created or a password is updated
                self.password = make_password(self.password)
            super().save(*args, **kwargs)

    def check_password(self, raw_password):
        """Verify that the supplied password matches the stored hash password"""
        return check_password(raw_password, self.password)


    class Meta:
        verbose_name = verbose_name_plural = 'seller'
        db_table = 'seller'  # db table

    def __str__(self):
        return self.username

    def get_seller_info(self):
        """卖家 信息"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'age': self.age,
            'created_at': str(self.created_at)
        }

    def get_seller_orders(self):
        # 获取 卖家的订单
        li_orders = Order.objects.filter(seller_id=self.id).order_by('-id')

        return [item.order_info() for item in li_orders]


class GoodsCategory(models.Model):
    name = models.CharField('name', max_length=255)

    class Meta:
        verbose_name = verbose_name_plural = 'goods category'
        db_table = 'goods_category'  # db table

    def __str__(self):
        return self.name


class Goods(models.Model):
    title = models.CharField('title', max_length=255)
    desc = models.TextField('desc')
    price = models.DecimalField('price', max_digits=10, decimal_places=2)
    seller = models.ForeignKey(Seller, verbose_name='seller', on_delete=models.CASCADE)
    image = models.ImageField('image')
    category = models.ForeignKey(GoodsCategory, verbose_name='category', on_delete=models.DO_NOTHING, default=None,
                                 db_constraint=False)
    created_at = models.DateTimeField('create time', default=timezone.now)

    class Meta:
        verbose_name = verbose_name_plural = 'goods'
        db_table = 'goods'  # db table

    def __str__(self):
        return self.title

    def goods_info(self):
        return {
            'id': self.id,
            'title': self.title,
            'desc': self.desc,
            'price': float(self.price),
            'image_path': self.image.url,
            'image': {
                'url': self.image.url,
            },
            'created_at': str(self.created_at),
            'seller': self.seller.get_seller_info()
        }


class Cart(models.Model):
    """购物车"""
    user = models.ForeignKey(User, verbose_name='user', on_delete=models.DO_NOTHING)
    goods = models.ForeignKey(Goods, verbose_name='goods', on_delete=models.DO_NOTHING)
    count = models.IntegerField('count')
    created_at = models.DateTimeField('create time', default=timezone.now)

    class Meta:
        verbose_name = verbose_name_plural = 'cart'
        db_table = 'cart'  # db table

    def single_amount(self):
        """单行金额"""
        return float(self.goods.price * self.count)

    def cart_info(self):
        """购物车-信息"""
        return {
            'id': self.id,
            'count': self.count,
            'created_at': str(self.created_at),
            'single_amount': self.single_amount(),
            'goods': self.goods.goods_info()
        }


LI_ORDER_STATUS = (
    (1, 'unshipped'),
    (2, 'in transit'),
    (3, 'arrival')
)


class Order(models.Model):
    """订单"""
    user = models.ForeignKey(User, verbose_name='user', on_delete=models.DO_NOTHING)
    seller = models.ForeignKey(Seller, verbose_name='seller', on_delete=models.DO_NOTHING, default=1)
    created_at = models.DateTimeField('create time', default=timezone.now)
    total_price = models.DecimalField('total_price', max_digits=10, decimal_places=2, default=0)

    # 商品-价格-数量 数组 快照
    #   [
    #       {
    #         "id": 20,
    #         "count": 1,
    #         "created_at": "2023-08-23 02:32:44.602999+00:00",
    #         "single_amount": 44.0,
    #         "goods": {
    #           "id": 9,
    #           "title": "44",
    #           "desc": "44",
    #           "price": 44.0,
    #           "image_path": "/media/seller/goods/1692607920-Image03.jpg",
    #           "image": {
    #             "url": "/media/seller/goods/1692607920-Image03.jpg"
    #           },
    #           "created_at": "2023-08-21 08:52:00.129289+00:00"
    #         }
    #       }
    #     ]
    goods_info_json_str = models.TextField('goods info')

    # 发货信息 json字符串
    #   { name:'', phone:'', addr:'', email:'', notes:'' }
    delivery_info_json_str = models.TextField('delivery info')

    status = models.IntegerField('status', choices=LI_ORDER_STATUS, default=1)

    class Meta:
        verbose_name = verbose_name_plural = 'order'
        db_table = 'order'  # db table

    def order_info(self):
        return {
            'id': self.id,
            'user': self.user.get_user_info(),
            'seller': self.seller.get_seller_info(),
            'goods_info': json.loads(self.goods_info_json_str),  # 快照数据
            'delivery_info': json.loads(self.delivery_info_json_str),  # 快照数据
            'created_at': datetime.datetime.strftime(self.created_at + datetime.timedelta(hours=8),
                                                     '%Y-%m-%d %H:%M:%S'),
            'total_price': self.total_price,
            'status': self.status,
            'status_display': self.get_status_display()
        }


class Delivery(models.Model):
    """收货信息"""
    user = models.ForeignKey(User, verbose_name='user', on_delete=models.DO_NOTHING, default=1)
    name = models.CharField('name', max_length=255)
    phone = models.CharField('phone', max_length=255)
    email = models.CharField('email', max_length=255)
    addr = models.TextField('addr')
    notes = models.TextField('notes')

    class Meta:
        verbose_name = verbose_name_plural = 'delivery'
        db_table = 'delivery'  # db table

    def delivery_info(self):
        """发货-地址"""
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'addr': self.addr,
            'notes': self.notes,
        }


class OrderComment(models.Model):
    """评价"""
    user = models.ForeignKey(User, verbose_name='user', on_delete=models.DO_NOTHING, default=1)
    goods = models.ForeignKey(Goods, verbose_name='goods', on_delete=models.DO_NOTHING)
    order = models.ForeignKey(Order, verbose_name='order', on_delete=models.DO_NOTHING)
    content = models.TextField('content')
    created_at = models.DateTimeField('create time', default=timezone.now)

    class Meta:
        verbose_name = verbose_name_plural = 'order comment'
        db_table = 'order_comment'  # db table


class Services(models.Model):
    """服务"""

    title = models.CharField('title', max_length=255)
    desc = models.TextField('desc')
    price = models.DecimalField('price', max_digits=10, decimal_places=2)
    seller = models.ForeignKey(Seller, verbose_name='seller', on_delete=models.CASCADE)
    image = models.ImageField('image')
    category_name = models.CharField('category name', max_length=255)
    created_at = models.DateTimeField('create time', default=timezone.now)

    class Meta:
        verbose_name = verbose_name_plural = 'services'
        db_table = 'services'  # db table

    def __str__(self):
        return self.title

    def get_service_info(self):
        """服务 基本信息"""
        return {
            'title': self.title,
            'desc': self.desc,
            'category_name': self.category_name,
            'price': float(self.price),
            'seller': self.seller.get_seller_info(),
            'image': {
                'url': self.image.url
            },
            'created_at': datetime.datetime.strftime(self.created_at + datetime.timedelta(hours=8),
                                                     '%Y-%m-%d %H:%M:%S')
        }


LI_BOOKINGS_STATUS = (
    (1, 'Successfully Booked'),
    (2, 'In progress'),
    (3, 'Order completion')
)


class Bookings(models.Model):
    """服务预约订单"""

    user = models.ForeignKey(User, verbose_name='user', on_delete=models.DO_NOTHING)
    seller = models.ForeignKey(Seller, verbose_name='seller', on_delete=models.DO_NOTHING, default=1)

    # 预约时间
    appointment_time = models.DateTimeField('appointment_time', default=None)

    # 预约服务信息
    service_info_json_str = models.TextField('service_info_json_str')

    # 服务价格
    total_price = models.DecimalField('total_price', max_digits=10, decimal_places=2, default=0)

    # 宠物信息
    pet_info_json_str = models.TextField('service_info_json_str')

    created_at = models.DateTimeField('create time', default=timezone.now)

    status = models.IntegerField('status', choices=LI_BOOKINGS_STATUS, default=1)

    class Meta:
        verbose_name = verbose_name_plural = 'bookings'
        db_table = 'bookings'  # db table

    def get_bookings_info(self):
        """预约-信息"""
        return {
            'id': self.id,
            'user': self.user.get_user_info(),
            'seller': self.seller.get_seller_info(),
            'service_info': json.loads(self.service_info_json_str),
            'pet_info': json.loads(self.pet_info_json_str),
            'created_at': datetime.datetime.strftime(self.created_at + datetime.timedelta(hours=8),
                                                     '%Y-%m-%d %H:%M:%S'),
            'status': self.status,
            'status_display': self.get_status_display()
        }


class Forum(models.Model):
    """论坛"""
    from_user = models.ForeignKey(User, verbose_name='from user', on_delete=models.DO_NOTHING,
                                  related_name='from_user')  # 发送消息的学生

    content = models.TextField(verbose_name='content')

    to_user = models.ForeignKey(User, verbose_name='to user', on_delete=models.DO_NOTHING,
                                related_name='to_user', null=True, blank=True)  # 被回复的学生，可以为空

    created_at = models.DateTimeField(verbose_name='created time', default=timezone.now)

    class Meta:
        verbose_name = verbose_name_plural = 'forum'
        db_table = 'forum'  # 数据库表名

    def __str__(self):
        return self.content


class Community(models.Model):
    """社区分享"""

    user = models.ForeignKey(User, verbose_name='user', on_delete=models.DO_NOTHING)

    title = models.CharField('title', max_length=255, default='')
    content = models.TextField('content')

    created_at = models.DateTimeField('create time', default=timezone.now)

    class Meta:
        verbose_name = verbose_name_plural = 'community'
        db_table = 'community'  # db table
