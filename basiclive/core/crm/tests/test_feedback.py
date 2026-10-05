from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from basiclive.core.crm.models import Feedback, SupportArea, LikertScale
from basiclive.core.lims.models import Beamline, Project, Session
from basiclive.utils.encrypt import decrypt, encrypt

User = get_user_model()


class FeedbackTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.pi = User.objects.create_user(username="prof_jones", email="jones@college.edu")
        self.project = Project.objects.create(name="archaeology-01", pi=self.pi)
        self.beamline = Beamline.objects.create(name="BioCAT", acronym="08B1-1")
        self.session = Session.objects.create(project=self.project, beamline=self.beamline, name="run-alpha")

    def test_session_feedback_key_generation_and_decryption(self):
        key = self.session.feedback_key()
        self.assertIsInstance(key, str)
        decrypted = decrypt(key)
        self.assertEqual(decrypted, f"{self.project.name}:{self.session.name}")

    def test_feedback_create_view_valid_key(self):
        url = reverse('session-feedback', kwargs={'key': self.session.feedback_key()})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('form', resp.context)
        self.assertEqual(resp.context['form'].initial['session'], self.session)

    def test_feedback_create_view_invalid_key_404(self):
        url = reverse('session-feedback', kwargs={'key': 'invalid-malformed-key'})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_feedback_create_view_nonexistent_session_404(self):
        fake_key = encrypt("nonexistent-proj:nonexistent-sess")
        url = reverse('session-feedback', kwargs={'key': fake_key})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

    def test_feedback_survey_submission(self):
        scale = LikertScale.objects.create(
            statement="How satisfied were you?",
            worst="Very Dissatisfied",
            worse="Dissatisfied",
            better="Satisfied",
            best="Very Satisfied"
        )
        area = SupportArea.objects.create(name="Beamline Software", user_feedback=True, scale=scale)

        url = reverse('session-feedback', kwargs={'key': self.session.feedback_key()})
        post_data = {
            'session': self.session.pk,
            'comments': 'Great remote experiment session!',
            'contact': True,
            'beamline-software': ['2'],
        }
        resp = self.client.post(url, data=post_data)
        self.assertEqual(resp.status_code, 302)

        feedback = Feedback.objects.filter(session=self.session).first()
        self.assertIsNotNone(feedback)
        self.assertEqual(feedback.comments, 'Great remote experiment session!')
        self.assertTrue(feedback.contact)
        self.assertEqual(feedback.session.project.name, 'archaeology-01')
