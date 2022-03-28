from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='ioan')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Текстовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_user = Client()
        self.user = User.objects.create_user(username='pit')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(PostURLTests.user_author)

    def test_page_guest_user_at_desired_location(self):
        status_pages_direct = {
            '/': HTTPStatus.OK,
            f'/group/{PostURLTests.group.slug}/': HTTPStatus.OK,
            f'/profile/{PostURLTests.user_author.username}/': HTTPStatus.OK,
            f'/posts/{PostURLTests.post.id}/': HTTPStatus.OK,
            '/unexisting_page': HTTPStatus.NOT_FOUND
        }
        for address, code in status_pages_direct.items():
            with self.subTest(address=address):
                response = self.guest_user.get(address)
                self.assertEqual(response.status_code, code)

        status_pages_redirect = {
            f'/posts/{PostURLTests.post.id}/edit/':
            f'/auth/login/?next=/posts/{PostURLTests.post.id}/edit/',
            '/create/': '/auth/login/?next=/create/',
        }
        for address, redirect_address in status_pages_redirect.items():
            with self.subTest(address=address):
                response = self.guest_user.get(address, follow=True)
                self.assertRedirects(response, redirect_address)

    def test_page_authorized_user_at_desired_location(self):
        status_pages_direct = {
            '/': HTTPStatus.OK,
            f'/group/{PostURLTests.group.slug}/': HTTPStatus.OK,
            f'/profile/{PostURLTests.user_author.username}/': HTTPStatus.OK,
            f'/posts/{PostURLTests.post.id}/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            '/unexisting_page': HTTPStatus.NOT_FOUND
        }
        for address, code in status_pages_direct.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, code)
        status_pages_redirect = {
            f'/posts/{PostURLTests.post.id}/edit/':
            f'/posts/{PostURLTests.post.id}/',
        }
        for address, redirect_address in status_pages_redirect.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)
                self.assertRedirects(response, redirect_address)

    def test_authorized_author_user_at_desired_location(self):
        status_pages_direct = {
            '/': HTTPStatus.OK,
            f'/group/{PostURLTests.group.slug}/': HTTPStatus.OK,
            f'/profile/{PostURLTests.user_author.username}/': HTTPStatus.OK,
            f'/posts/{PostURLTests.post.id}/': HTTPStatus.OK,
            f'/posts/{PostURLTests.post.id}/edit/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            '/unexisting_page': HTTPStatus.NOT_FOUND
        }
        for address, code in status_pages_direct.items():
            with self.subTest(address=address):
                response = self.authorized_author_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_urls_users_correct_template(self):
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostURLTests.user_author.username}/':
            'posts/profile.html',
            f'/posts/{PostURLTests.post.id}/': 'posts/post_detail.html',
            f'/posts/{PostURLTests.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_author_client.get(address)
                self.assertTemplateUsed(response, template)
