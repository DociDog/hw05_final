from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache
from ..models import Group, Post
from ..forms import PostForm

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_name')
        cls.group = Group.objects.create(
            title='Тест',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group,
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post.author)
        self.author = PostPagesTests.post.author

    def posts_check_all_fields(self, post):
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.id, self.post.group.id)

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_page_names = {
            reverse('posts:posts_index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}
                    ): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user.username}
                    ): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}
                    ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}
                    ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):

        """Шаблон index сформирован с правильным контекстом."""

        response = self.guest_client.get(reverse('posts:posts_index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.text, self.post.text)

    def test_groups_page_show_correct_context(self):
        """Шаблон group_list.html."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug})
        )
        self.assertEqual(response.context['group'], self.group)
        self.posts_check_all_fields(response.context['page_obj'][0])

    def test_profile_page_show_correct_context(self):
        """Шаблон profile.html."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}))
        self.assertEqual(response.context['author'], PostPagesTests.user)
        self.posts_check_all_fields(response.context['page_obj'][0])

    def test_detail_page_show_correct_context(self):
        """Шаблон post_detail.html."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}))
        get_context = response.context.get('post')
        self.assertEqual(get_context.id, self.post.id)
        self.posts_check_all_fields(response.context['post'])
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get(
            'post').author, self.post.author)
        self.assertEqual(response.context.get(
            'post').group, self.post.group)
        self.assertEqual(response.context.get('posts_count'),
                         self.post.author.posts.count())

    def test_create_correct_context(self):
        """Тест контекста для post_create."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertIsInstance(response.context['form'], PostForm)

    def test_edit_correct_context(self):
        """Тест контекста для edit."""
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id})
        )
        self.assertIsInstance(response.context['form'], PostForm)
        self.assertIn("is_edit", response.context)
        self.assertTrue(response.context["is_edit"], True)


class PostPaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_name')
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug='test_slug',
            description='Тестовое описание',
        )
        for count_post in range(13):
            cls.post = Post.objects.create(
                text='Тестовый текст',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_posts(self):
        paginator_list = {
            'posts:index': reverse('posts:posts_index'),
            'posts:group_list': reverse(
                'posts:group_list',
                kwargs={'slug': PostPaginatorTests.group.slug}
            ),
            'posts:profile': reverse(
                'posts:profile',
                kwargs={'username': PostPaginatorTests.user.username}
            ),
        }
        for template, reverse_name in paginator_list.items():
            response = self.guest_client.get(reverse_name)
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_ten_posts(self):
        paginator_list = {
            'posts:index': reverse('posts:posts_index') + '?page=2',
            'posts:group_list': reverse(
                'posts:group_list',
                kwargs={'slug': PostPaginatorTests.group.slug}
            ) + '?page=2',
            'posts:profile': reverse(
                'posts:profile',
                kwargs={'username': PostPaginatorTests.user.username}
            ) + '?page=2',
        }
        for template, reverse_name in paginator_list.items():
            response = self.guest_client.get(reverse_name)
            self.assertEqual(len(response.context['page_obj']), 3)
