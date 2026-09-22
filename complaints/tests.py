import io
from PIL import Image
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from complaints.models import Complaint

def generate_test_image(filename='test_image.png'):
    file_obj = io.BytesIO()
    image = Image.new('RGB', (100, 100), color=(73, 109, 137))
    image.save(file_obj, 'png')
    file_obj.seek(0)
    return SimpleUploadedFile(filename, file_obj.read(), content_type='image/png')

class ComplaintSystemTestCase(TestCase):
    def setUp(self):
        # Create regular user and admin user
        self.regular_user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='userpass123'
        )
        self.admin_user = User.objects.create_superuser(
            username='testadmin',
            email='admin@example.com',
            password='adminpass123'
        )

        self.client = Client()

    def test_single_login_routing(self):
        """Test single login page routes user and admin to their respective dashboards."""
        # Test regular user login
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'userpass123'
        })
        self.assertRedirects(response, reverse('user_dashboard'))

        self.client.logout()

        # Test admin user login
        response = self.client.post(reverse('login'), {
            'username': 'testadmin',
            'password': 'adminpass123'
        })
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_role_security_authorization(self):
        """Test regular user cannot access admin dashboard or administrative actions."""
        self.client.login(username='testuser', password='userpass123')
        
        response = self.client.get(reverse('admin_dashboard'))
        self.assertRedirects(response, reverse('user_dashboard'))

    def test_complaint_lifecycle_and_take_complaint(self):
        """Test user submitting a complaint, initial status NEW, and admin taking it to PENDING."""
        self.client.login(username='testuser', password='userpass123')
        
        test_img = generate_test_image('complaint.png')
        response = self.client.post(reverse('submit_complaint'), {
            'title': 'Broken Streetlight',
            'description': 'The streetlight near house #42 is flickering and dark.',
            'image': test_img
        })
        
        # Verify complaint created with NEW status
        complaint = Complaint.objects.get(title='Broken Streetlight')
        self.assertEqual(complaint.status, 'NEW')
        self.assertEqual(complaint.user, self.regular_user)
        self.assertIn(complaint.ai_verification_status, ['PASS', 'FAIL', 'UNCERTAIN', 'PENDING'])

        # Admin logs in and takes the complaint
        self.client.login(username='testadmin', password='adminpass123')
        response = self.client.post(reverse('admin_take_complaint', kwargs={'pk': complaint.pk}))
        
        complaint.refresh_from_db()
        self.assertEqual(complaint.status, 'PENDING')

    def test_admin_manual_confirm_password_security(self):
        """Test manual resolution confirmation requires valid admin password authentication."""
        # Create a pending complaint
        test_img = generate_test_image('issue.png')
        complaint = Complaint.objects.create(
            user=self.regular_user,
            title='Pothole on Main St',
            description='Large pothole causing traffic obstruction.',
            image=test_img,
            status='PENDING',
            resolution_ai_status='UNCERTAIN',
            resolution_ai_reason='Resolution evidence inconclusive.'
        )

        self.client.login(username='testadmin', password='adminpass123')

        # Attempt manual confirm with WRONG password
        response = self.client.post(
            reverse('admin_manual_confirm', kwargs={'pk': complaint.pk}),
            {'admin_password': 'wrongpassword'}
        )
        complaint.refresh_from_db()
        self.assertEqual(complaint.status, 'PENDING') # Should remain PENDING

        # Attempt manual confirm with CORRECT password
        response = self.client.post(
            reverse('admin_manual_confirm', kwargs={'pk': complaint.pk}),
            {'admin_password': 'adminpass123'}
        )
        complaint.refresh_from_db()
        self.assertEqual(complaint.status, 'RESOLVED')
        self.assertIsNotNone(complaint.resolved_at)

        # Check email dispatches to user
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Complaint #', mail.outbox[0].subject)
        self.assertIn('RESOLVED', mail.outbox[0].body)
