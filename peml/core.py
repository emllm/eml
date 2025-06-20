from typing import Dict, Any, Optional
import email
from email.message import EmailMessage
from email.parser import BytesParser
from email.policy import default
import json

class PEMLError(Exception):
    """Base exception for PEML errors"""
    pass

class PEMLParser:
    def __init__(self, encoding: str = 'utf-8'):
        self.encoding = encoding
        self.parser = BytesParser(policy=default)

    def parse(self, peml_content: str) -> EmailMessage:
        """Parse PEML content into an EmailMessage object"""
        try:
            message = self.parser.parsebytes(peml_content.encode(self.encoding))
            return message
        except Exception as e:
            raise PEMLError(f"Error parsing PEML content: {str(e)}")

    def to_dict(self, message: EmailMessage) -> Dict[str, Any]:
        """Convert EmailMessage to dictionary format"""
        try:
            result = {
                'headers': dict(message.items()),
                'body': message.get_body(preferencelist=('plain', 'html')).get_content(),
                'attachments': []
            }
            
            for part in message.iter_attachments():
                attachment = {
                    'content_type': part.get_content_type(),
                    'filename': part.get_filename(),
                    'content': part.get_content()
                }
                # Handle binary content
                if part.get_content_maintype() != 'text':
                    attachment['content'] = part.get_payload(decode=True)
                result['attachments'].append(attachment)
            
            return result
        except Exception as e:
            raise PEMLError(f"Error converting message to dict: {str(e)}")

    def from_dict(self, data: Dict[str, Any]) -> EmailMessage:
        """Create EmailMessage from dictionary"""
        try:
            message = EmailMessage()
            
            # Set headers
            for key, value in data.get('headers', {}).items():
                message[key] = value
            
            # Set body
            if 'body' in data:
                message.set_content(data['body'])
            
            # Add attachments
            for attachment in data.get('attachments', []):
                content = attachment['content']
                # Handle binary content
                if isinstance(content, bytes):
                    message.add_attachment(
                        content,
                        maintype=attachment['content_type'].split('/')[0],
                        subtype=attachment['content_type'].split('/')[1],
                        filename=attachment.get('filename'),
                        disposition='attachment'
                    )
                else:
                    message.add_attachment(
                        str(content),
                        maintype=attachment['content_type'].split('/')[0],
                        subtype=attachment['content_type'].split('/')[1],
                        filename=attachment.get('filename'),
                        disposition='attachment'
                    )
            
            return message
        except Exception as e:
            raise PEMLError(f"Error creating message from dict: {str(e)}")
