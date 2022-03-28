from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post

User = get_user_model()


class PostModelTestPost(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_name(self):
        post = PostModelTestPost.post
        expected_post_name = post.text
        self.assertEqual(
            expected_post_name, str(post)
        )

    def test_label_post(self):
        post = PostModelTestPost.post
        labels_list = {
            post._meta.get_field('text').verbose_name:
                'Текст поста',
            post._meta.get_field('text').help_text:
                'Текст нового поста',
            post._meta.get_field('author').verbose_name:
                'Автор',
            post._meta.get_field('author').help_text:
                'Автор поста',
            post._meta.get_field('group').verbose_name:
                'Группа',
            post._meta.get_field('group').help_text:
                'Группа, к которой будет относиться пост'
        }
        for label, expected_label in labels_list.items():
            with self.subTest(label=label):
                self.assertEqual(label, expected_label)


class PostModelTestGroup(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Текстовое описание',
        )

    def test_models_have_correct_object_name(self):
        group = PostModelTestGroup.group
        expected_group_name = group.title
        self.assertEqual(
            expected_group_name, str(group)
        )

    def test_label_group(self):
        group = PostModelTestGroup.group
        labels_list = {
            group._meta.get_field('title').verbose_name:
                'Название группы',
            group._meta.get_field('title').help_text:
                'Группа, к которой будет относиться пост',
            group._meta.get_field('slug').verbose_name:
                'URL-идентификатор',
            group._meta.get_field('slug').help_text:
                'Уникальная строка, содержащая только "безопасные" символы',
            group._meta.get_field('description').verbose_name:
                'Описание группы',
            group._meta.get_field('description').help_text:
                'Краткое описание группы'
        }
        for label, expected_label in labels_list.items():
            with self.subTest(label=label):
                self.assertEqual(label, expected_label)
