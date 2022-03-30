import shutil
import tempfile

from datetime import date

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='ioan')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Текстовое описание',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.client = Client()
        self.client.force_login(PostCreateFormTests.user_author)

    def test_create_post(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст',
            'group': PostCreateFormTests.group.id,
            'image': uploaded,
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post_new = Post.objects.get(id=1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                group=1,
                author=1,
                image='posts/small.gif',
            ).exists()
        )
        self.assertEqual(Post.objects.count(), 1)
        self.assertRedirects(
            response, reverse('posts:profile', kwargs={'username': 'ioan'})
        )
        self.assertEqual(post_new.text, 'Тестовый текст')
        self.assertEqual(post_new.group.title, 'Тестовая группа')
        self.assertEqual(post_new.author.username, 'ioan')
        self.assertEqual(
            post_new.pub_date.isocalendar(),
            date.today().isocalendar()
        )
        self.assertEqual(post_new.image, 'posts/small.gif')

    def test_edit_post(self):
        post_first = Post.objects.create(
            author=PostCreateFormTests.user_author,
            text='Тестовый пост',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small_new.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый пост 2',
            'group': PostCreateFormTests.group.id,
            'image': uploaded,
        }
        response = self.client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': post_first.id}
                    ),
            data=form_data,
            follow=True
        )
        post_edit = Post.objects.get(id=post_first.id)
        self.assertRedirects(
            response, reverse('posts:post_detail',
                              kwargs={'post_id':
                                      post_first.id
                                      }
                              )
        )
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост 2',
                group=1,
                author=1,
                id=post_first.id,
                image='posts/small_new.gif'
            ).exists()
        )
        self.assertEqual(post_edit.text, 'Тестовый пост 2')
        self.assertEqual(post_edit.group.title, 'Тестовая группа')
        self.assertEqual(post_edit.author.username, 'ioan')
        self.assertEqual(
            post_edit.pub_date.isocalendar(),
            date.today().isocalendar()
        )
        self.assertEqual(post_edit.image, 'posts/small_new.gif')


class CommentCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='ioan')
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост',
        )

    def setUp(self):
        self.client = Client()
        self.user_commentator = User.objects.create_user(username='pit')
        self.client.force_login(self.user_commentator)

    def test_create_comment(self):
        form_data = {
            'text': 'Tекст комментария',
        }
        self.client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': CommentCreateFormTests.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), 1)
        new_comment = Comment.objects.get(id=1)
        self.assertEqual(new_comment.text, 'Tекст комментария')
        self.assertEqual(new_comment.post.id, CommentCreateFormTests.post.id)
        self.assertEqual(new_comment.author.username, 'pit')
        self.assertEqual(
            new_comment.created.isocalendar(),
            date.today().isocalendar()
        )