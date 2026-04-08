"""
Admin tools for KYC approval
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from accounts.models.kyc import KYC, KYCDocument
from accounts.services.kyc_service import calculate_business_hours_pending

@staff_member_required
def kyc_dashboard(request):
        """
        Dashboard for admin to review pending KYC verifications
        only superusers can access this
        """

        if not request.user.is_superuser:
                messages.error(request, "Access denied. Superuser privileges required. ")
                return redirect('admin:index')
        
        # Get all pending KYC applications
        pending_kyc = KYC.objects.filter(status='PENDING').select_related('user')

        # Prepare dashboard data
        pending_list = []
        for kyc in pending_kyc:
                #Get documents
                documents = kyc.documents.all()

                #Calculate business hours pending
                hours_pending = calculate_business_hours_pending(kyc.submitted_at)
                is_overdue = hours_pending > 48 if kyc.submitted_at else False

                #Get failed attempts
                failed_attempts = kyc.user.kyc_failed_attempts.all()[:3] #Last 3 attempts

                pending_list.append({
                        'kyc': kyc,
                        'user': kyc.user,
                        'documents': documents,
                        'hours_pending': hours_pending,
                        'is_overdue' : is_overdue,
                        'failed_attempts' : failed_attempts,
                })

        context = {
                'pending_list' : pending_list,
                'total_pending' : len(pending_list),
                'overdue_count' : sum(1 for p in pending_list if p ['is_overdue']),
        }
        return render (request, 'admin/kyc_dashboard.html', context)

@staff_member_required
def kyc_review(request, kyc_id):
        """
        Review a sepcific kyc application
        """
        if not request.user.is_superuser:
                messages.error(request, "Access denied. Superuser privileges required. ")
                return redirect('admin : index')
        
        kyc = get_object_or_404(KYC, id = kyc_id)
        documents = kyc.documents.all()

        if request.method == 'POST':
                action = request.POST.get('action')

        if action == 'approve':
                #Mark all documents as approved
                for doc in documents:
                        doc.approve()

                #Mark KYC as verified
                kyc.mark_verified(request.user)

                # TODO: Send approval email to user
                messages.success(request, f"KYC for {kyc.user.username} approved successfully!")
                return redirect('accounts : kyc_dashboard')
        elif action == 'reject':
                # Get rejection reason form
                rejection_reason = request.POST.get('rejection_reason')
                rejection_details = request.POST.get('rejection_details', '')
                document_id = request.POST.get('document_id')

                if document_id:
                        doc = get_object_or_404(KYCDocument, id = document_id)
                        doc.reject(rejection_reason, rejection_details)

                        # Create failed attempt record
                        from accounts.models.kyc import KYCFailedAttempt
                        KYCFailedAttempt.objects.create(
                                user = kyc.user,
                                document_type = doc.document_type,
                                failure_reason = rejection_reason,
                                failure_details = rejection_details
                        )
                        messages.success(request, f"Document rejected for {kyc.user.username}")

                        #If all documents are rejected, mark KYC as rejected 
                        pending_docs = kyc.documents.filter(status = 'PENDING')
                        if pending_docs.count() == 0:
                                kyc.mark_rejected(request.user)
                                messages.info(request, f" All documents rejected. KYC marked as rejected.")

                        return redirect('accounts:kyc_dashboard')
                
                context = {
                        'kyc' : kyc,
                        'user' : kyc.user,
                        'documents' : documents,
                }
                return render(request, 'admin/kyc_review.html', context)
        
@staff_member_required
def check_overdue_kyc(request):
        """
        Check for overdue KYC applications and send alerts
        This can be called by a scheduled task
        """        
        pending_kyc = KYC.objects.filter(status='PENDING')
        overdue_list = []

        for kyc in pending_kyc:
                if kyc.submitted_at:
                        hours_pending = calculate_business_hours_pending(kyc.submitted_at)
                        if hours_pending > 48:
                                overdue_list.append(kyc)
                                #TODO: Send alert to admin email

        return overdue_list





