from django.contrib import admin

from pets.models import GoodsCategory, Goods, User, Pet, Seller, Cart, Order, Delivery, OrderComment, Services, \
    Bookings, Forum, Community


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'age', 'created_at')

    search_fields = ('username',)

    ordering = ('-id',)
    list_per_page = 10  # 满10条数据就自动分页


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'breed',
                    'weight', 'hair', 'food_preference', 'temperament',
                    'photo',)

    search_fields = ('name', 'breed',)
    list_filter = ('owner',)

    ordering = ('-id',)
    list_per_page = 10  # 满10条数据就自动分页


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'age', 'created_at')

    search_fields = ('username', 'email',)

    ordering = ('-id',)
    list_per_page = 10  # 满10条数据就自动分页


@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    list_display = ('title', 'desc', 'price', 'seller', 'image', 'category',
                    'created_at')

    search_fields = ('title',)

    list_filter = ('category',)  # 筛选字段

    ordering = ('-id',)  # 后台数据列表排序方式
    list_per_page = 10  # 满10条数据就自动分页


@admin.register(GoodsCategory)
class GoodsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

    search_fields = ('name',)

    ordering = ('-id',)  # 后台数据列表排序方式
    list_per_page = 10  # 满10条数据就自动分页


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'goods', 'count', 'created_at')

    # search_fields = ('title',)

    list_filter = ('user', 'goods')  # 筛选字段

    ordering = ('-id',)  # 后台数据列表排序方式
    list_per_page = 10  # 满10条数据就自动分页


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'seller', 'total_price',
                    'goods_info_json_str', 'delivery_info_json_str',
                    'created_at')

    # search_fields = ('title',)

    list_filter = ('user', 'seller')  # 筛选字段

    ordering = ('-id',)  # 后台数据列表排序方式
    list_per_page = 10  # 满10条数据就自动分页


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'phone',
                    'email', 'addr', 'notes')

    search_fields = ('name',)

    # list_filter = ('user', 'seller')  # 筛选字段

    ordering = ('-id',)  # 后台数据列表排序方式
    list_per_page = 10  # 满10条数据就自动分页


@admin.register(OrderComment)
class OrderCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'goods', 'order',
                    'content', 'created_at')

    search_fields = ('content',)

    list_filter = ('user', 'goods')  # 筛选字段

    ordering = ('-id',)  # 后台数据列表排序方式
    list_per_page = 10  # 满10条数据就自动分页


@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = ('title', 'desc', 'seller', 'category_name',
                    'image', 'created_at')

    search_fields = ('title', 'desc',)

    list_filter = ('category_name', 'seller')  # 筛选字段

    ordering = ('-id',)  # 后台数据列表排序方式
    list_per_page = 10  # 满10条数据就自动分页


@admin.register(Bookings)
class BookingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'seller', 'appointment_time', 'total_price',
                    'service_info_json_str', 'pet_info_json_str', 'created_at')

    # search_fields = ('title', 'desc',)

    # list_filter = ('category_name', 'seller')  # 筛选字段

    ordering = ('-id',)  # 后台数据列表排序方式
    list_per_page = 10  # 满10条数据就自动分页


@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'content', 'created_at')

    search_fields = ('content',)

    list_filter = ('from_user', 'to_user')  # 筛选字段

    ordering = ('-id',)  # 后台数据列表排序方式
    list_per_page = 10  # 满10条数据就自动分页


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'content', 'created_at')

    search_fields = ('title', 'content',)

    list_filter = ('user',)  # 筛选字段

    ordering = ('-id',)  # 后台数据列表排序方式
    list_per_page = 10  # 满10条数据就自动分页
