KYC_STATUSES = [
    ('NOT_STARTED', 'Not Started'),
    ('PENDING', 'Pending Verification'),
    ('VERIFIED', 'Verified'),
    ('REJECTED', 'Rejected'),
    ('EXPIRED', 'Expired'),
]
#Document types for KYC
DOCUMENT_TYPES=[
    ('DRIVERS_LICENSE', "Driver's License"),
    ('SELFIE', 'Selfie with ID'),
]

#Reasons for rejection
REJECTION_REASONS=[
    ('BLURRY', 'Image is blurry or unclear'),
    ('WRONG_FORMAT', 'Wrong file format(use JPG, PNG, or PDF)'),
    ('FILE_TOO_LARGE', 'File size exceeds 15MB limit'),
    ('EXPIRED', 'Document is expired'),
    ('NAME_MISMATCH', 'Name does not match account'),
    ('ADDRESS_MISMATCH', 'Address does not match'),
    ('SELFIE_MISMATCH', 'Selfie does not match ID photo'),
    ('INCOMPLETE', 'Incomplete document(missing parts)'),
    ('OTHER', 'Other reason'),
]

