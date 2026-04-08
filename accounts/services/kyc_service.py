"""
KYC service for business hours calculations and other utilities
"""

from datetime import datetime, timedelta
from django.utils import timezone
from accounts.constants.holiday_dates import HOLIDAYS_BY_COUNTRY

def is_business_day(date, country='US'):
        """
        Check if a given data is a business day (Monday - Friday, not holiday)
        """
        # Check if weekend
        if date.weekday() >= 5: # 5 = Saturday, 6 = Sunday
                return False
        
        # Check if holiday
        date_str = date.strftime('%y-%m-%d')
        holidays = HOLIDAYS_BY_COUNTRY.get(country, [])

        if date_str in holidays:
                return False
        return True

def calculate_business_hours_pending(submitted_at):
        """
        Calculate number of business hours pending since submission 
        """
        if not submitted_at:
                return 0
        now = timezone.now()
        current = submitted_at
        business_hours = 0

        # Simple calculation: Count business days * 8 hours
        while current.date() <= now.date():
                if is_business_day(current):
                        if current.date() == now.date():
                                #Same day: count hours difference
                                hours_diff = (now - current).total_seconds() / 3600
                                business_hours += min (hours_diff, 8) #Max  hours per day
                        else:
                                #Full business day
                                business_hours += 8 
                current += timedelta(days=1)
        
        return round(business_hours, 1)

