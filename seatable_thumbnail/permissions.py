from sqlalchemy import select
from seaserv import ccnet_api
from seatable_thumbnail.models import DTables, DTableShare, \
    DTableGroupShare, DTableViewUserShare, DTableViewGroupShare, \
    DTableExternalLinks, DTableCollectionTables, DepartmentMembersV2, \
    DepartmentsV2, DepartmentV2Groups
from seatable_thumbnail.constants import PERMISSION_READ, PERMISSION_READ_WRITE
from seatable_thumbnail import redis_client

CACHE_TIMEOUT = 1800


class ThumbnailPermission(object):
    def __init__(self, db_session, **info):
        self.db_session = db_session
        self.__dict__.update(info)
        self.cache_key = self.session_key + ':' + self.dtable_uuid

    def check(self):
        if self.has_cache_permission():
            return True

        if self.has_dtable_asset_read_permission():
            self.set_cache_permission()
            return True

        return False

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

        return self.external_app['dtable_uuid'] == self.dtable_uuid

    def has_collection_table_permission(self):
        if not hasattr(self, 'collection_table'):
            return False
        if not self.collection_table.get('token'):
            return False
        if not self.collection_table.get('dtable_uuid'):
            return False

        token = self.collection_table['token']
        stmt = select(DTableCollectionTables).where(
            DTableCollectionTables.token==token)
        obj = self.db_session.scalars(stmt).first()
        if not obj:
            return False

        return self.collection_table['dtable_uuid'] == self.dtable_uuid

    def is_department_v2_group_member(self, group_id, email):
        stmt = select(DepartmentV2Groups).where(DepartmentV2Groups.group_id==group_id)
        group = self.db_session.scalars(stmt).first()
        if not group:
            return False
        department_id = group.department_id
        stmt = select(DepartmentMembersV2).where(
            DepartmentMembersV2.department_id==department_id, DepartmentMembersV2.username==email)
        member = self.db_session.scalars(stmt).first()
        if member:
            return True
        return False

    def is_group_member(self, group_id, email, in_structure=None):

        group_id = int(group_id)

        if self.is_department_v2_group_member(group_id, email):
            return True

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

    def get_ancestor_department_v2_ids(self, department, include_self=True):
        dep_ids = []
        for dep_id in department.path.strip('/').split('/'):
            if not include_self and dep_id == department.id:
                continue
            try:
                dep_ids.append(int(dep_id))
            except:
                pass
        return dep_ids

    def get_departments_v2_by_user(self, username):
        stmt = select(DepartmentMembersV2).where(
            DepartmentMembersV2.username==username)
        department_member_query = self.db_session.scalars(stmt)

        stmt = select(DepartmentsV2).where(
            DepartmentsV2.id.in_([item.department_id for item in department_member_query]))
        department_query = self.db_session.scalars(stmt)
        return department_query

    def get_department_v2_groups_by_user(self, username):
        departments = self.get_departments_v2_by_user(username)
        departments_ids_set = set()
        for department in departments:
            for department_id in self.get_ancestor_department_v2_ids(department):
                departments_ids_set.add(department_id)

        stmt = select(DepartmentV2Groups).where(
            DepartmentV2Groups.department_id.in_(list(departments_ids_set)))
        groups = self.db_session.scalars(stmt)
        return groups

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
                return PERMISSION_READ_WRITE
        else:
            if username == owner:
                return PERMISSION_READ_WRITE

        stmt = select(DTables).where(
            DTables.uuid==self.dtable_uuid)
        self.dtable = self.db_session.scalars(stmt).first()
        dtable = self.dtable

        if dtable:  # check user's all permissions from `share`, `group-share` and checkout higher one
            stmt = select(DTableShare).where(
                DTableShare.dtable_id==dtable.id, DTableShare.to_user==username)
            dtable_share = self.db_session.scalars(stmt).first()
            if dtable_share and dtable_share.permission == PERMISSION_READ_WRITE:
                return dtable_share.permission
            permission = dtable_share.permission if dtable_share else ''

            if org_id and org_id > 0:
                groups = ccnet_api.get_org_groups_by_user(org_id, username)
            else:
                groups = ccnet_api.get_groups(username, return_ancestors=True)
            group_ids = [group.id for group in groups]

            groups_v2 = self.get_department_v2_groups_by_user(username)
            groups_v2_ids = [group.group_id for group in groups_v2]
            group_ids.extend(groups_v2_ids)

            stmt = select(DTableGroupShare.permission).where(
                DTableGroupShare.dtable_id==dtable.id, DTableGroupShare.group_id.in_(group_ids))

            group_permissions = self.db_session.scalars(stmt)
            for group_permission in group_permissions:
                permission = permission if permission else group_permission[0]
                if group_permission[0] == PERMISSION_READ_WRITE:
                    return group_permission[0]
            return permission

        if '@seafile_group' not in owner:
            departments = self.get_departments_v2_by_user(owner)
            for department in departments:
                department_ids = self.get_ancestor_department_v2_ids(department)
                stmt = select(DepartmentMembersV2).where(
                    DepartmentMembersV2.department_id.in_(department_ids), DepartmentMembersV2.username==username)
                p = self.db_session.scalars(stmt).first()
                if p:
                    return PERMISSION_READ_WRITE

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

        stmt = select(DTableViewUserShare).where(
            DTableViewUserShare.dtable_id==dtable.id, DTableViewUserShare.to_user==username).order_by(DTableViewUserShare.permission.desc())
        view_share = self.db_session.scalars(stmt).first()
        if not view_share:
            return ''
        return view_share.permission

    def get_group_view_share_permission(self):
        # if multiple view share is in same dtable, get highest
        # 'rw' is lower than 'r' in lexical order, reverse to get 'rw' first
        username = self.username
        dtable = self.dtable

        stmt = select(DTableViewGroupShare).where(
            DTableViewGroupShare.dtable_id==dtable.id).order_by(DTableViewGroupShare.permission.desc())

        view_shares = self.db_session.scalars(stmt)
        target_view_share = None
        for view_share in view_shares:
            if self.is_group_member(view_share.to_group_id, username):
                target_view_share = view_share
                break

        if not target_view_share:
            return ''
        return target_view_share.permission
