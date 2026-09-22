import os
from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from .models import Complaint
from .forms import (
    UserRegisterForm,
    UserLoginForm,
    ComplaintSubmissionForm,
    ResolutionSubmissionForm,
    ManualConfirmForm
)
from . import ai_service

# --- Helper Decorators & Mail Utility ---

def admin_required(view_func):
    """
    Decorator ensuring only staff/admin users can access the view.
    Redirects regular users to user dashboard with an error message.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_staff:
            messages.error(request, "Access denied: Admin privileges required.")
            return redirect('user_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def _send_resolution_email(complaint):
    """
    Triggers an email notification to the user upon complaint resolution.
    """
    if not complaint.user.email:
        return

    display_name = complaint.user.first_name or complaint.user.username
    subject = f"Complaint #{complaint.id} - Resolution Update"
    message = (
        f"Hello {display_name},\n\n"
        f"Your complaint has been resolved.\n\n"
        f"Complaint ID: #{complaint.id}\n"
        f"Title: {complaint.title}\n\n"
        f"Resolution Details:\n"
        f"{complaint.resolution_description}\n\n"
        f"Status: RESOLVED\n\n"
        f"Thank you,\n"
        f"Complaint Management Team"
    )
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[complaint.user.email],
            fail_silently=False
        )
    except Exception as e:
        print(f"Error sending resolution email for complaint #{complaint.id}: {e}")

# --- Authentication Views ---

def login_view(request):
    """
    Single login page for both regular Users and Admins.
    Redirects staff users to admin_dashboard and normal users to user_dashboard.
    """
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('user_dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username_input = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Support logging in by username or email
            user = authenticate(request, username=username_input, password=password)
            if user is None:
                try:
                    user_obj = User.objects.get(email=username_input)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect('admin_dashboard')
                return redirect('user_dashboard')
            else:
                messages.error(request, "Invalid username/email or password.")
    else:
        form = UserLoginForm()

    return render(request, 'complaints/login.html', {'form': form})

def register_view(request):
    """
    Registration view for regular users. Only asks for Full Name, Email, Password.
    Stores full name in user.first_name and email in user.email / user.username.
    """
    if request.user.is_authenticated:
        return redirect('user_dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=full_name
            )
            user.is_staff = False
            user.is_superuser = False
            user.save()

            messages.success(request, "Account registered successfully! You can now log in.")
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'complaints/register.html', {'form': form})

def logout_view(request):
    """
    Logs out the current user and redirects to login page.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

# --- User Dashboard & Complaint Views ---

@login_required
def user_dashboard_view(request):
    """
    User dashboard showing status counters and recent complaints.
    """
    if request.user.is_staff:
        return redirect('admin_dashboard')

    user_complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
    total_count = user_complaints.count()
    new_count = user_complaints.filter(status='NEW').count()
    pending_count = user_complaints.filter(status='PENDING').count()
    resolved_count = user_complaints.filter(status='RESOLVED').count()

    recent_complaints = user_complaints[:5]

    context = {
        'total_count': total_count,
        'new_count': new_count,
        'pending_count': pending_count,
        'resolved_count': resolved_count,
        'recent_complaints': recent_complaints,
    }
    return render(request, 'complaints/user_dashboard.html', context)

@login_required
def submit_complaint_view(request):
    """
    Complaint submission view:
    Collects title, description, and image, runs 1st AI verification, saves complaint as NEW.
    """
    if request.user.is_staff:
        messages.warning(request, "Admins cannot submit complaints. Switch to a user account.")
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = ComplaintSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.status = 'NEW'
            complaint.save()

            # Execute First AI Verification
            status_result, reason_result = ai_service.verify_complaint(
                title=complaint.title,
                description=complaint.description,
                image_path=complaint.image.path
            )

            complaint.ai_verification_status = status_result
            complaint.ai_verification_reason = reason_result
            complaint.save()

            messages.success(request, "Complaint submitted successfully.")
            return redirect('complaint_detail', pk=complaint.pk)
    else:
        form = ComplaintSubmissionForm()

    return render(request, 'complaints/submit_complaint.html', {'form': form})

