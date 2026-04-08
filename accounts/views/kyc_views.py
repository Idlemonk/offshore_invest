"""
KYC Views - Document upload, status checking, and verification flow
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.models.kyc import KYC, KYCDocument, KYCFailedAttempt
import os


def validate_document(file, doc_type):
    """Validate uploaded document"""
    # Check file size (max 15MB)
    if file.size > 15 * 1024 * 1024:
        return False, "FILE_TOO_LARGE"
    
    # Check file extension
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.pdf']:
        return False, "WRONG_FORMAT"
    
    # For selfie, extra validation (must be image, not PDF)
    if doc_type == 'SELFIE' and ext == '.pdf':
        return False, "WRONG_FORMAT"
    
    return True, None


@login_required
def kyc_wizard(request):
    """Step-by-step KYC document upload wizard"""
    # Get or create KYC record
    kyc, created = KYC.objects.get_or_create(user=request.user)
    
    # Check if already verified
    if kyc.status == 'VERIFIED':
        messages.info(request, "You are already verified!")
        return redirect('accounts:homepage')
    
    # Check if verification is pending
    if kyc.status == 'PENDING':
        messages.info(request, "Your verification is already pending review. We'll notify you within 48 hours.")
        return redirect('accounts:homepage')
    
    # Get existing documents
    # Only redirect if both documents are already uploaded
    license_doc = kyc.documents.filter(document_type='DRIVERS_LICENSE', status='PENDING').first()
    selfie_doc = kyc.documents.filter(document_type='SELFIE', status='PENDING').first()
    
    #If both documents have been uploaded. then show the pending message
    if license_doc and selfie_doc and kyc.status == 'PENDING':
        messages.info(request, "Your documents are already submitted and pending review.")
        return redirect('accounts:homepage')


    # Handle POST request (file uploads)
    if request.method == 'POST':
        step = request.POST.get('step')
        
        if step == 'license':
            if 'license_file' not in request.FILES:
                messages.error(request, "Please select a file to upload.")
                return redirect('accounts:kyc_wizard')
            
            file = request.FILES['license_file']
            is_valid, error = validate_document(file, 'DRIVERS_LICENSE')
            
            if not is_valid:
                KYCFailedAttempt.objects.create(
                    user=request.user,
                    document_type='DRIVERS_LICENSE',
                    failure_reason=error,
                    failure_details=f"File: {file.name}"
                )
                messages.error(request, f"Invalid file: {error}")
                return redirect('accounts:kyc_wizard')
            
            KYCDocument.objects.create(
                kyc=kyc,
                document_type='DRIVERS_LICENSE',
                file=file,
                file_name=file.name,
                file_size=file.size,
                status='PENDING'
            )
            
            if kyc.status == 'NOT_STARTED':
                kyc.status = 'PENDING'
                kyc.submitted_at = timezone.now()
                kyc.save()
            
            messages.success(request, "Driver's license uploaded successfully! Now upload your selfie.")
            return redirect('accounts:kyc_wizard')
        
        elif step == 'selfie':
            if 'selfie_file' not in request.FILES:
                messages.error(request, "Please select a file to upload.")
                return redirect('accounts:kyc_wizard')
            
            file = request.FILES['selfie_file']
            is_valid, error = validate_document(file, 'SELFIE')
            
            if not is_valid:
                KYCFailedAttempt.objects.create(
                    user=request.user,
                    document_type='SELFIE',
                    failure_reason=error,
                    failure_details=f"File: {file.name}"
                )
                messages.error(request, f"Invalid file: {error}")
                return redirect('accounts:kyc_wizard')
            
            KYCDocument.objects.create(
                kyc=kyc,
                document_type='SELFIE',
                file=file,
                file_name=file.name,
                file_size=file.size,
                status='PENDING'
            )
            
            if not kyc.submitted_at:
                kyc.submitted_at = timezone.now()
                kyc.save()
            
            messages.success(request, "Selfie uploaded successfully! Your documents are now pending review.")
            return redirect('accounts:homepage')  # ← Redirect to homepage instead of kyc_status
        
        # Fallback for invalid step
        messages.error(request, "Invalid request.")
        return redirect('accounts:homepage')
    
    # Handle GET request - show appropriate step
    if not license_doc and not selfie_doc:
        return render(request, 'accounts/kyc_license.html', {
            'step': 1,
            'total_steps': 2,
        })
    elif license_doc and not selfie_doc:
        return render(request, 'accounts/kyc_selfie.html', {
            'step': 2,
            'total_steps': 2,
            'license_uploaded': license_doc,
        })
    else:
        # Both documents uploaded, show pending message
        messages.info(request, "Your documents have been submitted and are pending review.")
        return redirect('accounts:homepage')


@login_required
def kyc_status(request):
    """Show current KYC status"""
    try:
        kyc = request.user.kyc
        documents = kyc.documents.all()
        failed_attempts = KYCFailedAttempt.objects.filter(user=request.user)
    except:
        kyc = None
        documents = []
        failed_attempts = []
    
    context = {
        'kyc': kyc,
        'documents': documents,
        'failed_attempts': failed_attempts,
    }
    return render(request, 'accounts/kyc_status.html', context)


@login_required
def kyc_retry(request):
    """Retry KYC after rejection"""
    try:
        kyc = request.user.kyc
    except:
        messages.error(request, "No KYC application found.")
        return redirect('accounts:homepage')
    
    if kyc.status != 'REJECTED':
        messages.error(request, "You can only retry after a rejection.")
        return redirect('accounts:homepage')
    
    rejected_docs = kyc.documents.filter(status='REJECTED')
    
    if request.method == 'POST':
        for doc in rejected_docs:
            file_key = f"retry_{doc.document_type.lower()}"
            if file_key in request.FILES:
                file = request.FILES[file_key]
                is_valid, error = validate_document(file, doc.document_type)
                
                if not is_valid:
                    KYCFailedAttempt.objects.create(
                        user=request.user,
                        document_type=doc.document_type,
                        failure_reason=error,
                        failure_details=f"Retry attempt"
                    )
                    messages.error(request, f"Invalid file: {error}")
                    return redirect('accounts:kyc_retry')
                
                doc.file = file
                doc.file_name = file.name
                doc.file_size = file.size
                doc.status = 'PENDING'
                doc.rejection_reason = None
                doc.rejection_details = ''
                doc.reviewed_at = None
                doc.save()
        
        kyc.status = 'PENDING'
        kyc.submitted_at = timezone.now()
        kyc.save()
        
        messages.success(request, "Documents resubmitted successfully!")
        return redirect('accounts:homepage')
    
    context = {
        'kyc': kyc,
        'rejected_docs': rejected_docs,
    }
    return render(request, 'accounts/kyc_retry.html', context)
