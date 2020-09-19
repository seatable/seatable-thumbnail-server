from seaserv import ccnet_api
from seatable_thumbnail.models import DTables, DTableShare, \
    DTableGroupShare, DTableViewUserShare, DTableViewGroupShare, \
    DTableExternalLinks
from seatable_thumbnail.constants import PERMISSION_READ, PERMISSION_READ_WRITE


class ThumbnailPermission(object):
    def __init__(self, db_session, **info):
        self.db_session = db_session
        self.__dict__.update(info)
        self.dtable = self.db_session.query(
            DTables).filter_by(uuid=self.dtable_uuid).first()

    def check(self):
        return self.has_dtable_asset_read_permission()

    def has_dtable_asset_read_permission(self):
        # three ways to access asset
        # 1. through external link to get image
        # 2. through dtable perm, including dtable share
        # 3. through view share perm

        if not hasattr(self, 'username'):
            if self.can_access_image_through_external_link():
                return True
        else:
            if 'r' in self.check_dtable_permission():
                return True
            if 'r' in self.get_view_share_permission():
                return True

        return False

    def can_access_image_through_external_link(self):
        return self.external_link['dtable_uuid'] == self.dtable_uuid

    def check_dtable_permission(self):
        """Check workspace/dtable access permission of a user.
        """
        owner = self.workspace_owner
        username = self.username
        dtable = self.dtable
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
                    return group_permission[0]
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
