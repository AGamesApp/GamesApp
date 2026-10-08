"""
Custom logging filters to reduce noise from harmless CSRF warnings
"""
import logging

class CSRFRefererFilter(logging.Filter):
    """
    Filter to reduce noise from CSRF referer checking failures on public pages.
    
    These warnings are mostly from legitimate bots, crawlers, and direct navigation
    to public pages that don't have forms, so they're not real security concerns.
    """
    def filter(self, record):
        # Skip logging if it's a CSRF referer checking failure on root path
        message = record.getMessage()
        
        # Filter out bot/crawler CSRF warnings on public pages
        if (
            "Forbidden (Referer checking failed" in message and 
            "): /" in message and
            # Only filter root path warnings, keep warnings for other paths
            message.endswith("): /")
        ):
            return False
            
        # Allow all other log messages through
        return True