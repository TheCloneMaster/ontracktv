# -*- coding: utf-8 -*-
######################################################################
#                                                                    #
# Part of EKIKA CORPORATION PRIVATE LIMITED (Website: ekika.co).     #
# See LICENSE file for full copyright and licensing details.         #
#                                                                    #
######################################################################

'''
Errors to consider:
-------------------
Invalid Input: The request data is not valid, typically due to missing or invalid attributes or relationships.
Invalid Query Parameter: One or more query parameters in the request are invalid or not supported by the server.
Resource Not Found: The requested resource does not exist on the server.
Resource Forbidden: The client is authenticated but does not have permission to access the requested resource.
Resource Locked: The requested resource is temporarily locked and cannot be modified.
Resource Already Exists: The client is trying to create a resource that already exists.
Resource Relationship Not Found: A relationship from a resource to another resource does not exist.
Resource Relationship Incorrect Type: The type of a related resource in a relationship is not as expected.
Invalid Relationship Update: The request tries to update a relationship in a way that is not allowed.
Invalid Linkage: The linkage data in a request does not meet the requirements of the server.
Sort Parameter Not Allowed: The server does not support sorting of the requested resource.
Pagination Not Allowed: The server does not support pagination of the requested resource.
Too Many Requests: The client has exceeded the rate limit for making requests to the server.
Unsupported Media Type: The server does not support the content type of the request.
Unsupported Version: The requested API version is not supported by the server.
Internal Server Error: An unexpected error occurred on the server.
Not Implemented: The requested feature or endpoint is not yet implemented.
Service Unavailable: The server is temporarily unable to handle the request (e.g., due to maintenance).
CORS (Cross-Origin Resource Sharing) Error: There is a violation of CORS policies in the request.
Custom Error: Custom application-specific errors can also be defined by the server.

Implementation Mapping:
-----------------------
404 (Not Found) is used for ResourceNotFoundException.
400 (Bad Request) is used for ValidationError, BadRequestException, InvalidQueryParameterException, and MissingRequiredFieldException.
401 (Unauthorized) is used for AuthenticationFailureException.
403 (Forbidden) is used for AuthorizationFailureException and CORSException.
415 (Unsupported Media Type) is used for UnsupportedMediaTypeException.
409 (Conflict) is used for ConflictException.
429 (Too Many Requests) is used for RateLimitExceededException.
500 (Internal Server Error) is used for ServerErrorException.
302 (Found) and 303 (See Other) are used for RedirectException and RedirectToAnotherResourceException.
501 (Not Implemented) is used for NotImplementedException.
503 (Service Unavailable) is used for ServiceUnavailableException.
423 (Locked) is used for LockedResourceException.


Help for developer:
-------------------
Exception Class                 | Status Code | Title                   | Detail                   | Custom Note
--------------------------------|-------------|-------------------------|---------------------------|-------------------------------------------------------
ResourceNotFoundException      | 404         | Not Found               | Resource not found       | Typically used for resource retrieval failures.
ValidationError                | 400         | Validation Error        | Invalid data             | Raised for data validation and formatting issues.
AuthenticationFailureException | 401         | Unauthorized            | Authentication failed    | Indicates failed authentication attempts.
AuthorizationFailureException  | 403         | Forbidden               | Access denied            | Indicates lack of authorization for an action.
BadRequestException             | 400         | Bad Request             | Malformed request        | General client error, often due to malformed requests.
UnsupportedMediaTypeException   | 415         | Unsupported Media Type  | Unsupported content type | Client sent an unsupported content type.
ConflictException              | 409         | Conflict                | Resource conflict        | Indicates a conflict preventing the requested action.
RateLimitExceededException      | 429         | Rate Limit Exceeded     | Too many requests        | Limit on requests exceeded; implement rate limiting.
ServerErrorException           | 500         | Internal Server Error   | Server error             | Unexpected server error; check server logs.
RedirectException               | 302 or 303  | Found or See Other      | Redirection              | Used for redirections, such as for authentication.
NotImplementedException        | 501         | Not Implemented         | Feature not implemented | Indicates unimplemented features.
ServiceUnavailableException    | 503         | Service Unavailable     | Temporarily unavailable | Used for maintenance or service outages.
UnsupportedVersionException    | 400         | Unsupported Version     | Unsupported API version  | Specify supported API versions in docs.
InvalidQueryParameterException | 400         | Invalid Query Parameter | Invalid parameter         | Detect and handle invalid query parameters.
MissingRequiredFieldException  | 400         | Missing Required Field  | Required field missing   | Client omitted a required field.
UnsupportedHTTPMethodException | 405         | Method Not Allowed      | HTTP method not supported | Check allowed methods for endpoints.
LockedResourceException         | 423         | Locked Resource         | Resource locked          | Resource is temporarily locked for modification.
RedirectToAnotherResourceException | 302 or 303 | Found or See Other    | Redirection              | Redirect to another resource or URL.
CORSException                   | 403 or 401  | Forbidden or Unauthorized | CORS policy violation  | Handle cross-origin resource sharing errors.
CustomApplicationException      | Variable    | Custom Title            | Custom detail            | Define custom exceptions based on your app's needs.

'''


