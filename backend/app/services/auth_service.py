import logging
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginRequest
from app.schemas.token import Token
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.core.settings import settings

logger = logging.getLogger(__name__)

class AuthService:
    """Service layer for authentication and user management."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def register(self, user_in: UserCreate) -> UserResponse:
        """Registers a new user after validating email uniqueness."""
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            logger.warning(f"Registration failed: Email {user_in.email} already exists.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        new_user = await self.user_repo.create_user(user_in)
        await self.session.commit()
        logger.info(f"User {new_user.email} registered successfully.")
        return UserResponse.model_validate(new_user)

    async def authenticate_user(self, login_data: LoginRequest) -> User:
        """Authenticates a user and verifies their status."""
        user = await self.user_repo.get_by_email(login_data.email)
        if not user or not verify_password(login_data.password, user.password_hash):
            logger.warning(f"Failed login attempt for {login_data.email}.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            logger.warning(f"Login attempt for inactive account: {login_data.email}.")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive account"
            )
            
        return user

    async def login(self, login_data: LoginRequest) -> Token:
        """Processes login and generates an access token."""
        user = await self.authenticate_user(login_data)
        access_token = create_access_token(subject=str(user.id))
        logger.info(f"User {user.email} logged in successfully.")
        return Token(
            access_token=access_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
