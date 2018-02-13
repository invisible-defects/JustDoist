"""
Exception for responses with HTTP status >= 500
"""
class ServiceUnavailable(Exception):
    pass


"""
Errors returned by the Sync API (sync_status)
"""
class SyncError(Exception):
    pass
