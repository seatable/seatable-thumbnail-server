from sqlalchemy import Integer, String, ForeignKey, DateTime, \
    Boolean, BigInteger, Text
from sqlalchemy.orm import mapped_column

from seatable_thumbnail import Base


class Workspaces(Base):
    __tablename__ = 'workspaces'
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(255), nullable=True)
    owner = mapped_column(String(255), unique=True)
    repo_id = mapped_column(String(36), unique=True)
    org_id = mapped_column(Integer)
    created_at = mapped_column(DateTime)


class DTables(Base):
    __tablename__ = 'dtables'
    id = mapped_column(Integer, primary_key=True)
    workspace_id = mapped_column(Integer, ForeignKey('workspaces.id'))
    uuid = mapped_column(String(36), unique=True)
    name = mapped_column(String(255))
    creator = mapped_column(String(255))
    modifier = mapped_column(String(255))
    created_at = mapped_column(DateTime)
    updated_at = mapped_column(DateTime)
    deleted = mapped_column(Boolean)
    delete_time = mapped_column(DateTime, nullable=True)
    color = mapped_column(String(50), nullable=True)
    text_color = mapped_column(String(50), nullable=True)
    icon = mapped_column(String(50), nullable=True)


class DTableShare(Base):
    __tablename__ = 'dtable_share'
    id = mapped_column(BigInteger, primary_key=True)
    dtable_id = mapped_column(Integer, ForeignKey('dtables.id'))
    from_user = mapped_column(String(255), index=True)
    to_user = mapped_column(String(255), index=True)
    permission = mapped_column(String(15))


class DTableGroupShare(Base):
    __tablename__ = 'dtable_group_share'
    id = mapped_column(BigInteger, primary_key=True)
    dtable_id = mapped_column(Integer, ForeignKey('dtables.id'))
    group_id = mapped_column(Integer, index=True)
    created_by = mapped_column(String(255), index=True)
    permission = mapped_column(String(15))
    created_at = mapped_column(DateTime)


class DTableViewUserShare(Base):
    __tablename__ = 'dtable_view_user_share'
    id = mapped_column(BigInteger, primary_key=True)
    dtable_id = mapped_column(Integer, ForeignKey('dtables.id'))
    from_user = mapped_column(String(255), index=True)
    to_user = mapped_column(String(255), index=True)
    permission = mapped_column(String(15))
    table_id = mapped_column(String(36), index=True)
    view_id = mapped_column(String(36), index=True)


class DTableViewGroupShare(Base):
    __tablename__ = 'dtable_view_group_share'
    id = mapped_column(BigInteger, primary_key=True)
    dtable_id = mapped_column(Integer, ForeignKey('dtables.id'))
    from_user = mapped_column(String(255), index=True)
    to_group_id = mapped_column(Integer, index=True)
    permission = mapped_column(String(15))
    table_id = mapped_column(String(36), index=True)
    view_id = mapped_column(String(36), index=True)


class DTableExternalLinks(Base):
    __tablename__ = 'dtable_external_link'
    id = mapped_column(BigInteger, primary_key=True)
    dtable_id = mapped_column(Integer, ForeignKey('dtables.id'))
    creator = mapped_column(String(255))
    token = mapped_column(String(100), unique=True)
    permission = mapped_column(String(50))
    view_cnt = mapped_column(Integer)
    create_at = mapped_column(DateTime)
    is_custom = mapped_column(Boolean)
    password = mapped_column(String(128), nullable=True)
    expire_date = mapped_column(DateTime)


class DjangoSession(Base):
    __tablename__ = 'django_session'
    session_key = mapped_column(String(40), primary_key=True)
    session_data = mapped_column(Text)
    expire_date = mapped_column(DateTime)


class DTableSystemPlugins(Base):
    __tablename__ = 'dtable_system_plugin'
    id = mapped_column(Integer, primary_key=True)
    added_by = mapped_column(String(255))
    added_time = mapped_column(DateTime)
    info = mapped_column(Text)
    name = mapped_column(String(255), index=True)


class DTableCollectionTables(Base):
    __tablename__ = 'dtable_collection_tables'
    id = mapped_column(Integer, primary_key=True)
    username = mapped_column(String(255), index=True)
    workspace_id = mapped_column(Integer, index=True)
    dtable_uuid = mapped_column(String(36), index=True)
    config = mapped_column(Text, nullable=True)
    token = mapped_column(String(36), unique=True)
    created_at = mapped_column(DateTime, nullable=True)


class DepartmentsV2(Base):
    __tablename__ = 'departments_v2'
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(255))
    created_at = mapped_column(DateTime)
    parent_id = mapped_column(Integer, index=True)
    org_id = mapped_column(Integer)
    id_in_org = mapped_column(Integer)
    path = mapped_column(String(1024), index=True)


class DepartmentMembersV2(Base):
    __tablename__ = 'department_members_v2'
    id = mapped_column(Integer, primary_key=True)
    department_id = mapped_column(Integer, ForeignKey('departments_v2.id'))
    username = mapped_column(String(255), index=True)
    is_staff = mapped_column(Boolean)
    created_at = mapped_column(DateTime)


class DepartmentV2Groups(Base):
    __tablename__ = 'department_v2_groups'
    id = mapped_column(Integer, primary_key=True)
    department_id = mapped_column(Integer, ForeignKey('departments_v2.id'))
    group_id = mapped_column(Integer, index=True)
