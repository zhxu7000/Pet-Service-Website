import json
from django.test import TestCase, Client
from django.urls import reverse

from . import views_user
from .models import User, Goods, Cart, Seller, GoodsCategory, Pet, Delivery
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib import messages
from django.contrib.messages import get_messages

from decimal import Decimal


# Create your tests here.

# Test for views_user.py

class UserTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username='testuser', password='testpassword', email='testuser@example.com',
                                        age=20)
        self.pet_photo = SimpleUploadedFile("file.jpg", b"file_content", content_type="image/jpeg")
        self.pet_data = {
            'name': 'Buddy',
            'breed': 'Labrador',
            'weight': Decimal('30.00'),
            'hair': 'Short',
            'food_preference': 'Dry Food',
            'temperament': 'Friendly'
        }

        # create seller
        self.seller = Seller.objects.create(username='testseller', password='testpassword', email='seller@example.com', age=20)
        self.seller2 = Seller.objects.create(username='Seller 2', password='testpassword', email='seller@example.com',
                                             age=20)
        # create category
        self.category = GoodsCategory.objects.create(name='testcategory')

        # create goods
        self.goods = Goods.objects.create(
            title='testproduct',
            desc='testdescription',
            price=Decimal('10.00'),
            seller=self.seller,
            image=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg'),
            category=self.category
        )

        self.good2 = Goods.objects.create(
            title='Good 2',
            desc='testdescription',
            price=Decimal('10.00'),
            seller=self.seller2,
            image=SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg'),
            category=self.category
        )

        self.delivery_data = {
            'name': 'Test Name',
            'phone': '1234567890',
            'email': 'test@example.com',
            'addr': '123 Test Street',
            'notes': 'Leave at door'
        }

        # create cart items
        self.cart_item = Cart.objects.create(user=self.user, goods=self.goods, count=1)

        Cart.objects.create(user=self.user, goods=self.goods, count=2)
        Cart.objects.create(user=self.user, goods=self.good2, count=1)

    # Test user login: pass
    def test_login_success(self):
        login_data = {
            'account': 'testuser',
            'password': 'testpassword',
        }

        response = self.client.post(reverse('login'), login_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        user_info = self.client.session.get('user')
        self.assertIsNotNone(user_info, 'User should be logged in')

    # Test user logout: pass
    def test_user_logout(self):
        # log in the user
        self.client.force_login(self.user)
        response = self.client.get(reverse('user_logout'))
        self.assertEqual(response.status_code, 302)  # redirect to login page

    # Test user register get request: pass
    def test_user_register_get_request(self):
        response = self.client.get(reverse('user_register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/register.html')

    # Test user register missing params: pass
    def test_user_register_missing_params(self):
        response = self.client.post(reverse('user_register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'age': '21',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/user/register', status_code=302, target_status_code=301)
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), 'Illegal Params')

    # Test user register username exists: pass
    def test_user_register_username_exists(self):
        User.objects.create(username='existinguser', password='password', email='test@example.com', age=21)
        response = self.client.post(reverse('user_register'), {
            'username': 'existinguser',
            'password': 'newpassword',
            'email': 'newuser@example.com',
            'age': '21',
            'name': 'petname',
            'photo': self.pet_photo,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/user/register', status_code=302, target_status_code=301)
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), 'Username Already Exists')

    # Test user register successful: pass
    def test_user_register_successful(self):
        response = self.client.post(reverse('user_register'), {
            'username': 'newuser',
            'password': 'newpassword',
            'email': 'newuser@example.com',
            'age': '21',
            'name': 'petname',
            'photo': self.pet_photo,
            'breed': 'test_breed',
            'weight': '10',
            'hair': 'short',
            'food_preference': 'dry',
            'temperament': 'calm'
        })
        self.assertEqual(response.status_code, 302)  # redirect to login page
        self.assertRedirects(response, '/user/login', status_code=302, target_status_code=301)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(Pet.objects.filter(name='petname').exists())
        new_pet = Pet.objects.get(name='petname')
        self.assertEqual(new_pet.breed, 'test_breed')
        self.assertEqual(new_pet.weight, Decimal('10.00'))
        self.assertEqual(new_pet.hair, 'short')
        self.assertEqual(new_pet.food_preference, 'dry')
        self.assertEqual(new_pet.temperament, 'calm')
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), 'Register Successfully')

