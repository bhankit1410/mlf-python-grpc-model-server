"""mlpkitsecurity.exceptions"""


class Error(Exception):
    """mlpkitsecurity base exception."""
    pass


class SecurityError(Error):
    """mlpkitsecurity domain exception."""

    def __init__(self, detail_info, *, root_cause=None, code=401):
        self.detail_info = detail_info
        self.root_cause = root_cause
        self.code = code

    def __repr__(self):
        return 'Error code {}: {}'.format(self.code, self.detail_info)


class TokenError(Error):
    """mlpkitsecurity domain exception"""

    def __init__(self, detail_info):
        self.detail_info = detail_info

    def __repr__(self):
        return 'Token error: {}'.format(self.detail_info)
