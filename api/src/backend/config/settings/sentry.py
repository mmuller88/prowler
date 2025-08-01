import sentry_sdk
from config.env import env

IGNORED_EXCEPTIONS = [
    # Provider is not connected due to credentials errors
    "is not connected",
    "ProviderConnectionError",
    # Authentication Errors from AWS
    "InvalidToken",
    "AccessDeniedException",
    "AuthorizationErrorException",
    "UnrecognizedClientException",
    "UnauthorizedOperation",
    "AuthFailure",
    "InvalidClientTokenId",
    "AWSInvalidProviderIdError",
    "InternalServerErrorException",
    "AccessDenied",
    "No Shodan API Key",  # Shodan Check
    "RequestLimitExceeded",  # For now, we don't want to log the RequestLimitExceeded errors
    "ThrottlingException",
    "Rate exceeded",
    "SubscriptionRequiredException",
    "UnknownOperationException",
    "OptInRequired",
    "ReadTimeout",
    "LimitExceeded",
    "ConnectTimeoutError",
    "ExpiredToken",
    "IncompleteSignature",
    "RegionDisabledException",
    "TooManyRequestsException",
    "SignatureDoesNotMatch",
    "InvalidParameterValueException",
    "InvalidInputException",
    "ValidationException",
    "AWSSecretAccessKeyInvalidError",
    "InvalidAction",
    "InvalidRequestException",
    "RequestExpired",
    "ConnectionClosedError",
    "MaxRetryError",
    "AWSAccessKeyIDInvalidError",
    "AWSSessionTokenExpiredError",
    "EndpointConnectionError",  # AWS Service is not available in a region
    # The following comes from urllib3: eu-west-1 -- HTTPClientError[126]: An HTTP Client raised an
    # unhandled exception: AWSHTTPSConnectionPool(host='hostname.s3.eu-west-1.amazonaws.com', port=443): Pool is closed.
    "Pool is closed",
    # Authentication Errors from GCP
    "ClientAuthenticationError",
    "AuthorizationFailed",
    "Reauthentication is needed",
    "Permission denied to get service",
    "API has not been used in project",
    "HttpError 404 when requesting",
    "HttpError 403 when requesting",
    "HttpError 400 when requesting",
    "GCPNoAccesibleProjectsError",
    # Authentication Errors from Azure
    "ClientAuthenticationError",
    "AuthorizationFailed",
    "Subscription Not Registered",
    "AzureNotValidClientIdError",
    "AzureNotValidClientSecretError",
    "AzureNotValidTenantIdError",
    "AzureInvalidProviderIdError",
    "AzureTenantIdAndClientSecretNotBelongingToClientIdError",
    "AzureTenantIdAndClientIdNotBelongingToClientSecretError",
    "AzureClientIdAndClientSecretNotBelongingToTenantIdError",
    "AzureHTTPResponseError",
    "Error with credentials provided",
]


def before_send(event, hint):
    """
    before_send handles the Sentry events in order to send them or not
    """
    # Ignore logs with the ignored_exceptions
    # https://docs.python.org/3/library/logging.html#logrecord-objects
    if "log_record" in hint:
        log_msg = hint["log_record"].msg
        log_lvl = hint["log_record"].levelno

        # Handle Error and Critical events and discard the rest
        if log_lvl <= 40 and any(ignored in log_msg for ignored in IGNORED_EXCEPTIONS):
            return None  # Explicitly return None to drop the event

    # Ignore exceptions with the ignored_exceptions
    if "exc_info" in hint and hint["exc_info"]:
        exc_value = str(hint["exc_info"][1])
        if any(ignored in exc_value for ignored in IGNORED_EXCEPTIONS):
            return None  # Explicitly return None to drop the event

    return event


sentry_sdk.init(
    dsn=env.str("DJANGO_SENTRY_DSN", ""),
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    before_send=before_send,
    send_default_pii=True,
    _experiments={
        # Set continuous_profiling_auto_start to True
        # to automatically start the profiler on when
        # possible.
        "continuous_profiling_auto_start": True,
    },
    attach_stacktrace=True,
    ignore_errors=IGNORED_EXCEPTIONS,
)
