from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост, который большн пятнадцати символов',
        )

    def test_models_have_correct_object_names(self):
        max_len_title = 15
        group_title = PostModelTest.group
        expected_object_name = group_title.title
        # Проверка длины __str__ post
        error_name = f"Вывод не имеет {max_len_title} символов"
        self.assertEqual(self.post.__str__(),
                         self.post.text[:max_len_title],
                         error_name)
        # Проверяем, что у модели корректно работает __str__.
        self.assertEqual(str(group_title), expected_object_name)
