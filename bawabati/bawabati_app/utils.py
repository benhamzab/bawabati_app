from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import IntegrityError
from django.http import Http404
import logging

# Initialize logger
logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    """
    Optimized Custom Exception Handler for Django REST Framework.
    This ensures all API errors follow a standardized format.
    """
    # Call DRF's default exception handler to get the response
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            'success': False,
            'message': get_error_message(exc),
            'code': response.status_code
        }

        # For validation errors, add the full error details
        if isinstance(exc, ValidationError):
            response.data['errors'] = exc.detail

        return response

    # Custom handling for common Django exceptions
    if isinstance(exc, ValidationError):
        return api_error_response("Validation error", status.HTTP_400_BAD_REQUEST)

    if isinstance(exc, PermissionDenied):
        return api_error_response("Permission denied", status.HTTP_403_FORBIDDEN)

    if isinstance(exc, Http404):
        return api_error_response("Resource not found", status.HTTP_404_NOT_FOUND)

    if isinstance(exc, IntegrityError):
        return api_error_response("Database integrity error", status.HTTP_400_BAD_REQUEST)

    # Log any unhandled exceptions
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    # For unhandled exceptions, return a generic 500 error
    return api_error_response("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_error_message(exc):
    """
    Extracts a user-friendly error message from an exception.
    """
    if hasattr(exc, 'detail'):
        if isinstance(exc.detail, dict):
            # Extract the first validation error message
            first_key = next(iter(exc.detail), None)
            if first_key:
                first_error = exc.detail[first_key]
                if isinstance(first_error, list) and len(first_error) > 0:
                    return f"{first_key}: {first_error[0]}"
                return str(first_error)

        elif isinstance(exc.detail, list) and len(exc.detail) > 0:
            return str(exc.detail[0])

        return str(exc.detail)
    
    # Default message for unknown exceptions
    return str(exc) or "An unknown error occurred"


def api_error_response(message, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Returns a standardized error response for API errors.
    """
    return Response({
        "success": False,
        "message": message,
        "code": status_code
    }, status=status_code)
