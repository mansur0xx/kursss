class AppError(Exception):
    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


class BadRequestError(AppError):
    pass


class AuthError(AppError):
    pass


UnauthorizedError = AuthError


class ForbiddenError(AppError):
    pass


class NotFoundError(AppError):
    pass


class ConflictError(AppError):
    pass
