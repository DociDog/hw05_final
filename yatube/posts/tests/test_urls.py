from http import HTTPStatus
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Noname')
        cls.post = Post.objects.create(
            text='Тестовая запись для создания нового поста',
            author=cls.user,
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug_slug',
            description='Тестовое описание',
        )
        cls.user_not_author = User.objects.create(username='Test_not_author')

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = PostURLTests.user
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.user_not_author)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    # Проверяем доступность страниц для авторизованного пользователя
    def test_task_list_url_exists_at_desired_location(self):
        """Страница /task/ доступна авторизованному пользователю."""
        response = self.authorized_client_not_author.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_author_username_edit_post_url(self):
        """
        Проверка доступности страницы редактирования поста, при обращении
        автора
        """
        response = self.authorized_client_author.get(reverse(
            'posts:post_edit', args={self.post.pk}
        ))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_author_username_edit_post_url(self):
        # Проверка возможности изменять посты для авторизованного неавтора
        response = self.authorized_client_not_author.get(reverse(
            'posts:post_edit', args={self.post.pk}
        ))
        self.assertRedirects(response, reverse(
            'posts:post_detail', args={self.post.pk}
        ))

    def test_page_404(self):
        response = self.guest_client.get('/practicum_super/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_redirect_guest_client(self):
        """
        Проверка переадресации для неавторизованного
        пользователя при запросе страниц создания и
        редактирования поста
        """
        templates_url_names = {
            '/create/': 'posts/post_create.html',
            f'/posts/{self.post.id}/edit/': 'posts/post_edit.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(address, follow=True)
                if address == '/create/':
                    self.assertRedirects(
                        response, reverse('users:login') + '?next=' + reverse(
                            'posts:post_create'
                        )
                    )
                else:
                    self.assertRedirects(
                        response, reverse('users:login') + '?next=' + reverse(
                            'posts:post_edit',
                            kwargs={"post_id": self.post.id}
                        )
                    )

    def test_urls_status_code(self):
        """Проверка статуса ответа
        на страницы index, group, author, detail."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_404(self):
        """Проверка ошибки 404.
        Ошибка 404 передает кастомный шаблон."""
        response = self.guest_client.get('/practicum_super_class/',
                                         follow=True
                                         )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
        
