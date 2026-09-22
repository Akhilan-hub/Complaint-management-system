from django.db import models
from django.contrib.auth.models import User

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('PENDING', 'Pending'),
        ('RESOLVED', 'Resolved'),
    ]

    AI_STATUS_CHOICES = [
        ('PASS', 'Pass'),
        ('FAIL', 'Fail'),
        ('UNCERTAIN', 'Uncertain'),
        ('PENDING', 'Pending Verification'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='complaints/')
    
    # First AI Verification results
    ai_verification_status = models.CharField(
        max_length=20,
        choices=AI_STATUS_CHOICES,
        default='PENDING'
    )
    ai_verification_reason = models.TextField(blank=True, default='')

    # Complaint overall status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='NEW'
    )

    # Resolution details (entered by Admin)
    resolution_description = models.TextField(blank=True, null=True)
    resolution_image = models.ImageField(upload_to='resolutions/', blank=True, null=True)
    
    # Second AI Verification results
    resolution_ai_status = models.CharField(
        max_length=20,
        choices=AI_STATUS_CHOICES,
        blank=True,
        null=True
    )
    resolution_ai_reason = models.TextField(blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Complaint #{self.id} - {self.title} ({self.status})"
