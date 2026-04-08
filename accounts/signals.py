# imports the receiver function from user.py and metadata.py respectively 
from accounts.models.user import create_user_profile, save_user_profile
from accounts.models.metadata import create_user_metadata
"""
Signal Registry - Import all signal handlers here 
This file is imported in apps.py to register all signals    
"""
#Import signals from user.py
from accounts.models.user import create_user_profile, save_user_profile

#Import signals from metadata.py - THIS FIXES THE METADATA ISSUE!
from accounts.models.metadata import create_user_metadata 

# Import signals from kyc.py (will add in Phase 2)
# from accounts.models.kyc import create_kyc_record