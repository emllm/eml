from typing import Dict, Any
import re
from email.utils import parseaddr

import logging

logger = logging.getLogger(__name__)

class PEMLValidator:
    REQUIRED_HEADERS = ['From', 'To', 'Subject']
    
    def validate(self, data: Dict[str, Any]) -> None:
        """Validate PEML message data"""
        errors = []
        
        try:
            self._validate_required_headers(data, errors)
            self._validate_email_addresses(data, errors)
            self._validate_content_type(data, errors)
            
            if errors:
                raise ValueError("\n".join(errors))
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            raise

    def _validate_required_headers(self, data: Dict[str, Any], errors: list) -> None:
        """Check if all required headers are present"""
        headers = data.get('headers', {})
        for header in self.REQUIRED_HEADERS:
            if header not in headers:
                errors.append(f"Missing required header: {header}")

    def _validate_email_addresses(self, data: Dict[str, Any], errors: list) -> None:
        """Validate email addresses in From and To headers"""
        headers = data.get('headers', {})
        
        for field in ['From', 'To']:
            if field in headers:
                email_addr = parseaddr(headers[field])[1]
                if not self._is_valid_email(email_addr):
                    errors.append(f"Invalid email address in {field}: {email_addr}")

    def _validate_content_type(self, data: Dict[str, Any], errors: list) -> None:
        """Validate content types of attachments"""
        for i, attachment in enumerate(data.get('attachments', [])):
            content_type = attachment.get('content_type', '')
            if not content_type:
                errors.append(f"Attachment {i+1}: Missing content_type")
                continue
            
            if not re.match(r'^[a-z]+/[a-z0-9.-]+$', content_type, re.IGNORECASE):
                errors.append(f"Attachment {i+1}: Invalid content_type: {content_type}")

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Basic email validation"""
        if not email:
            return False
            
        # Basic regex check
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
