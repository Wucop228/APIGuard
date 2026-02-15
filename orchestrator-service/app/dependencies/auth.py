from fastapi import Request, HTTPException, status


def get_current_user(request: Request) -> str:
    user_id: str | None = getattr(request.state, "user_id", None)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не авторизован",
        )

    return user_id


def get_optional_user(request: Request) -> str | None:
    return getattr(request.state, "user_id", None)