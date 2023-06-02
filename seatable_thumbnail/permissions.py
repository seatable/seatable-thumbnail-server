import logging
import json
import time
from urllib import parse
from uuid import UUID

import jwt
from seaserv import ccnet_api
from seatable_thumbnail.models import DTables, DTableShare, \
    DTableGroupShare, DTableViewUserShare, DTableViewGroupShare, \
    DTableExternalLinks, DTableCollectionTables, DTableWorkflows, \
    DTableWorkflowTasks, DTableWorkflowTaskParticipants, \
    DTableWorkflowTaskLogs, DTableExternalApps
from seatable_thumbnail.constants import PERMISSION_READ, PERMISSION_READ_WRITE, IMAGE
from seatable_thumbnail import redis_client, settings
from seatable_thumbnail.dtable_db_api import DTableDBAPI
from seatable_thumbnail.dtable_server_api import DTableServerAPI
from seatable_thumbnail.utils import get_dtable_server_url

logger = logging.getLogger(__name__)
CACHE_TIMEOUT = 1800
dtable_server_url = get_dtable_server_url()


class ThumbnailPermission(object):
    def __init__(self, db_session, **info):
        self.db_session = db_session
        self.__dict__.update(info)
        self.cache_key = self.session_key + ':' + self.dtable_uuid
        self.app_need_check_permission_pages = ['table', 'gallery', 'calendar', 'kanban', 'timeline']

    def check(self):
        # if self.has_cache_permission():
        #     return True

        # if self.has_dtable_asset_read_permission():
        #     self.set_cache_permission()
        #     return True

        # return False
        return self.can_access_asset()[0]

    def has_cache_permission(self):
        try:
            return redis_client.get(self.cache_key) == '1'
        except Exception as e:
            return False

    def set_cache_permission(self):
        try:
            redis_client.set(self.cache_key, '1', ex=CACHE_TIMEOUT)
        except Exception as e:
            pass

    def can_access_asset(self):
        """
        can access asset with path

        public
        collection-table
        external-link
        cache
        workflow
        base permission
        view permission
        template base
        external-app

        return: can_access -> bool, need_cache -> bool
        """
        # check permission, order matters !!!
        # please arrange heavy checks with multi sql queries or http requests to later positions
        can_access, need_cache = False, False

        path = self.file_path.lstrip('/')

        # public
        if path.startswith('public'):
            can_access = True
            print('from public')
            return can_access, need_cache

        if self.has_collection_table_permission():
            can_access = True
            print('from collection')
            return can_access, need_cache
        if self.can_access_image_through_external_link():
            can_access = True
            print('from external link')
            return can_access, need_cache
        workflow_token = getattr(self, 'workflow_token', None)
        task_id = getattr(self, 'task_id', None)
        column_key = getattr(self, 'column_key', None)
        column_type = getattr(self, 'column_type', None)
        is_from_workflow_task = bool(workflow_token and task_id and column_key and column_type)
        print('is_from_workflow_task: ', is_from_workflow_task)
        if is_from_workflow_task and self.can_access_image_through_workflow_task():
            print('from workflow')
            can_access = True
            need_cache = True
            return can_access, need_cache
        if self.check_dtable_permission():
            print('from dtable permission')
            can_access = True
            need_cache = True
            return can_access, need_cache
        if self.get_view_share_permission():
            print('from view share')
            can_access = True
            need_cache = True
            return can_access, need_cache
        if self.can_access_image_through_external_app():
            print('from external app')
            can_access = True
            need_cache = True
            return can_access, need_cache

        print('can_access: ', can_access, ' need_cache: ', need_cache)
        return can_access, need_cache

    def has_dtable_asset_read_permission(self):
        # four ways to access asset
        # 1. through external link or external app to get image
        # 2. through collection table to get image
        # 3. through dtable perm, including dtable share, dtable custom share
        # 4. through view share perm

        if self.can_access_image_through_external_link():
            return True
        if self.can_access_image_through_external_app():
            return True
        if self.has_collection_table_permission():
            return True
        if self.check_dtable_permission():
            return True
        if self.get_view_share_permission():
            return True

        return False

    def can_access_image_through_external_link(self):
        if not hasattr(self, 'external_link'):
            return False
        if not self.external_link.get('dtable_uuid'):
            return False

        return self.external_link['dtable_uuid'] == self.dtable_uuid

    def can_access_image_through_external_app(self):
        if not hasattr(self, 'external_app'):
            return False
        if not self.external_app.get('dtable_uuid'):
            return False

        if self.external_app.get('app_type') != 'universal-app':
            return self.external_app['dtable_uuid'] == self.dtable_uuid

        asset_access_token = self.external_app.get('asset_access_token')
        try:
            payload = jwt.decode(asset_access_token, settings.DTABLE_PRIVATE_KEY, algorithms=['HS256'])
        except:
            return False
        app_token = payload.get('app_token')
        if not app_token:
            return False
        external_app = self.db_session.query(
            DTableExternalApps
        ).filter(
            DTableExternalApps.token==app_token
        ).first()
        if not external_app:
            return False
        if self.dtable_uuid.replace('-', '') != external_app.dtable_uuid.replace('-', ''):
            return False
        # can access image asset
        if self.file_type == IMAGE:
            return True
        return False

    def can_access_image_through_workflow_task(self):
        if not self.username:
            print('username')
            return False
        try:
            print('workflow_token: ', self.workflow_token)
            print('task_id: ', self.task_id)
            workflow_token = self.workflow_token
            task_id = int(self.task_id)
        except:
            print('params')
            return False
        column_key = self.column_key
        column_type = self.column_type
        if not (workflow_token and task_id):
            print('params2')
            return False
        task = self.db_session.query(DTableWorkflowTasks).filter_by(id=task_id).first()
        if not task:
            print('task')
            return False
        workflow = self.db_session.query(DTableWorkflows).filter_by(id=task.dtable_workflow_id).first()
        if not workflow:
            print('workflow')
            return False
        workflow_config = json.loads(workflow.workflow_config)
        # admin
        try:
            group_id = int(workflow.owner.split('@')[0])
        except:
            print('group_id')
            return False
        if self.is_group_admin_or_owner(group_id, self.username):
            return True
        # participant
        task_exists = self.db_session.query(self.db_session.query(
            DTableWorkflowTaskLogs
        ).filter(
            DTableWorkflowTaskLogs.task_id == task_id,
            DTableWorkflowTaskLogs.operator == self.username,
            DTableWorkflowTaskLogs.log_type.not_in(['init'])
        ).exists()).scalar()
        print('task_exists: ', task_exists, ' type: ', type(task_exists))
        print('bool(task_exists): ', bool(task_exists))
        participant_exists = self.db_session.query(self.db_session.query(
            DTableWorkflowTaskParticipants
        ).filter(
            DTableWorkflowTaskParticipants.dtable_workflow_task_id == task_id,
            DTableWorkflowTaskParticipants.participant == self.username
        ).exists()).scalar()
        print('participant_exists: ', participant_exists, ' bool(participant_exists): ', bool(participant_exists))
        if task_exists or participant_exists:
            return True
        # initiator
        path = self.file_path.split('')
        print('self.username: ', self.username)
        print('task.initiator: ', task.initiator)
        print('column_key: ', column_key)
        print('column_type: ', column_type)
        if task.initiator == self.username and column_key and column_type:
            row_id = task.row_id
            table_id = workflow_config.get('table_id')
            dtable_server_api = DTableServerAPI(self.username, self.dtable_uuid, dtable_server_url)
            try:
                row = dtable_server_api.get_row_by_table_id(table_id, row_id, convert=False)
            except:
                print('row')
                return False
            value = row.get(column_key)
            if not value:
                print('value')
                return False
            if column_type == 'image':
                if not isinstance(value, list):
                    print('image list')
                    return False
                for img in value:
                    if isinstance(img, str) and path in parse.unquote(img):
                        return True
            elif column_type == 'file':
                if not isinstance(value, list):
                    print('file list')
                    return False
                for file in value:
                    if isinstance(file, dict) and path in parse.unquote(file.get('url', '')):
                        return True
            elif column_type == 'long-text':
                if isinstance(value, dict):
                    for image in value.get('images', []):
                        if path in parse.unquote(image):
                            return True
                elif isinstance(value, str):
                    print('path and quota')
                    return path in parse.unquote(value)
            elif column_type == 'digital-sign':
                if not isinstance(value, dict):
                    print('digital-sign dict')
                    return False
                print('path: ', path)
                print("value.get('sign_image_url': ", value.get('sign_image_url'))
                if path in parse.unquote(value.get('sign_image_url', '')):
                    return True
        print('allllllll')
        return False

    def has_collection_table_permission(self):
        if not hasattr(self, 'collection_table'):
            return False
        if not self.collection_table.get('token'):
            return False
        if not self.collection_table.get('dtable_uuid'):
            return False

        # token = self.collection_table['token']
        # obj = self.db_session.query(
        #     DTableCollectionTables).filter_by(token=token).first()
        # if not obj:
        #     return False

        return self.collection_table['dtable_uuid'] == self.dtable_uuid

    def is_group_member(self, group_id, email, in_structure=None):

        group_id = int(group_id)

        if in_structure in (True, False):
            return ccnet_api.is_group_user(group_id, email, in_structure)

        group = ccnet_api.get_group(group_id)
        if not group:
            return False

        if group.parent_group_id == 0:
            # -1: top address book group
            #  0: group not in address book
            # >0: sub group in address book
            # if `in_structure` is False, NOT check sub groups in address book
            return ccnet_api.is_group_user(group_id, email, in_structure=False)
        else:
            return ccnet_api.is_group_user(group_id, email)

    def is_group_admin(self, group_id, email):
        return ccnet_api.check_group_staff(int(group_id), email)

    def is_group_owner(self, group_id, email):
        group = ccnet_api.get_group(int(group_id))
        if not group:
            return False
        if email == group.creator_name:
            return True
        else:
            return False

    def is_group_admin_or_owner(self, group_id, email):
        return self.is_group_admin(group_id, email) or self.is_group_owner(group_id, email)

    def check_dtable_permission(self):
        """Check workspace/dtable access permission of a user.
        """
        owner = self.workspace_owner
        username = self.username
        if not hasattr(self, 'org_id'):
            self.org_id = -1
        org_id = self.org_id

        if '@seafile_group' in owner:
            group_id = int(owner.split('@')[0])
            if self.is_group_member(group_id, username):
                print('group member')
                return PERMISSION_READ_WRITE
        else:
            if username == owner:
                print('owner')
                return PERMISSION_READ_WRITE

        self.dtable = self.db_session.query(
            DTables).filter_by(uuid=self.dtable_uuid).first()
        dtable = self.dtable

        if dtable:  # check user's all permissions from `share`, `group-share` and checkout higher one
            dtable_share = self.db_session.query(
                DTableShare).filter_by(dtable_id=dtable.id, to_user=username).first()
            if dtable_share and dtable_share.permission == PERMISSION_READ_WRITE:
                return dtable_share.permission
            permission = dtable_share.permission if dtable_share else ''

            if org_id and org_id > 0:
                groups = ccnet_api.get_org_groups_by_user(org_id, username)
            else:
                groups = ccnet_api.get_groups(username, return_ancestors=True)
            group_ids = [group.id for group in groups]
            group_permissions = self.db_session.query(
                DTableGroupShare.permission).filter(DTableGroupShare.dtable_id == dtable.id, DTableGroupShare.group_id.in_(group_ids)).all()

            for group_permission in group_permissions:
                permission = permission if permission else group_permission[0]
                if group_permission[0] == PERMISSION_READ_WRITE:
                    print('read write')
                    return group_permission[0]
            print('dtable permission: ', permission, len(permission))
            return permission

        return ''

    def get_view_share_permission(self):
        """return 'r' or 'rw' or ''
        """
        user_view_share_perm = self.get_user_view_share_permission()
        if user_view_share_perm:
            return user_view_share_perm
        group_view_share_perm = self.get_group_view_share_permission()
        return group_view_share_perm

    def get_user_view_share_permission(self):
        # if multiple view share is in same dtable, get highest
        # 'rw' is lower than 'r' in lexical order, reverse to get 'rw' first
        username = self.username
        dtable = self.dtable

        view_share = self.db_session.query(
            DTableViewUserShare).filter_by(dtable_id=dtable.id, to_user=username).order_by(DTableViewUserShare.permission.desc()).first()
        if not view_share:
            return ''
        return view_share.permission

    def get_group_view_share_permission(self):
        # if multiple view share is in same dtable, get highest
        # 'rw' is lower than 'r' in lexical order, reverse to get 'rw' first
        username = self.username
        dtable = self.dtable

        view_shares = self.db_session.query(
            DTableViewGroupShare).filter_by(dtable_id=dtable.id).order_by(DTableViewGroupShare.permission.desc()).all()

        target_view_share = None
        for view_share in view_shares:
            if self.is_group_member(view_share.to_group_id, username):
                target_view_share = view_share
                break

        if not target_view_share:
            return ''
        return target_view_share.permission
