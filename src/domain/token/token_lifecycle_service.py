from datetime import datetime, timedelta, timezone

from security.token_crypto import TokenCrypto


class TokenLifecycleService:
    def create_token(
        self,
        session,
        user_id,
        *,
        token_crypto: TokenCrypto,
        repository,
        ttl: timedelta,
    ):
        expires_at = datetime.now(timezone.utc) + ttl
        raw_token = token_crypto.generate_token()
        token_hash = token_crypto.hash_token(raw_token)

        repository.deactivate_all_user_tokens(session, user_id)
        repository.add_token(session, user_id, token_hash, expires_at)

        return raw_token
