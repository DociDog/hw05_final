import tempfile
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, User

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='Noname')
        cls.post = Post.objects.create(
            text='Тестовая запись для создания нового поста',
            author=cls.user,
        )
        cls.test_group = Group.objects.create(
            title='Тестовая группа',
            slug='slug_slug',
            description='Тестовое описание',
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = ImageTests.user
        self.authorized_client_author = User.objects.create(
            username='Test_author'
        )
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)
        self.user_not_author = User.objects.create(username='Test_not_author')
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(self.user_not_author)
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_with_picture(self):
        posts_count = Post.objects.count()

        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.test_group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
        }
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='test.gif',
            content=small_gif,
            content_type='image/gif',
        )
        form_data = {
            'text': 'Тестовый пост с картинкой',
            'group': self.test_group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(
            response, reverse(
                'posts:profile',
                kwargs={'username': self.user})
        )
        post = Post.objects.first()
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.image, 'posts/test.gif')

        for address, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
                self.assertEqual(post.image, 'posts/test.gif')
