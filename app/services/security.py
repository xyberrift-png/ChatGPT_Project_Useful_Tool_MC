from __future__ import annotations


class SecurityService:
    @staticmethod
    def hash_password(password: str) -> str:
        import bcrypt

        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        import bcrypt

        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
        except ValueError:
            return False