class JsonAPIException(Exception):
    def __init__(self, title, detail, status_code, source_pointer=None, meta=None):
        """
        Base JSON:API Exception. Use this when need to convert to json api response.

        Params:
        title: (jsonapi: error.title) a short, human-readable summary of the problem that SHOULD NOT change from
            occurrence to occurrence of the problem, except for purposes of localization.
        detail: (jsonapi: error.detail) a human-readable explanation specific to this occurrence of the problem.
            Like title, this field's value can be localized.
        status_code: (error.status) the HTTP status code applicable to this problem, expressed as
            a string value. This SHOULD be provided.
        source_pointer: (error.source.pointer) a JSON Pointer [RFC6901] to the value in the request document that
            caused the error [e.g. "/data" for a primary data object, or "/data/attributes/title" for a specific
            attribute]. This MUST point to a value in the request document that exists; if it doesn't,
            the client SHOULD simply ignore the pointer.
        meta: (error.meta) a meta object containing non-standard meta-information about the error. (We can put the
            odoo's traceback for traceability)
        """
        super().__init__(detail)
        self.title = title
        self.detail = detail
        self.status_code = status_code
        self.source_pointer = source_pointer
        self.meta = meta

    def to_json_api_error(self):
        """Returns error(dict) based on information available in the instance."""
        error = {
            "status": str(self.status_code),
            "title": self.title,
            "detail": self.detail,
        }
        if self.source_pointer:
            error["source"] = {"pointer": self.source_pointer}
        if self.meta:
            error["meta"] = self.meta
        return error


class ResourceNotFoundException(JsonAPIException):
    def __init__(self, resource_type, resource_id, source_pointer=None, meta=None):
        detail = f"{resource_type} with ID {resource_id} not found"
        super().__init__("Not Found", detail, 404,
                         source_pointer=source_pointer, meta=meta)


class ValidationError(JsonAPIException):
    def __init__(self, detail, source_pointer=None, meta=None):
        super().__init__("Validation Error", detail, 400,
                         source_pointer=source_pointer, meta=meta)


class AuthenticationFailureException(JsonAPIException):
    def __init__(self, detail):
        super().__init__("Unauthorized", detail, 401)


class AuthorizationFailureException(JsonAPIException):
    def __init__(self, detail, source_pointer=None, meta=None):
        super().__init__("Forbidden", detail, 403,
                         source_pointer=source_pointer, meta=meta)


class BadRequestException(JsonAPIException):
    def __init__(self, detail, source_pointer=None, meta=None):
        super().__init__("Bad Request", detail, 400,
                         source_pointer=source_pointer, meta=meta)


class UnsupportedMediaTypeException(JsonAPIException):
    def __init__(self, source_pointer=None, meta=None):
        super().__init__("Unsupported Media Type", "Unsupported content type", 415,
                         source_pointer=source_pointer, meta=meta)


class ConflictException(JsonAPIException):
    def __init__(self, detail, source_pointer=None, meta=None):
        super().__init__("Conflict", detail, 409, source_pointer=source_pointer, meta=meta)


class RateLimitExceededException(JsonAPIException):
    def __init__(self, detail, source_pointer=None, meta=None):
        super().__init__("Rate Limit Exceeded", detail, 429,
                         source_pointer=source_pointer, meta=meta)


class ServerErrorException(JsonAPIException):
    def __init__(self, source_pointer=None, meta=None):
        super().__init__("Internal Server Error", "Unexpected server error", 500,
                         source_pointer=source_pointer, meta=meta)


class NotImplementedException(JsonAPIException):
    def __init__(self, source_pointer=None, meta=None):
        super().__init__("Not Implemented", "Feature not implemented", 501,
                         source_pointer=source_pointer, meta=meta)


class ServiceUnavailableException(JsonAPIException):
    def __init__(self, source_pointer=None, meta=None):
        super().__init__("Service Unavailable", "Temporarily unavailable", 503,
                         source_pointer=source_pointer, meta=meta)


class UnsupportedVersionException(JsonAPIException):
    def __init__(self, detail, source_pointer=None, meta=None):
        super().__init__("Unsupported Version", detail, 400,
                         source_pointer=source_pointer, meta=meta)


class InvalidQueryParameterException(JsonAPIException):
    def __init__(self, detail, source_pointer=None, meta=None):
        super().__init__("Invalid Query Parameter", detail, 400,
                         source_pointer=source_pointer, meta=meta)


class MissingRequiredFieldException(JsonAPIException):
    def __init__(self, field_name, source_pointer=None, meta=None):
        detail = f"Required field '{field_name}' is missing"
        super().__init__("Missing Required Field", detail, 400,
                         source_pointer=source_pointer, meta=meta)


class UnsupportedHTTPMethodException(JsonAPIException):
    def __init__(self, method, source_pointer=None, meta=None):
        detail = f"HTTP method '{method}' is not supported"
        super().__init__("Method Not Allowed", detail, 405,
                         source_pointer=source_pointer, meta=meta)


class LockedResourceException(JsonAPIException):
    def __init__(self, detail, source_pointer=None, meta=None):
        super().__init__("Locked Resource", detail, 423,
                         source_pointer=source_pointer, meta=meta)


class CORSException(JsonAPIException):
    def __init__(self, status_code, title, detail, source_pointer=None, meta=None):
        super().__init__(title, detail, status_code,
                         source_pointer=source_pointer, meta=meta)


# class RedirectException(JsonAPIException):
#     def __init__(self, status_code, location, title, detail):
#         super().__init__(title, detail, status_code)
#         self.location = location


# class RedirectToAnotherResourceException(JsonAPIException):
#     def __init__(self, status_code, location):
#         super().__init__("Found", "Redirect to another resource", status_code)
#         self.location = location
