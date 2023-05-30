import shutil
import tempfile
from datetime import date

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(
            username='ioan',
            first_name='Иван',
            last_name='Иванов')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Текстовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост',
            group=PostPagesTests.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(PostPagesTests.user_author)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'ioan'}):
                'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': PostPagesTests.post.id}
                    ):
                'posts/post_detail.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{PostPagesTests.post.id}'}
                    ):
                'posts/create_post.html'
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def check_post_attributes(self, post):
        post_in = post
        task_text_0 = post_in.text
        task_author_0 = post_in.author.username
        task_pub_date_0 = post_in.pub_date.isocalendar()
        task_image_0 = post_in.image
        post_attr = {
            task_text_0: 'Тестовый пост',
            task_author_0: 'ioan',
            task_pub_date_0: date.today().isocalendar(),
            task_image_0: 'posts/small.gif'
        }
        for attr_get, expected_attr in post_attr.items():
            with self.subTest(attr_get=attr_get):
                self.assertEqual(attr_get, expected_attr)

    def test_index_correct_context(self):
        response = self.authorized_author_client.get(reverse('posts:index'))
        task_title = response.context['title']
        self.assertEqual(task_title, 'Это главная страница проекта Yatube')
        first_object = response.context['page_obj'][0]
        self.check_post_attributes(post=first_object)

    def test_group_list_correct_context(self):
        response = self.authorized_author_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        task_group = response.context['group']
        first_object = response.context['page_obj'][0]
        self.assertEqual(task_group.title, PostPagesTests.group.title)
        self.assertEqual(task_group.description, 'Текстовое описание')
        self.check_post_attributes(post=first_object)

    def test_profile_correct_context(self):
        response = self.authorized_author_client.get(
            reverse('posts:profile', kwargs={'username': 'ioan'})
        )
        task_author = response.context['author']
        task_post_count = response.context['post_count']
        first_object = response.context['page_obj'][0]
        self.assertEqual(task_author.get_full_name(), 'Иван Иванов')
        self.assertEqual(task_post_count, 1)
        self.check_post_attributes(post=first_object)

    def test_post_detail_correct_context(self):
        response = self.authorized_author_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{PostPagesTests.post.id}'}
                    )
        )
        task_post_count = response.context['post_count']
        post = response.context['post']
        self.assertEqual(task_post_count, 1)
        self.assertEqual(post.author.get_full_name(), 'Иван Иванов')
        self.check_post_attributes(post=post)

    def test_post_create_correct_context(self):
        response = self.authorized_author_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_correct_context(self):
        response = self.authorized_author_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{PostPagesTests.post.id}'}
                    )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(
            username='pit',
            first_name='Пётр',
            last_name='Иванов')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Текстовое описание',
        )
        for i in range(13):
            cls.post = Post.objects.create(
                author=cls.user_author,
                text=f'Тестовый пост {i}',
                group=PaginatorViewsTest.group
            )

    def setUp(self):
        self.client = Client()
        self.client.force_login(PaginatorViewsTest.user_author)

    def test_index_first_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_first_page_contains_ten_records(self):
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_second_page_contains_ten_records(self):
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': 'pit'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_ten_records(self):
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': 'pit'}) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)


class PostPresentTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='pit')
        cls.group_first = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug-first',
            description='Текстовое описание',
        )
        cls.group_second = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug-second',
            description='Текстовое описание2',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост',
            group=PostPresentTest.group_first
        )

    def setUp(self):
        self.client = Client()

    def test_index_contain_post(self):
        response = self.client.get(reverse('posts:index'))
        for post in response.context['page_obj']:
            post_get = None
            if post.text == 'Тестовый пост':
                post_get = post
        self.assertEqual(post_get, PostPresentTest.post)

    def test_group_list_contain_post(self):
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug-first'})
        )
        for post in response.context['page_obj']:
            post_get = None
            if post.text == 'Тестовый пост':
                post_get = post
        self.assertEqual(post_get, PostPresentTest.post)

    def test_profile_contain_post(self):
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': 'pit'})
        )
        for post in response.context['page_obj']:
            post_get = None
            if post.text == 'Тестовый пост':
                post_get = post
        self.assertEqual(post_get, PostPresentTest.post)

    def test_group_list_not_contain_post(self):
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug-second'})
        )
        post_get = None
        for post in response.context['page_obj']:
            if post.text == 'Тестовый пост':
                post_get = post
        self.assertIsNone(post_get)


class CommentTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(
            username='ioan',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.not_authorized_client = Client()
        self.authorized_client.force_login(CommentTest.user_author)

    def test_add_comment_authorized_client(self):
        comment_data = {
            'text': 'Отличная мысль',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': CommentTest.post.id}
            ),
            data=comment_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': CommentTest.post.id}
            )
        )
        self.assertTrue(
            Comment.objects.filter(
                text='Отличная мысль',
                author=1,
            ).exists()
        )

    def test_comment_of_post_detail_authorized_client(self):
        Comment.objects.create(
            text='Отличная мысль',
            post_id=CommentTest.post.id,
            author=CommentTest.user_author
        )
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': CommentTest.post.id}
            )
        )
        comment_get_by_context = response.context['comments'][0]
        self.assertEqual(
            comment_get_by_context.text,
            'Отличная мысль'
        )
        self.assertEqual(comment_get_by_context.author.username, 'ioan')

    def test_comment_of_post_detail_not_authorized_client(self):
        comment_data = {
            'text': 'Отличная мысль',
        }
        response = self.not_authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': CommentTest.post.id}
            ),
            data=comment_data,
            follow=True
        )
        self.assertRedirects(
            response,
            '/auth/login/?next=/posts/1/comment/'
        )
        self.assertEqual(Comment.objects.count(), 0)


class CacheTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_author = User.objects.create_user(
            username='pit',
        )
        for i in range(100, 113):
            Post.objects.create(
                text=f'Тест {i}',
                author=CacheTests.user_author,
            )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(CacheTests.user_author)

    def test_index_cache(self):

        response_page1 = self.authorized_author_client.get(
            reverse('posts:index')
        )
        response_page2 = self.authorized_author_client.get(
            reverse('posts:index'),
            {'page': 2}
        )
        self.assertNotEqual(response_page1.content, response_page2.content)
        self.assertIsNotNone(response_page1)
        key = make_template_fragment_key(
            'index_page',
            [response_page1.context['page_obj'].number, ]
        )
        cach_page = cache.get(key)
        self.assertIsNotNone(cach_page)
        CacheTests.post.delete()
        Post.objects.create(
            author=CacheTests.user_author,
            text='Тестовый пост2',
        )
        response_befor_clear_cache = self.authorized_author_client.get(
            reverse('posts:index')
        )
        self.assertIsNotNone(response_befor_clear_cache)
        key_after_del = make_template_fragment_key(
            'index_page',
            [response_befor_clear_cache.context['page_obj'].number, ]
        )
        cach_page_after_del = cache.get(key_after_del)
        self.assertIsNotNone(cach_page_after_del)
        self.assertEqual(cach_page, cach_page_after_del)
        self.assertEqual(
            response_befor_clear_cache.content,
            response_page1.content
        )
        cache.clear()
        response_after_clear_cache = self.authorized_author_client.get(
            reverse('posts:index')
        )
        self.assertIsNotNone(response_after_clear_cache)
        key_after_clear = make_template_fragment_key(
            'index_page',
            [response_after_clear_cache.context['page_obj'].number, ]
        )
        cach_page_after_clear = cache.get(key_after_clear)
        self.assertIsNotNone(cach_page_after_clear)
        self.assertNotEqual(cach_page, cach_page_after_clear)
        self.assertNotEqual(
            response_after_clear_cache.content,
            response_page1.content
        )


class FollowTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_author = User.objects.create_user(
            username='ioan',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.user = User.objects.create_user(
            username='pit',
        )
        self.authorized_client.force_login(self.user)
        self.authorized_client_unfollower = Client()
        self.user_unfollower = User.objects.create_user(
            username='tom',
        )
        self.authorized_client_unfollower.force_login(self.user_unfollower)

    def test_subscribe_create(self):
        empty_subscribe = Follow.objects.filter(user=self.user).count()
        self.assertEqual(empty_subscribe, 0)
        self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': FollowTests.user_author}
            )
        )
        add_subscribe = Follow.objects.filter(user=self.user).count()
        self.assertEqual(add_subscribe, empty_subscribe + 1)

    def test_subscribe_context(self):
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        empty_subscribe_response = len(response.context['page_obj'])
        self.assertEqual(empty_subscribe_response, 0)
        response = self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': FollowTests.user_author}
            )
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        append_subscribe_response = len(response.context['page_obj'])
        self.assertEqual(append_subscribe_response, 1)
        post = response.context['page_obj'][0]
        post_attr = {
            post.text: 'Тестовый пост',
            post.author.username: 'ioan',
            post.pub_date.isocalendar(): date.today().isocalendar(),
        }
        for attr_get, expected_attr in post_attr.items():
            with self.subTest(attr_get=attr_get):
                self.assertEqual(attr_get, expected_attr)

    def test_unsubscribe_delete(self):
        Follow.objects.create(user=self.user, author=FollowTests.user_author)
        subscribe = Follow.objects.filter(user=self.user).count()
        self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': FollowTests.user_author}
            )
        )
        empty_subscribe = Follow.objects.filter(user=self.user).count()
        self.assertEqual(empty_subscribe, subscribe - 1)

    def test_unsubscribe_context(self):
        Follow.objects.create(user=self.user, author=FollowTests.user_author)
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        subscribe_response = len(response.context['page_obj'])
        self.assertEqual(subscribe_response, 1)
        response = self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': FollowTests.user_author}
            )
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        empty_subscribe_response = len(response.context['page_obj'])
        self.assertEqual(empty_subscribe_response, subscribe_response - 1)

    def test_view_to_follower(self):
        Follow.objects.create(user=self.user, author=FollowTests.user_author)
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response.context['page_obj']), 1)
        post_in = response.context['page_obj'][0]
        task_text_0 = post_in.text
        task_author_0 = post_in.author.username
        task_pub_date_0 = post_in.pub_date.isocalendar()
        post_attr = {
            task_text_0: 'Тестовый пост',
            task_author_0: 'ioan',
            task_pub_date_0: date.today().isocalendar(),
        }
        for attr_get, expected_attr in post_attr.items():
            with self.subTest(attr_get=attr_get):
                self.assertEqual(attr_get, expected_attr)

    def test_view_to_unfollower(self):
        Follow.objects.create(user=self.user, author=FollowTests.user_author)
        response = self.authorized_client_unfollower.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(len(response.context['page_obj']), 0)