@login_required
def my_complaints_view(request):
    """
    Lists all complaints submitted by the logged-in user with status filtering. Ordered newest first.
    """
    if request.user.is_staff:
        return redirect('admin_dashboard')

    status_filter = request.GET.get('status', 'all')

    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')

    if status_filter in ['NEW', 'PENDING', 'RESOLVED']:
        complaints = complaints.filter(status=status_filter)

    context = {
        'complaints': complaints,
        'status_filter': status_filter,
    }
    return render(request, 'complaints/my_complaints.html', context)

@login_required
def complaint_detail_view(request, pk):
    """
    Detail view for normal user (or admin inspecting complaint).
    """
    complaint = get_object_or_404(Complaint, pk=pk)

    # Security check: normal user can only view their own complaint
    if not request.user.is_staff and complaint.user != request.user:
        messages.error(request, "You are not authorized to view this complaint.")
        return redirect('user_dashboard')

    context = {
        'complaint': complaint
    }
    return render(request, 'complaints/complaint_detail.html', context)

@login_required
def delete_complaint_view(request, pk):
    """
    Deletes a single complaint.
    Users can delete their own complaint; Admins can delete any complaint.
    """
    complaint = get_object_or_404(Complaint, pk=pk)

    if not request.user.is_staff and complaint.user != request.user:
        messages.error(request, "You are not authorized to delete this complaint.")
        return redirect('user_dashboard')

    if request.method == 'POST':
        complaint_id = complaint.id
        if complaint.image and os.path.exists(complaint.image.path):
            try:
                os.remove(complaint.image.path)
            except Exception:
                pass
        if complaint.resolution_image and os.path.exists(complaint.resolution_image.path):
            try:
                os.remove(complaint.resolution_image.path)
            except Exception:
                pass

        complaint.delete()
        messages.success(request, f"Complaint #{complaint_id} deleted successfully.")

    if request.user.is_staff:
        return redirect('admin_dashboard')
    return redirect('my_complaints')

@login_required
def bulk_delete_complaints_view(request):
    """
    Deletes multiple selected complaints in bulk upon confirmation.
    """
    if request.method == 'POST':
        complaint_ids = request.POST.getlist('complaint_ids')
        if not complaint_ids:
            messages.warning(request, "No complaints selected for deletion.")
        else:
            if request.user.is_staff:
                complaints_to_delete = Complaint.objects.filter(id__in=complaint_ids)
            else:
                complaints_to_delete = Complaint.objects.filter(id__in=complaint_ids, user=request.user)

            count = complaints_to_delete.count()
            for c in complaints_to_delete:
                if c.image and os.path.exists(c.image.path):
                    try:
                        os.remove(c.image.path)
                    except Exception:
                        pass
                if c.resolution_image and os.path.exists(c.resolution_image.path):
                    try:
                        os.remove(c.resolution_image.path)
                    except Exception:
                        pass

            complaints_to_delete.delete()
            messages.success(request, f"{count} complaint(s) deleted successfully.")

    if request.user.is_staff:
        return redirect('admin_dashboard')
    return redirect('my_complaints')

# --- Admin Dashboard & Resolution Views ---

@admin_required
def admin_dashboard_view(request):
    """
    Admin dashboard displaying 4 summary cards, filter tabs, and clean complaint table.
    Always ordered newest first (-created_at).
    """
    status_filter = request.GET.get('status', 'all')

    all_complaints = Complaint.objects.all().order_by('-created_at')
    total_count = all_complaints.count()
    new_count = all_complaints.filter(status='NEW').count()
    pending_count = all_complaints.filter(status='PENDING').count()
    resolved_count = all_complaints.filter(status='RESOLVED').count()

    filtered_complaints = all_complaints
    if status_filter in ['NEW', 'PENDING', 'RESOLVED']:
        filtered_complaints = all_complaints.filter(status=status_filter)

    context = {
        'total_count': total_count,
        'new_count': new_count,
        'pending_count': pending_count,
        'resolved_count': resolved_count,
        'complaints': filtered_complaints,
        'status_filter': status_filter,
    }
    return render(request, 'complaints/admin_dashboard.html', context)

@admin_required
def admin_complaint_detail_view(request, pk):
    """
    Admin complaint detail view:
    Shows original complaint details, 1st AI check, "Take Complaint" button,
    resolution upload form, 2nd AI verification result, and confirmation options.
    """
    complaint = get_object_or_404(Complaint, pk=pk)
    resolution_form = ResolutionSubmissionForm()
    manual_form = ManualConfirmForm()

    context = {
        'complaint': complaint,
        'resolution_form': resolution_form,
        'manual_form': manual_form,
    }
    return render(request, 'complaints/admin_complaint_detail.html', context)

