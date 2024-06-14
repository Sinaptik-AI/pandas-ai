import datetime
import uuid
from enum import Enum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from core.database import Base


class OrganizationRole:
    MEMBER = "MEMBER"
    ADMIN = "ADMIN"
    OWNER = "OWNER"


class DataframeLoadStatus(Enum):
    DONE = "DONE"
    IN_PROGRESS = "IN_PROGRESS"
    FAILED = "FAILED"


class ConnectorType(Enum):
    CSV = "CSV"


class User(Base):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), index=True, unique=True)
    first_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    password = Column(String(255))
    verified = Column(Boolean, default=False)
    last_name = Column(String(255), nullable=True)

    datasets = relationship("Dataset", back_populates="user")
    connectors = relationship("Connector", back_populates="user")
    memberships = relationship(
        "OrganizationMembership", back_populates="user", lazy="selectin"
    )
    spaces = relationship("Workspace", back_populates="user")
    user_spaces = relationship("UserSpace", back_populates="user")


class Organization(Base):
    __tablename__ = "organization"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, index=True)
    url = Column(String, nullable=True)
    is_default = Column(Boolean, default=False)
    settings = Column(JSON, nullable=True)

    api_keys = relationship("APIKeys", back_populates="organization")
    datasets = relationship("Dataset", back_populates="organization")
    members = relationship(
        "OrganizationMembership", back_populates="organization", lazy="selectin"
    )
    workspaces = relationship("Workspace", back_populates="organization")


class APIKeys(Base):
    __tablename__ = "api_keys"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"))
    api_key = Column(String(255))

    organization = relationship("Organization", back_populates="api_keys")


class OrganizationMembership(Base):
    __tablename__ = "organization_membership"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"))
    role = Column(String, default=OrganizationRole.MEMBER)
    verified = Column(Boolean, default=True)

    organization = relationship("Organization", back_populates="members", lazy="joined")
    user = relationship("User", back_populates="memberships", lazy="joined")


class Dataset(Base):
    __tablename__ = "dataset"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String)
    table_name = Column(String)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    head = Column(JSON, nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"))
    connector_id = Column(UUID(as_uuid=True), ForeignKey("connector.id"))
    field_descriptions = Column(JSON, nullable=True)
    filterable_columns = Column(JSON, nullable=True)

    user = relationship("User", back_populates="datasets")
    organization = relationship("Organization", back_populates="datasets")
    connector = relationship("Connector", back_populates="datasets", lazy="joined")
    dataset_spaces = relationship("DatasetSpace", back_populates="dataset")


class Connector(Base):
    __tablename__ = "connector"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    type = Column(String, nullable=False)
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))

    user = relationship("User", back_populates="connectors")
    datasets = relationship("Dataset", back_populates="connector")

    __table_args__ = (UniqueConstraint("id", name="uq_connector_id"),)


class Workspace(Base):
    __tablename__ = "workspace"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organization.id"))
    slug = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)

    organization = relationship("Organization", back_populates="workspaces")
    user = relationship("User", back_populates="spaces")
    dataset_spaces = relationship("DatasetSpace", back_populates="workspace")
    user_spaces = relationship("UserSpace", back_populates="workspace")


class UserSpace(Base):
    __tablename__ = "user_space"
    workspace_id = Column(
        UUID(as_uuid=True), ForeignKey("workspace.id"), primary_key=True
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True)

    workspace = relationship("Workspace", back_populates="user_spaces", lazy="joined")
    user = relationship("User", back_populates="user_spaces", lazy="joined")


class UserConversation(Base):
    __tablename__ = "user_conversation"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspace.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    created_at = Column(DateTime, default=datetime.datetime.now)
    valid = Column(Boolean, default=True)

    workspace = relationship("Workspace")
    user = relationship("User")
    messages = relationship(
        "ConversationMessage",
        back_populates="user_conversation",
        cascade="all, delete-orphan",
    )


class ConversationMessage(Base):
    __tablename__ = "conversation_message"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("user_conversation.id"))
    created_at = Column(DateTime, default=datetime.datetime.now)
    query = Column(String)
    response = Column(JSON, nullable=True)
    code_generated = Column(String, nullable=True)
    label = Column(String, nullable=True)
    log_id = Column(UUID(as_uuid=True), nullable=True)
    settings = Column(JSON, nullable=True)

    user_conversation = relationship("UserConversation", back_populates="messages")


class DatasetSpace(Base):
    __tablename__ = "dataset_space"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("dataset.id"))
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspace.id"))

    dataset = relationship("Dataset", back_populates="dataset_spaces")
    workspace = relationship("Workspace", back_populates="dataset_spaces")
