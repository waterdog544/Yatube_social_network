from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Comment, Follow, Group, Post

User = get_user_model()


class ModelTestPost(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_name(self):
        post = ModelTestPost.post
        expected_post_name = post.text
        self.assertEqual(
            expected_post_name, str(post)
        )

    def test_label_post(self):
        post = ModelTestPost.post
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


class ModelTestGroup(TestCase):
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
        group = ModelTestGroup.group
        expected_group_name = group.title
        self.assertEqual(
            expected_group_name, str(group)
        )

    def test_label_group(self):
        group = ModelTestGroup.group
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


class ModelTestComment(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый коментарий',
            post=cls.post
        )

    def test_models_have_correct_object_name(self):
        comment = ModelTestComment.comment
        expected_comment_name = comment.text[:15]
        self.assertEqual(
            expected_comment_name, str(comment)
        )

    def test_label_post(self):
        comment = ModelTestComment.comment
        labels_list = {
            comment._meta.get_field('text').verbose_name:
                'Текст комментария',
            comment._meta.get_field('text').help_text:
                'Прокомментируйте пост',
            comment._meta.get_field('author').verbose_name:
                'Автор',
            comment._meta.get_field('author').help_text:
                'Автор комментария',
            comment._meta.get_field('post').verbose_name:
                'Пост',
            comment._meta.get_field('post').help_text:
                'Комментируемый пост',
            comment._meta.get_field('created').verbose_name:
                'Дата',
            comment._meta.get_field('created').help_text:
                'Дата создания комментария',
        }
        for label, expected_label in labels_list.items():
            with self.subTest(label=label):
                self.assertEqual(label, expected_label)


class ModelTestFollow(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.author = User.objects.create_user(username='pit')
        cls.follow = Follow.objects.create(user=cls.user, author=cls.author)

    def test_models_have_correct_object_name(self):
        follow = ModelTestFollow.follow
        expected_comment_name = (f'{ModelTestFollow.user} подписан '
                                 f'на {ModelTestFollow.author}'
                                 )
        self.assertEqual(
            str(follow), expected_comment_name
        )

    def test_label_post(self):
        follow = ModelTestFollow.follow
        labels_list = {
            follow._meta.get_field('author').verbose_name:
                'Автор',
            follow._meta.get_field('author').help_text:
                'Автор, на которого желаете подписаться',
            follow._meta.get_field('user').verbose_name:
                'Пользователь',
            follow._meta.get_field('user').help_text:
                'Пользователь, желающий подписаться на автора',
        }
        for label, expected_label in labels_list.items():
            with self.subTest(label=label):
                self.assertEqual(label, expected_label)
