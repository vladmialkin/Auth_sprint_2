class ServiceBaseException(Exception):
    def __init__(self, *args):
        self.detail = args[0] if args else None


class ServiceConnectionError(ServiceBaseException):
    pass


class UnauthorizedError(ServiceBaseException):
    pass


class BadRequestError(ServiceBaseException):
    pass


class NotFoundError(ServiceBaseException):
    pass


class ResponseDecodeError(ServiceBaseException):
    pass
