from seaserv import ccnet_api
from seatable_thumbnail import session
from seatable_thumbnail.models import Workspaces, DTables, DTableShare, \
    DTableGroupShare, DTableViewUserShare, DTableViewGroupShare


class ThumbnailPermission(object):
    def __init__(self, **info):
        self.__dict__.update(info)
        self.check()

    def check(self):
        pass


def has_dtable_asset_read_permission(request, workspace, dtable, asset_name):
    # three ways to access asset
    # 1. through external link to get image
    # 2. through dtable perm, including dtable share
    # 3. through view share perm
    username = request.user.username

    if can_access_image_through_external_link(request, dtable, asset_name):
        return True
    if check_dtable_permission(username, workspace, dtable):
        return True
    if get_view_share_permision(username, dtable) in [PERMISSION_READ, PERMISSION_READ_WRITE]:
        return True
    return False


def can_access_image_through_external_link(request, dtable, asset_name):
    if not is_image_asset_type(asset_name):
        return False

    external_link = request.session.get('external_link')
    if not external_link:
        return False

    return external_link['dtable_uuid'] == dtable.uuid.hex


def get_view_share_permision(username, dtable):
    """
        return 'r' or 'rw' or ''
    """
    user_view_share_perm = get_user_view_share_permission(username, dtable)
    if user_view_share_perm:
        return user_view_share_perm
    group_view_share_perm = get_group_view_share_permission(username, dtable)
    return group_view_share_perm


def check_dtable_permission(username, workspace, dtable=None, org_id=None):
    """Check workspace/dtable access permission of a user.
    """
    owner = workspace.owner

    if '@seafile_group' in owner:
        group_id = int(owner.split('@')[0])
        if is_group_member(group_id, username):
            return PERMISSION_READ_WRITE
    else:
        if username == owner:
            return PERMISSION_READ_WRITE

    if dtable:  # check user's all permissions from `share`, `group-share` and checkout higher one
        dtable_share = DTableShare.objects.get_by_dtable_and_to_user(
            dtable, username)
        if dtable_share and dtable_share.permission == PERMISSION_READ_WRITE:
            return dtable_share.permission
        permission = dtable_share.permission if dtable_share else None

        if org_id and org_id > 0:
            groups = ccnet_api.get_org_groups_by_user(org_id, username)
        else:
            groups = ccnet_api.get_groups(username, return_ancestors=True)
        group_ids = [group.id for group in groups]
        group_permissions = DTableGroupShare.objects.filter(
            dtable=dtable, group_id__in=group_ids).values_list('permission', flat=True)
        for group_permission in group_permissions:
            permission = permission if permission else group_permission
            if group_permission == PERMISSION_READ_WRITE:
                return group_permission
        return permission

    return None


def get_user_view_share_permission(username, dtable):
    # if multiple view share is in same dtable, get highest
    # 'rw' is lower than 'r' in lexical order, reverse to get 'rw' first
    view_share = DTableViewUserShare.objects.filter(
        to_user=username, dtable=dtable).order_by('-permission').first()
    if not view_share:
        return ''
    return view_share.permission


def get_group_view_share_permission(username, dtable):
    # if multiple view share is in same dtable, get highest
    # 'rw' is lower than 'r' in lexical order, reverse to get 'rw' first
    view_shares = DTableViewGroupShare.objects.filter(
        dtable=dtable).order_by('-permission')

    target_view_share = None
    for view_share in view_shares:
        if is_group_member(view_share.to_group_id, username):
            target_view_share = view_share
            break

    if not target_view_share:
        return ''
    return target_view_share.permission
