from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from posts.models import Follow, Post

User = get_user_model()


class PostFollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Author')
        cls.follower = User.objects.create_user(username='Follower')
        cls.follower_client = Client()
        cls.follower_client.force_login(cls.follower)

        cls.nonfollower = User.objects.create_user(username='Nonfollower')
        cls.nonfollower_client = Client()
        cls.nonfollower_client.force_login(cls.nonfollower)

    def setUp(self):
        cache.clear()

    def test_follow_and_unfollow(self):
        '''Авторизованный пользователь может подписываться на других
        пользователей и удалять их из подписок'''
        PostFollowTests.follower_client.get(
            (reverse('posts:profile_follow', kwargs={'username': 'Author'})),
        )
        self.assertEqual(
            Follow.objects.filter(
                user=PostFollowTests.follower,
            ).count(),
            1,
        )

        PostFollowTests.follower_client.get(
            (reverse('posts:profile_unfollow', kwargs={'username': 'Author'})),
        )
        self.assertEqual(
            Follow.objects.filter(user=PostFollowTests.follower).count(),
            0
        )

    def test_follow_index(self):
        '''Новая запись пользователя появляется в ленте тех, кто на него
        подписан и не появляется в ленте тех, кто не подписан.'''
        Post.objects.create(
            author=PostFollowTests.author,
            text='Тестовый пост',
        )
        Follow.objects.create(
            user=PostFollowTests.follower, author=PostFollowTests.author
        )
        response_follower = PostFollowTests.follower_client.get(
            reverse('posts:follow')
        )
        self.assertEqual(
            len(response_follower.context['page_obj']),
            1
        )
        # cache.clear()
        response_nonfollower = PostFollowTests.nonfollower_client.get(
            reverse('posts:follow')
        )
        self.assertEqual(
            len(response_nonfollower.context['page_obj']),
            0
        )
