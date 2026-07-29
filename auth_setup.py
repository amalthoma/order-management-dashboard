import os

base_dir = r"C:\Users\Amal Thomas\.gemini\antigravity\scratch\order_management"

files = {
    "backend/app/utils/responses.py": """from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    \"\"\"Standard API response format.\"\"\"
    data: Optional[T] = None
    message: str = "Success"
    error: Optional[Any] = None
""",
    "backend/app/models/__init__.py": """from app.database.base import Base
from app.models.user import User

__all__ = ["Base", "User"]
""",
    "backend/app/models/user.py": """import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class User(Base):
    \"\"\"Database model for users.\"\"\"
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
""",
    "backend/app/schemas/user.py": """import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    \"\"\"Base schema for user data.\"\"\"
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    \"\"\"Schema for creating a new user.\"\"\"
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long.")

class UserResponse(UserBase):
    \"\"\"Schema for returning user data.\"\"\"
    id: uuid.UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
""",
    "backend/app/schemas/auth.py": """from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    \"\"\"Schema for login request.\"\"\"
    email: EmailStr
    password: str
""",
    "backend/app/schemas/token.py": """from pydantic import BaseModel

class Token(BaseModel):
    \"\"\"Schema for access token.\"\"\"
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    \"\"\"Schema for token payload.\"\"\"
    sub: str | None = None
""",
    "backend/app/core/security.py": """from datetime import datetime, timedelta, timezone
from typing import Any
from passlib.context import CryptContext
from jose import jwt
from app.core.settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    \"\"\"Verifies a plain password against the hashed password.\"\"\"
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    \"\"\"Generates a bcrypt hash for the given password.\"\"\"
    return pwd_context.hash(password)

def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    \"\"\"Generates a JWT access token for the given subject.\"\"\"
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt
""",
    "backend/app/repositories/user_repository.py": """import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

class UserRepository:
    \"\"\"Repository for managing User database operations.\"\"\"
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> Optional[User]:
        \"\"\"Retrieve a user by their email address.\"\"\"
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        \"\"\"Retrieve a user by their UUID.\"\"\"
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def create_user(self, user_in: UserCreate) -> User:
        \"\"\"Create a new user with a hashed password.\"\"\"
        db_user = User(
            email=user_in.email,
            full_name=user_in.full_name,
            password_hash=get_password_hash(user_in.password),
        )
        self.session.add(db_user)
        await self.session.flush()
        await self.session.refresh(db_user)
        return db_user
""",
    "backend/app/services/auth_service.py": """import logging
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginRequest
from app.schemas.token import Token
from app.core.security import verify_password, create_access_token
from app.models.user import User

logger = logging.getLogger(__name__)

class AuthService:
    \"\"\"Service layer for authentication and user management.\"\"\"
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def register(self, user_in: UserCreate) -> UserResponse:
        \"\"\"Registers a new user after validating email uniqueness.\"\"\"
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
        \"\"\"Authenticates a user and verifies their status.\"\"\"
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
        \"\"\"Processes login and generates an access token.\"\"\"
        user = await self.authenticate_user(login_data)
        access_token = create_access_token(subject=str(user.id))
        logger.info(f"User {user.email} logged in successfully.")
        return Token(access_token=access_token)
""",
    "backend/app/api/dependencies.py": """import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.core.settings import settings
from app.schemas.token import TokenPayload
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login"
)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    \"\"\"Dependency to retrieve the currently authenticated user.\"\"\"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        token_data = TokenPayload(sub=user_id_str)
    except JWTError:
        raise credentials_exception
        
    try:
        if token_data.sub is None:
            raise credentials_exception
        user_id = uuid.UUID(token_data.sub)
    except ValueError:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if not user:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Inactive account"
        )
        
    return user

__all__ = ["get_db", "get_current_user"]
""",
    "backend/app/api/v1/endpoints/auth.py": """from fastapi import APIRouter, Depends, status
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
    \"\"\"Register a new user in the system.\"\"\"
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
    \"\"\"Authenticate a user and return a JWT access token.\"\"\"
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
    \"\"\"Retrieve details of the currently authenticated user.\"\"\"
    return StandardResponse(
        data=UserResponse.model_validate(current_user),
        message="Current user retrieved successfully",
        error=None
    )
""",
    "backend/app/api/v1/router.py": """from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.api.dependencies import get_db
from app.database.session import check_database_health
from app.core.settings import settings
from app.api.v1.endpoints import auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

@api_router.get("/health", response_model=dict, tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    \"\"\"Health check endpoint.\"\"\"
    is_db_healthy = await check_database_health()
    return {
        "status": "healthy" if is_db_healthy else "degraded",
        "version": settings.VERSION,
        "database": "connected" if is_db_healthy else "disconnected",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
""",
    "backend/alembic/env.py": """import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from app.core.settings import settings
from app.database.base import Base
import app.models  # noqa

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
"""
}

for path, content in files.items():
    full_path = os.path.join(base_dir, path.replace('/', os.sep))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Authentication module files generated successfully.")
