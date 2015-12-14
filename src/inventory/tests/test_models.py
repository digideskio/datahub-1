import factory

from inventory import models

from django.test import TestCase
from django.db.models import signals
from django.contrib.auth.models import User


class LegacyuserTests(TestCase):
    """ saving and loading users"""

    def test_fields(self):
        models.DataHubLegacyUser.objects.create(
            id=10, email="foo@bar.fizz", username="foobar", f_name="f_name",
            l_name="l_name", password="_h4rd;Pa_ss w-0Rd_", active=True,
            issuer="issuer", subject="subject")
        loaded_user = models.DataHubLegacyUser.objects.get(id=10)

        self.assertEqual(loaded_user.id, 10)
        self.assertEqual(loaded_user.email, "foo@bar.fizz")
        self.assertEqual(loaded_user.username, "foobar")
        self.assertEqual(loaded_user.f_name, "f_name")
        self.assertEqual(loaded_user.l_name, "l_name")
        self.assertEqual(loaded_user.password, "_h4rd;Pa_ss w-0Rd_")
        self.assertEqual(loaded_user.active, True)
        self.assertEqual(loaded_user.issuer, "issuer")
        self.assertEqual(loaded_user.subject, "subject")
        self.assertEqual(unicode(loaded_user), "foobar")


class CardTests(TestCase):
    """test saving and loading cards"""

    def test_fields(self):
        models.Card.objects.create(
            id=10, repo_base="repo_base", repo_name="repo_name",
            card_name="card_name", query="query")

        loaded_card = models.Card.objects.get(id=10)

        self.assertEqual(loaded_card.id, 10)
        self.assertEqual(loaded_card.repo_base, "repo_base")
        self.assertEqual(loaded_card.repo_name, "repo_name")
        self.assertEqual(loaded_card.card_name, "card_name")
        self.assertEqual(loaded_card.query, "query")


class AnnotationTest(TestCase):
    """test saving and loading annotation"""

    def test_fields(self):
        models.Annotation.objects.create(
            id=10, url_path="url_path", annotation_text="annotation_text")
        loaded_annotation = models.Annotation.objects.get(id=10)

        self.assertEqual(loaded_annotation.id, 10)
        self.assertEqual(loaded_annotation.url_path, "url_path")
        self.assertEqual(loaded_annotation.annotation_text, "annotation_text")


class AppTest(TestCase):
    """test saving and loading apps"""

    @factory.django.mute_signals(signals.pre_save)
    def setUp(self):
        self.legacy_user = models.DataHubLegacyUser.objects.create(
            id=10, email="foo@bar.fizz", username="foobar", f_name="f_name",
            l_name="l_name", password="_h4rd;Pa_ss w-0Rd_", active=True,
            issuer="issuer", subject="subject")

        self.user = User.objects.create_user(
            "username", "email@email.email", "password")

    def test_fields(self):
        app = models.App.objects.create(
            app_id="app_id", id=10, app_name="app_name",
            app_token="app_token", user=self.user,
            legacy_user=self.legacy_user)

        self.assertEqual(app.id, 10)
        self.assertEqual(app.app_id, "app_id")
        self.assertEqual(app.app_name, "app_name")
        self.assertEqual(app.app_token, "app_token")
        self.assertEqual(app.legacy_user, self.legacy_user)
        self.assertEqual(app.user, self.user)


class PermissionTest(TestCase):
    """test permissions granted to apps"""

    @factory.django.mute_signals(signals.pre_save)
    def setUp(self):
        self.legacy_user = models.DataHubLegacyUser.objects.create(
            id=10, email="foo@bar.fizz", username="foobar", f_name="f_name",
            l_name="l_name", password="_h4rd;Pa_ss w-0Rd_", active=True,
            issuer="issuer", subject="subject")

        self.user = User.objects.create_user(
            "username", "email@email.email", "password")

        self.app = models.App.objects.create(
            app_id="app_id", id=10, app_name="app_name",
            app_token="app_token", user=self.user,
            legacy_user=self.legacy_user)

    def test_fields(self):
        permission = models.Permission.objects.create(
            id=10, legacy_user=self.legacy_user, user=self.user,
            app=self.app, access=True)

        self.assertEqual(permission.user, self.user)
        self.assertEqual(permission.legacy_user, self.legacy_user)
        self.assertEqual(permission.app, self.app)
        self.assertEqual(permission.access, True)

    def test_defaults(self):
        permission = models.Permission.objects.create(
            id=11, legacy_user=self.legacy_user, user=self.user, app=self.app)

        self.assertEqual(permission.access, False)
