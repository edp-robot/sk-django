import typing

from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType

from baseline.types import ModelType, StringList

if typing.TYPE_CHECKING:
    from django.contrib.auth.models import Permission

PermissionList = typing.Iterable["Permission"]


def change_group_permissions(
    group_name: str,
    operation: str,
    permissions: PermissionList,
    group_cls: ModelType = Group,
    db_alias: str = "default",
) -> None:
    """
    Adds or removes the given permissions on the specified group
    Args:
        group_name: the name of the group to perform the operation on
        operation: "add" to add groups, "remove" to remove them
        permissions: the list of permissions to change
        group_cls: the group model class to use, by default use the direct import
        db_alias: the database alias to use
    """
    group = group_cls.objects.using(db_alias).get(name=group_name)

    operation_fn = getattr(group.permissions, operation)
    operation_fn(*permissions)


def get_permissions(
    app_name: str,
    model_name: str,
    permissions_verbs: StringList,
    content_type_cls: ModelType = ContentType,
    db_alias: str = "default",
) -> PermissionList:
    """
    Returns permission objects for the verbs provided for the given content type model

    Args:
        app_name:
        model_name:
        permissions_verbs:
        content_type_cls: the ContentType class to use to make the query; by default use the direct import
        db_alias: the database to use

    Returns:
        a list of permission objects
    """
    content_type = content_type_cls.objects.using(db_alias).get(
        app_label=app_name, model=model_name
    )

    content_type_queryset = content_type.permission_set.using(db_alias)

    permissions = []
    if "all" in permissions_verbs:
        permissions.extend(content_type_queryset.all())
    else:
        for verb in permissions_verbs:
            prefix = f"{verb}_"
            permissions.append(
                # get each permission in order to catch if one of the given verbs is
                # not in the db
                content_type_queryset.get(codename__startswith=prefix)
            )

    return permissions