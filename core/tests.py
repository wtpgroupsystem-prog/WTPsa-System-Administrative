from django.test import TestCase
from django.urls import reverse

class CoreViewsTests(TestCase):
    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
