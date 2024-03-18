from django.test import TestCase
from .models import User, Pet,Seller,GoodsCategory,Goods
from django.contrib.auth.hashers import check_password
from django.core.files.uploadedfile import SimpleUploadedFile


class UserTestCase(TestCase):
    def setUp(self):
        User.objects.create(username="alice", password="alice123", email="alice@example.com", age=30)
        User.objects.create(username="bob", password="bob123", email="bob@example.com", age=35)

    def test_user_info(self):
        alice = User.objects.get(username="alice")
        bob = User.objects.get(username="bob")
        self.assertEqual(alice.get_user_info()['email'], 'alice@example.com')
        self.assertEqual(bob.get_user_info()['age'], 35)

class SellerTestCase(TestCase):
    def setUp(self):
        Seller.objects.create(username="seller1", password="pass123", email="seller1@example.com", age=40)

    def test_seller_info(self):
        seller1 = Seller.objects.get(username="seller1")
        self.assertEqual(seller1.get_seller_info()['email'], 'seller1@example.com')

class GoodsTestCase(TestCase):
    def setUp(self):
        seller = Seller.objects.create(username="goodseller", password="pass456", email="goodseller@example.com", age=45)
        category = GoodsCategory.objects.create(name="food")
        with open('/Users/xuzhenke/Desktop/Group-15/pets/test_image/test_image.jpg', 'rb') as img:
            image = SimpleUploadedFile(name='test_image.jpg', content=img.read(), content_type='image/jpg')
        Goods.objects.create(title="Widget", desc="A great widget", price=19.99, seller=seller, category=category,
                             image=image)
    def test_goods_info(self):
        widget = Goods.objects.get(title="Widget")
        self.assertEqual(widget.goods_info()['price'], 19.99)
        self.assertEqual(widget.category.name, 'food')  # 检查类别名称是否正确


