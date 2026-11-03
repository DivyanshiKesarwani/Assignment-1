"""Application errors safe to report to the CLI user."""


class ReminderAgentError(Exception):
    """Base class for expected reminder-agent failures."""


class ModelConfigurationError(ReminderAgentError):
    """The local model configuration is absent or unusable."""


class ModelServiceError(ReminderAgentError):
    """The configured model service failed to return usable text."""


class ResponseParseError(ReminderAgentError):
    """The model response is not exactly one JSON object."""


class ResponseValidationError(ReminderAgentError):
    """The parsed model response violates the output contract."""
