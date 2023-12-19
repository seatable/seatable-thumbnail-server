from sqlalchemy import Column, Integer, String, ForeignKey, Index, DateTime, \
    Boolean, BigInteger, Text

from seatable_thumbnail import Base


class Workspaces(Base):
    __tablename__ = 'workspaces'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=True)
    owner = Column(String(255), unique=True)
    repo_id = Column(String(36), unique=True)
    org_id = Column(Integer)
    created_at = Column(DateTime)


class DTables(Base):
    __tablename__ = 'dtables'
    id = Column(Integer, primary_key=True)
    workspace_id = Column(Integer, ForeignKey('workspaces.id'))
    uuid = Column(String(36), unique=True)
    name = Column(String(255))
    creator = Column(String(255))
    modifier = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted = Column(Boolean)
    delete_time = Column(DateTime, nullable=True)
    color = Column(String(50), nullable=True)
    text_color = Column(String(50), nullable=True)
    icon = Column(String(50), nullable=True)


class DTableShare(Base):
    __tablename__ = 'dtable_share'
    id = Column(BigInteger, primary_key=True)
    dtable_id = Column(Integer, ForeignKey('dtables.id'))
    from_user = Column(String(255), index=True)
    to_user = Column(String(255), index=True)
    permission = Column(String(15))


class DTableGroupShare(Base):
    __tablename__ = 'dtable_group_share'
    id = Column(BigInteger, primary_key=True)
    dtable_id = Column(Integer, ForeignKey('dtables.id'))
    group_id = Column(Integer, index=True)
    created_by = Column(String(255), index=True)
    permission = Column(String(15))
    created_at = Column(DateTime)


class DTableViewUserShare(Base):
    __tablename__ = 'dtable_view_user_share'
    id = Column(BigInteger, primary_key=True)
    dtable_id = Column(Integer, ForeignKey('dtables.id'))
    from_user = Column(String(255), index=True)
    to_user = Column(String(255), index=True)
    permission = Column(String(15))
    table_id = Column(String(36), index=True)
    view_id = Column(String(36), index=True)


class DTableViewGroupShare(Base):
    __tablename__ = 'dtable_view_group_share'
    id = Column(BigInteger, primary_key=True)
    dtable_id = Column(Integer, ForeignKey('dtables.id'))
    from_user = Column(String(255), index=True)
    to_group_id = Column(Integer, index=True)
    permission = Column(String(15))
    table_id = Column(String(36), index=True)
    view_id = Column(String(36), index=True)


class DTableExternalLinks(Base):
    __tablename__ = 'dtable_external_link'
    id = Column(BigInteger, primary_key=True)
    dtable_id = Column(Integer, ForeignKey('dtables.id'))
    creator = Column(String(255))
    token = Column(String(100), unique=True)
    permission = Column(String(50))
    view_cnt = Column(Integer)
    create_at = Column(DateTime)
    is_custom = Column(Boolean)
    password = Column(String(128), nullable=True)
    expire_date = Column(DateTime)


class DjangoSession(Base):
    __tablename__ = 'django_session'
    session_key = Column(String(40), primary_key=True)
    session_data = Column(Text)
    expire_date = Column(DateTime)


class DTableSystemPlugins(Base):
    __tablename__ = 'dtable_system_plugin'
    id = Column(Integer, primary_key=True)
    added_by = Column(String(255))
    added_time = Column(DateTime)
    info = Column(Text)
    name = Column(String(255), index=True)


class DTableCollectionTables(Base):
    __tablename__ = 'dtable_collection_tables'
    id = Column(Integer, primary_key=True)
    username = Column(String(255), index=True)
    workspace_id = Column(Integer, index=True)
    dtable_uuid = Column(String(36), index=True)
    config = Column(Text, nullable=True)
    token = Column(String(36), unique=True)
    created_at = Column(DateTime, nullable=True)


class DepartmentsV2(Base):
    __tablename__ = 'departments_v2'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    created_at = Column(DateTime)
    parent_id = Column(Integer, index=True)
    org_id = Column(Integer)
    id_in_org = Column(Integer)
    path = Column(String(1024), index=True)


class DepartmentMembersV2(Base):
    __tablename__ = 'department_members_v2'
    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey('departments_v2.id'))
    username = Column(String(255), index=True)
    is_staff = Column(Boolean)
    created_at = Column(DateTime)


class DepartmentV2Groups(Base):
    __tablename__ = 'department_v2_groups'
    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey('departments_v2.id'))
    group_id = Column(Integer, index=True)
