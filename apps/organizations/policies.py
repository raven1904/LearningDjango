from .models import Membership


def get_membership(user, organization):
    return Membership.objects.filter(
        user=user,
        organization=organization,
    ).first()


def is_member(user, organization):
    return Membership.objects.filter(
        user=user,
        organization=organization,
    ).exists()


def is_admin(user, organization):
    return Membership.objects.filter(
        user=user,
        organization=organization,
        role__in=[
            Membership.Role.OWNER,
            Membership.Role.ADMIN,
        ],
    ).exists()


def is_owner(user, organization):
    return organization.owner_id == user.id


def can_view_organization(user, organization):
    return is_member(user, organization)


def can_update_organization(user, organization):
    return is_owner(user, organization)


def can_delete_organization(user, organization):
    return is_owner(user, organization)


def can_manage_members(user, organization):
    return is_admin(user, organization)


def can_create_team(user, organization):
    return is_admin(user, organization)
