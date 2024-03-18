from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse
import json
from unittest.mock import patch, MagicMock
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.files.uploadedfile import SimpleUploadedFile
from pets.models import User, Pet, Cart, Delivery, Order, Seller, OrderComment, Services, Bookings,Goods,GoodsCategory,Forum
from django.contrib.sessions.middleware import SessionMiddleware


class ViewTestCase(TestCase):
    def setUp(self):

        # Set up client
        self.client = Client()
        with open('/Users/xuzhenke/Desktop/Group-15/pets/test_image/test_image.jpg', 'rb') as img:
            image = SimpleUploadedFile(name='test_image.jpg', content=img.read(), content_type='image/jpg')

        # Create test users and items
        self.user = User.objects.create(
            username="testuser", 
            password="password123",
            age=30
            )
        Goods.objects.create(
            title="Test Good",
            desc="Test Description",
            price=30,
            seller_id=5,
            category_id=2,
            image=image 
            )

    def test_index_view(self):
        
        session = self.client.session
        session['user'] = {'id': self.user.id}
        session.save()

        response = self.client.get(reverse('index'))  
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Good")

    @patch('requests.get')
    def test_chatbot_request(self, mock_get):
        # Simulate requests.get return value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'text': 'Mock Reply'}
        mock_get.return_value = mock_response

        response = self.client.get(reverse('chatbot_request'), {'message': 'hello'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'), {'reply': 'Mock Reply'})


class ServiceViewTestCase(TestCase):
    def setUp(self):

        self.client = Client()

        self.user = User.objects.create(
            username="testuser", 
            password="password123",
            age=30
            )
        
        with open('/Users/xuzhenke/Desktop/Group-15/pets/test_image/test_image.jpg', 'rb') as img:
            image = SimpleUploadedFile(name='test_image.jpg', content=img.read(), content_type='image/jpg')

 
        seller = Seller.objects.create(username="Test Seller", password="password", email="test@example.com", age=30)
        Services.objects.create(title="Test Service",
                                 desc="Test Service Description", 
                                 price=100, seller=seller, 
                                 category_name="Test Category",
                                 image=image 
                                )

    def test_services_view_pagination(self):
        
        response = self.client.get(reverse('services'), {'page': 1, 'size': 1})
        self.assertEqual(response.status_code, 200)
        

    def test_services_view_with_keyword(self):
    
        response = self.client.get(reverse('services'), {'keyword': 'Test'})
        self.assertEqual(response.status_code, 200)


    def test_services_view_with_category_filter(self):

        response = self.client.get(reverse('services'), {'category_name': 'Test Category'})
        self.assertEqual(response.status_code, 200)
  

    def test_services_view_without_login(self):

        response = self.client.get(reverse('services'))
        self.assertEqual(response.status_code, 200)




def add_session_to_request(request):

    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

class ShopViewTest(TestCase):

    def setUp(self):

        # Create test users and items
        self.user = User.objects.create(
            username="testuser", 
            password="password123",
            age=30
            )
        with open('/Users/xuzhenke/Desktop/Group-15/pets/test_image/test_image.jpg', 'rb') as img:
            image = SimpleUploadedFile(name='test_image.jpg', content=img.read(), content_type='image/jpg')
        Goods.objects.create(
            title="Test Good",
            desc="Test Description",
            price=30,
            seller_id=5,
            category_id=2,
            image=image 
            )

        self.goods_category = GoodsCategory.objects.create(name="Test Category")


    def test_shop_view_without_login(self):

        response = self.client.get(reverse('shop'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context.get('cart_info'), {})


    def test_shop_view_with_login(self):
        self.user = User.objects.create(
            username="testuser", 
            password="password123",
            age=30
            )
        self.client.login(username='testuser',password='password123')
        response = self.client.get(reverse('shop'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('cart_info', response.context)

    def test_shop_view_with_keyword_search(self):

        response = self.client.get(reverse('shop') + '?keyword=Test')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(good.title == "Test Good" for good in response.context['li_goods']))

    def test_shop_view_with_category_filter(self):
        """测试类别过滤"""
        response = self.client.get(reverse('shop') + '?category=Test Category')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(good.category.name == "Test Category" for good in response.context['li_goods']))

    def test_shop_view_pagination(self):
        """测试分页"""
        # 假设你已经有足够多的商品来测试分页
        response = self.client.get(reverse('shop') + '?page=1&size=5')
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(response.context['li_goods']), 5)

class ShopDetailsViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            username="testuser", 
            password="password123",
            age=30
            )
        
        with open('/Users/xuzhenke/Desktop/Group-15/pets/test_image/test_image.jpg', 'rb') as img:
            image = SimpleUploadedFile(name='test_image.jpg', content=img.read(), content_type='image/jpg')
        self.goods=Goods.objects.create(
            title="Test Good",
            desc="Test Description",
            price=30,
            seller_id=1,
            category_id=2,
            image=image 
            )
        
        self.seller = Seller.objects.create(username="Test Seller", password="password", email="test@example.com", age=30)

        self.order = Order.objects.create(
            user=self.user,
            seller=self.seller,
            created_at=timezone.now(),
            total_price=10.0,
            goods_info_json_str=json.dumps([]),  
            delivery_info_json_str=json.dumps({}),
            status=1  
        )

        self.comment = OrderComment.objects.create(
            user=self.user,
            goods=self.goods,
            order=self.order,
            content="Test Comment",
            created_at=timezone.now()
        )



    def test_shop_details_with_comments(self):
        response = self.client.get(reverse('shop_details', args=[self.goods.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('count_comment', response.context)
        self.assertIn('li_comment', response.context)
        self.assertGreaterEqual(len(response.context['li_comment']), 1)



class ForumViewTest(TestCase):

    def setUp(self):
        self.client=Client()
        self.user1 = User.objects.create(
            username="testuser1", 
            password="password1231",
            age=30)

        self.user2 = User.objects.create(
            username="testuser2",             
            password="password1232",
            age=31)

        self.forum1 = Forum.objects.create(
            from_user=self.user1,
            content="Content from user1",
            to_user=self.user2,
            created_at=timezone.now()
        )

        self.forum2 = Forum.objects.create(
            from_user=self.user2,
            content="Content from user2",
            to_user=None,  # 可以为空
            created_at=timezone.now()
        )

    def test_forum_page_get_request(self):
        response = self.client.get(reverse('forum'))  # 确保 'forum' 是对应的 URL 名称
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum.html')

    # def test_forum_post_without_login(self):
    #     response = self.client.post(reverse('forum'), {'content': 'test content'})
    #     login_url = '/user/login/'  # Adjust based on your actual URL configuration
    #     self.assertRedirects(response, login_url, status_code=302, target_status_code=200)

    # def test_forum_post_with_login(self):
    #     session = self.client.session
    #     session['user'] = {'id': self.user1.id}
    #     session.save()

    #     response = self.client.post(reverse('forum'), {'content': 'test content'})
    #     expected_url = '/forum/'  # Make sure this matches your actual URL, including trailing slash
    #     self.assertRedirects(response, expected_url, status_code=302, target_status_code=200)
    #     self.assertEqual(Forum.objects.count(), 3)  # Adjust based on your setup
    #     new_post = Forum.objects.last()
    #     self.assertEqual(new_post.content, 'test content')

class CommunityListViewTest(TestCase):
    
    def test_community_list(self):
        # Assuming some community stories are already added in setup
        response = self.client.get(reverse('community_list'), {'page': 1})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'community_list.html')
        self.assertIn('community', response.context)
        # Further assertions can check pagination and actual content

class CommunityDetailsViewTest(TestCase):

    def test_community_details(self):
        # Assuming a community story with id 1 exists
        response = self.client.get(reverse('community_details', args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'community_details.html')
        self.assertIn('community', response.context)
        # Further assertions for the community content

# class CommunitySendViewTest(TestCase):

#     def test_community_send_get(self):
#         # For the GET request
#         response = self.client.get(reverse('community_send'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'community_send.html')

#     def test_community_send_post_without_login(self):
#         # For the POST request without login
#         response = self.client.post(reverse('community_send'), {'title': 'Test Title', 'content': 'Test Content'})
#         self.assertRedirects(response, reverse('user_login'), status_code=302, target_status_code=200)

#     def test_community_send_post_with_login(self):
#         # Simulate login
#         session = self.client.session
#         session['user'] = {'id': 'user_id'}  # Adjust as needed
#         session.save()

#         response = self.client.post(reverse('community_send'), {'title': 'Test Title', 'content': 'Test Content'})
#         self.assertRedirects(response, reverse('community_list'), status_code=302, target_status_code=200)


class CommunityEditorImageUploadViewTest(TestCase):

    def test_image_upload(self):
        # Create a simple test image file
        image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(reverse('community_editor_image_upload'), {'file': image})
        self.assertEqual(response.status_code, 200)
        self.assertTrue('location' in response.json())



class PostMessageTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.post_message_url = reverse('post_message')  # Replace with your actual URL name
        self.user = User.objects.create(username='testuser', password='password123',age=30)

    def test_message_post_success(self):
        # Simulate logged-in user
        session = self.client.session
        session['user'] = {'id': self.user.pk}
        session.save()

        response = self.client.post(self.post_message_url, {
            'content': 'Test Message',
            'to_user_id': ''  # Assuming it's an optional field
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))
        self.assertIn('Test Message', response.json().get('html'))

    def test_message_post_no_authentication(self):
        response = self.client.post(self.post_message_url, {
            'content': 'Test Message',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json().get('success'))
        self.assertEqual(response.json().get('error_message'), 'User not authenticated')

    def test_message_post_invalid_data(self):
        # Simulate logged-in user
        session = self.client.session
        session['user'] = {'id': self.user.pk}
        session.save()

        response = self.client.post(self.post_message_url, {
            'content': 'Test Message',
            'to_user_id': 'invalid_id'
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json().get('success'))
        self.assertEqual(response.json().get('error_message'), 'Invalid to_user_id')

