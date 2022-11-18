from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User

User = get_user_model()


class FormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_name')
        cls.test_group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.test_group,
        )

    def setUp(self):
        self.user = User.objects.create(username='DociDog')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Валидная форма создает пост."""
        count_posts = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': self.test_group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(Post.objects.count(), count_posts + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data.get('text'),
                author=self.user,
                group=form_data.get('group'),
            ).exists()
        )

    def test_post_edit(self):
        post = Post.objects.create(
            author=self.user,
            text='Leon',
        )
        self.new_group = Group.objects.create(
            title='Тестовая группа 44',
            slug='test-slug_2',
            description='Текстовое описание',
        )
        post_count = Post.objects.count()
        forms_data = {
            'text': 'Текст прописи',
            'group': self.new_group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=forms_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post.id}
        ))
        self.assertTrue(
            Post.objects.filter(
                pk=post.id,
                text=forms_data.get("text"),
                group=Group.objects.get(title='Тестовая группа 44').id,
            ).exists()
        )
        self.assertEqual(Post.objects.count(), post_count)