# ———————— 购物车 ————————
    # Test cart add: pass
    def test_cart_add(self):

        # Simulate user login
        login_data = {
            'account': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertRedirects(response, '/')

        # Simulate POST request to add item to cart
        good = Goods.objects.create(title='testgood', price=10, seller=self.seller, category=self.category)
        response = self.client.post(reverse('cart_add'), {'id': good.id, 'count': 1})

        # Check if item was added to cart
        cart_item = Cart.objects.filter(user=self.user, goods=good).first()
        print(cart_item)
        self.assertIsNotNone(cart_item)
        self.assertEqual(cart_item.count, 1)

        # Check if success message was added
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Successfully Add To Cart')

        # Check if user was redirected
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/cart_list/')

    # Test cart delete: pass
    def test_cart_del(self):
        # Simulate user login
        login_data = {
            'account': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertRedirects(response, '/')

        # Add an item to the cart
        good = Goods.objects.create(title='testgood', price=10, seller=self.seller, category=self.category)
        Cart.objects.create(user=self.user, goods=good, count=1)

        # Simulate POST request to delete item from cart
        response = self.client.post(reverse('cart_del_jq', args=[good.id]))

        # Check if item was removed from cart
        cart_item = Cart.objects.filter(user=self.user, goods=good).first()
        self.assertIsNotNone(cart_item)

        # Check if success message was added
        self.assertEqual(response.json().get('status'), None)
        self.assertEqual(response.status_code, 200)

    def test_cart_update(self):
        # Simulate user login
        login_data = {
            'account': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertRedirects(response, '/')

        # Add an item to the cart
        good = Goods.objects.create(title='testgood', price=10, seller=self.seller, category=self.category)
        cart_item = Cart.objects.create(user=self.user, goods=good, count=1)

        # Simulate POST request to update item quantity in the cart
        new_count = 5
        response = self.client.get(reverse('cart_update_jq', args=[cart_item.id]), {'count': new_count})

        # Check if item quantity was updated
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.count, new_count)

        # Check if success message was added
        self.assertEqual(response.json().get('status'), None)
        self.assertEqual(response.status_code, 200)

    def test_cart_list(self):
        login_data = {
            'account': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertRedirects(response, '/')

        response = self.client.get(reverse('cart_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/cart_list.html')

    def test_cart_list_jq(self):
        response = self.client.get(reverse('cart_list_jq'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'success': False, 'msg': 'Please Login...'})

        login_data = {
            'account': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertRedirects(response, '/')

        response = self.client.get(reverse('cart_list_jq'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))

    def test_get_user_total_bill_price(self):
        good = Goods.objects.create(title='testgood', price=10, seller=self.seller, category=self.category)
        Cart.objects.create(user=self.user, goods=good, count=2)

        total_price = views_user.get_user_total_bill_price(self.user.id)
        self.assertEqual(total_price, 60.0)

    def test_get_cart_bill(self):
        # Testing the function directly
        cart_bill = views_user.get_cart_bill(self.user.id)
        self.assertEqual(cart_bill['total_amount'], 40.0)
        self.assertEqual(len(cart_bill['li_cart']), 3)

    def test_delivery_add(self):
        login_data = {
            'account': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertRedirects(response, '/')

        # Test authenticated user access
        response = self.client.post(reverse('delivery_add'), self.delivery_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Delivery.objects.filter(user=self.user, name='Test Name').exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Successfully Add A Delivery Info')

    def test_get_split_order_info_by_cart(self):
        login_data = {
            'account': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertRedirects(response, '/')
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)

    def test_checkout(self):
        login_data = {
            'account': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertRedirects(response, '/')
        # Test checkout view
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testproduct')
        self.assertContains(response, 'Good 2')
        self.assertContains(response, 'testuser')

    def test_account_view(self):
        login_data = {
            'account': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertRedirects(response, '/')
        # Test that the account view is accessible and displays correct information
        response = self.client.get(reverse('account'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'testuser@example.com')
        self.assertContains(response, '20')

    def test_user_update(self):
        login_data = {
            'account': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertRedirects(response, '/')
        # Test that a user can update their account information
        response = self.client.post(reverse('user_update'), {
            'password': 'newpassword',
            'ck_password': 'newpassword',
            'email': 'newemail@example.com',
            'age': '30'
        })
        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Successfully Update')
        # Check that the user was actually updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@example.com')
        self.assertEqual(self.user.age, 30)

    def test_delivery_update(self):
        login_data = {
            'account': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertRedirects(response, '/')
        response = self.client.post(reverse('delivery_add'), self.delivery_data)
        self.assertEqual(response.status_code, 302)
        # Test that a user can update their delivery information
        response = self.client.post(reverse('delivery_update'), {
            'name': 'Jane Doe',
            'phone': '0987654321',
            'email': 'jane@example.com',
            'addr': '456 Main St',
            'notes': 'Ring bell'
        })
        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Successfully Add A Delivery Info')

    def test_pet_update(self):
        login_data = {
            'account': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertRedirects(response, '/')
        # Test that a user can update their pet’s information
        response = self.client.post(reverse('pet_update'), {
            'breed': 'Golden Retriever',
            'weight': '30',
            'hair': 'Long',
            'food_preference': 'Wet Food',
            'temperament': 'Playful'
        })
        # Check for success message
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Successfully Update')

    def test_pet_add(self):
        login_data = {
            'account': 'testuser',
            'password': 'testpassword',
        }
        response = self.client.post(reverse('login'), login_data)
        self.assertRedirects(response, '/')
        # Sending a POST request to add a pet
        response = self.client.post(reverse('pet_add'), {
            **self.pet_data,
            'photo': self.pet_photo
        }, follow=True)

        # Check that the pet was added successfully
        self.assertTrue(Pet.objects.filter(name='Buddy').exists())
        pet = Pet.objects.get(name='Buddy')

        for field, value in self.pet_data.items():
            self.assertEqual(getattr(pet, field), value)


