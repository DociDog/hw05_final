from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from ..models import Post

User = get_user_model()


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='noname')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache(self):
        Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        response = self.authorized_client.get(reverse("posts:posts_index"))
        response_first_content = response.content
        Post.objects.all().delete()
        cache.clear()
        response = self.authorized_client.get(reverse("posts:posts_index"))
        response_second_content = response.content
        self.assertNotEqual(response_first_content, response_second_content)

    def test_cashe_second(self):
        Post.objects.create(
            author=self.user,
            text='Тестовый пост',
        )
        response = self.authorized_client.get(reverse("posts:posts_index"))
        response_first_content = response.content
        Post.objects.all().delete()
        cache.clear()
        response = self.client.get(reverse("posts:posts_index"))
        response_second_content = response.content
        self.assertNotEqual(response_first_content, response_second_content)
