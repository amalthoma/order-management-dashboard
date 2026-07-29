from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginRequest
from app.schemas.token import Token
from app.services.auth_service import AuthService
from app.models.user import User
from app.utils.responses import StandardResponse

router = APIRouter()

@router.post(
    "/register",
    response_model=StandardResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user in the system."""
    auth_service = AuthService(db)
    user = await auth_service.register(user_in)
    return StandardResponse(
        data=user,
        message="User registered successfully",
        error=None
    )

@router.post(
    "/login",
    response_model=StandardResponse[Token],
    status_code=status.HTTP_200_OK,
    summary="Login and get access token"
)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate a user and return a JWT access token."""
    auth_service = AuthService(db)
    token = await auth_service.login(login_data)
    return StandardResponse(
        data=token,
        message="Login successful",
        error=None
    )

@router.get(
    "/me",
    response_model=StandardResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Get current user"
)
async def get_current_user_endpoint(
    current_user: User = Depends(get_current_user)
):
    """Retrieve details of the currently authenticated user."""
    return StandardResponse(
        data=UserResponse.model_validate(current_user),
        message="Current user retrieved successfully",
        error=None
    )
