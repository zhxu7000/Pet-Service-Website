from django.test import TestCase, Client
from .models import User,Seller
from django.urls import reverse
from django.contrib.auth import authenticate, login

class SellerRegisterTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('seller_register')  

    def test_register_success(self):
        response = self.client.post(self.register_url, {
            'username': 'new_user',
            'password': 'password123',
            'confirm_password': 'password123',
            'email': 'new_user@example.com',
            'age': '25'
        })
        self.assertEqual(response.status_code, 302)  # Expect to redirect to the login page
        self.assertTrue(Seller.objects.filter(username='new_user').exists())

    def test_register_with_missing_fields(self):
        response = self.client.post(self.register_url, {
            'username': 'new_user',
            'password': 'password123',
            'confirm_password': 'password123',
            # 'email': 'new_user@example.com',
            'age': '25'
        })
        self.assertEqual(response.status_code, 302)  # 期望重定向到注册页面
        self.assertFalse(Seller.objects.filter(username='new_user').exists())


class SellerLoginTestCase(TestCase):
    def setUp(self):
        self.seller = Seller.objects.create(
            username="testuser", 
            password="password", 
            email="test@example.com",
            age=30)
        
    def test_login_with_username(self):
        response = self.client.post('/user/login', {'account': 'testuser', 'password': 'password'})
        self.assertRedirects(response, '/user/login/', status_code=301, target_status_code=200)

    def test_login_with_email(self):
        response = self.client.post('/user/login', {'account': 'test@example.com', 'password': 'password'})
        self.assertRedirects(response, '/user/login/', status_code=301, target_status_code=200)



class SellerUpdateTestCase(TestCase):
    def setUp(self):
        # 创建一个seller实例供测试使用
        self.seller = Seller.objects.create(username='testuser', email='test@example.com', password='oldpassword',age=30)

    def test_update_info(self):
        session = self.client.session
        session['seller'] = {'id': self.seller.id}
        session.save()
        response = self.client.post('/seller_update/', {'password': 'newpassword', 'email': 'new@example.com', 'age': 35})
        self.assertRedirects(response, '/seller/seller_account/', status_code=302, target_status_code=200)
        self.seller.refresh_from_db()
        self.assertEqual(self.seller.email, 'new@example.com')

class SellerIndexTestCase(TestCase):

    def create_and_login_seller(self):
        # set up seller
        password = 'password'
        seller = Seller.objects.create(username='seller', email='seller@example.com', age=30)
        seller.set_password(password)
        seller.save()

        # login simulation
        user = authenticate(username=seller.username, password=password)
        if user is not None:
            login(self.client, user)
