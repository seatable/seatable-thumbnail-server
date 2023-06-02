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


class DTableExternalApps(Base):
    __tablename__ = 'dtable_external_apps'
    id = Column(Integer, primary_key=True)
    token = Column(String(36), index=True)
    dtable_uuid = Column(String(36), index=True)
    app_type = Column(String(255))
    app_config = Column(Text)
    created_at = Column(DateTime, nullable=True)
    visit_times = Column(Integer)
    creator = Column(String(255))
    org_id = Column(Integer, nullable=True)
    custom_url = Column(String(100), nullable=True, unique=True)


class DTableWorkflows(Base):
    __tablename__ = 'dtable_workflows'
    id = Column(Integer, primary_key=True)
    token = Column(String(36), unique=True)
    dtable_uuid = Column(String(36), index=True)
    workflow_config = Column(Text)
    creator = Column(String(255))
    owner = Column(String(255), index=True)
    created_at = Column(DateTime, nullable=True)
    visit_times = Column(Integer, nullable=True)


class DTableWorkflowTasks(Base):
    __tablename__ = 'dtable_workflow_tasks'
    id = Column(Integer, primary_key=True)
    dtable_workflow_id = Column(Integer, ForeignKey('dtable_workflows.id'))
    row_id = Column(String(36), nullable=False, index=True)
    initiator = Column(String(255), index=True)
    node_id = Column(String(36), nullable=False, index=True)
    created_at = Column(DateTime, nullable=True)
    task_state = Column(String(40), index=True)
    finished_at = Column(DateTime, nullable=True)
    is_valid = Column(Boolean)


class DTableWorkflowTaskParticipants(Base):
    __tablename__ = 'dtable_workflow_task_participants'
    id = Column(Integer, primary_key=True)
    dtable_workflow_task_id = Column(Integer, ForeignKey('dtable_workflow_tasks.id'))
    node_id = Column(String(36), nullable=False, index=True)
    participant = Column(String(255), index=True, nullable=False)
    updated_at = Column(DateTime, nullable=True)


class DTableWorkflowTaskLogs(Base):
    __tablename__ = 'dtable_workflow_task_logs'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('DTableWorkflowTasks.id'))
    operator = Column(String(255), nullable=False, index=True)
    log_type = Column(String(20), nullable=False, index=True)
    node_id = Column(String(50), nullable=True)
    next_node_id = Column(String(50), nullable=True)
    row_data = Column(Text)
    start_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True)
