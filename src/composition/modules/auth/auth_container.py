from dataclasses import dataclass

from application.auth.login_user_use_case import LoginUserUseCase
from application.auth.register_user_use_case import RegisterUserUseCase
from application.auth.resend_verification_use_case import (
    ResendVerificationUseCase,
)
from application.auth.reset_password_use_case import ResetPasswordUseCase
from application.auth.verify_email_use_case import VerifyEmailUseCase
from application.auth.verify_new_password_use_case import (
    VerifyNewPasswordUseCase,
)


@dataclass(frozen=True, slots=True)
class AuthContainer:
    register_user: RegisterUserUseCase
    login_user: LoginUserUseCase
    verify_email: VerifyEmailUseCase
    resend_verification: ResendVerificationUseCase
    reset_password: ResetPasswordUseCase
    verify_new_password: VerifyNewPasswordUseCase