@admin_required
def admin_take_complaint_view(request, pk):
    """
    Moves complaint status from NEW to PENDING when admin takes responsibility.
    """
    complaint = get_object_or_404(Complaint, pk=pk)
    if complaint.status == 'NEW':
        complaint.status = 'PENDING'
        complaint.save()
        messages.success(request, f"Complaint #{complaint.id} status updated to PENDING.")
    else:
        messages.info(request, f"Complaint #{complaint.id} is already {complaint.status}.")

    return redirect('admin_complaint_detail', pk=complaint.pk)

@admin_required
def admin_submit_resolution_view(request, pk):
    """
    Admin uploads resolution description & evidence image inside complaint detail view.
    Triggers 2nd AI verification using Gemini.
    """
    complaint = get_object_or_404(Complaint, pk=pk)

    if complaint.status != 'PENDING':
        messages.error(request, "Resolution can only be submitted for complaints in PENDING status.")
        return redirect('admin_complaint_detail', pk=complaint.pk)

    if request.method == 'POST':
        form = ResolutionSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            complaint.resolution_description = form.cleaned_data['resolution_description']
            complaint.resolution_image = form.cleaned_data['resolution_image']
            complaint.save()

            # Execute Second AI Verification
            status_result, reason_result = ai_service.verify_resolution(
                title=complaint.title,
                description=complaint.description,
                original_image_path=complaint.image.path if complaint.image else None,
                resolution_description=complaint.resolution_description,
                resolution_image_path=complaint.resolution_image.path if complaint.resolution_image else None
            )

            complaint.resolution_ai_status = status_result
            complaint.resolution_ai_reason = reason_result
            complaint.save()

            if status_result == 'PASS':
                messages.success(request, "AI Verification Passed! Review evidence and confirm resolution.")
            else:
                messages.warning(request, f"AI Verification Result: {status_result}. Review options below.")

    return redirect('admin_complaint_detail', pk=complaint.pk)

@admin_required
def admin_resolve_complaint_view(request, pk):
    """
    Action endpoint when AI verification passed:
    Marks complaint as RESOLVED, updates timestamp, and sends email notification to user.
    """
    complaint = get_object_or_404(Complaint, pk=pk)

    if complaint.status != 'PENDING':
        messages.error(request, "Complaint must be PENDING to resolve.")
        return redirect('admin_complaint_detail', pk=complaint.pk)

    if complaint.resolution_ai_status != 'PASS':
        messages.error(request, "AI status is not PASS. Use manual authentication if required.")
        return redirect('admin_complaint_detail', pk=complaint.pk)

    complaint.status = 'RESOLVED'
    complaint.resolved_at = timezone.now()
    complaint.save()

    _send_resolution_email(complaint)
    messages.success(request, f"Complaint #{complaint.id} resolved successfully! Notification email sent.")

    return redirect('admin_complaint_detail', pk=complaint.pk)

@admin_required
def admin_manual_confirm_view(request, pk):
    """
    Action endpoint for Manual Confirmation (when AI is FAIL or UNCERTAIN):
    Requires admin password authentication on the backend to confirm resolution.
    """
    complaint = get_object_or_404(Complaint, pk=pk)

    if complaint.status != 'PENDING':
        messages.error(request, "Complaint must be PENDING to resolve.")
        return redirect('admin_complaint_detail', pk=complaint.pk)

    if request.method == 'POST':
        admin_password = request.POST.get('admin_password')

        # Backend security check: verify password of currently logged in admin user
        if not request.user.check_password(admin_password):
            messages.error(request, "Invalid admin credentials. Resolution cannot be confirmed.")
            return redirect('admin_complaint_detail', pk=complaint.pk)

        # Admin password verified successfully
        complaint.status = 'RESOLVED'
        complaint.resolved_at = timezone.now()
        complaint.save()

        _send_resolution_email(complaint)
        messages.success(
            request,
            f"Complaint #{complaint.id} resolved manually after admin password authentication! Notification email sent."
        )

    return redirect('admin_complaint_detail', pk=complaint.pk)
