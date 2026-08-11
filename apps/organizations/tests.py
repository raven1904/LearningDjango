from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .models import Membership, Organization, OrganizationInvitation

User = get_user_model()


class OrganizationsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="orgowner",
            email="owner@example.com",
            password="TestPass123!",
        )
        self.other_user = User.objects.create_user(
            username="member",
            email="member@example.com",
            password="TestPass123!",
        )
        self.bob = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="TestPass123!",
        )
        self.charlie = User.objects.create_user(
            username="charlie",
            email="charlie@example.com",
            password="TestPass123!",
        )

    def create_organization(self, owner, name="Org", description="Test org"):
        organization = Organization.objects.create(
            name=name,
            description=description,
            owner=owner,
        )
        Membership.objects.create(
            organization=organization,
            user=owner,
            role=Membership.Role.OWNER,
        )
        return organization

    def test_list_organizations_returns_only_member_organizations(self):
        organization = self.create_organization(
            owner=self.user,
            name="Owner Org",
            description="Owned by user.",
        )

        Organization.objects.create(
            name="Other Org",
            description="Not visible to owner.",
            owner=self.other_user,
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/organizations/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], "Owner Org")

    def test_create_organization_sets_owner_and_adds_member(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/organizations/",
            {
                "name": "New Org",
                "description": "Organization created by API.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["name"], "New Org")
        self.assertEqual(response.json()["owner"], self.user.pk)
        self.assertEqual(response.json()["members"], [self.user.pk])

        organization = Organization.objects.get(pk=response.json()["id"])
        self.assertEqual(organization.owner, self.user)
        self.assertTrue(self.user in organization.members.all())

    def test_retrieve_organization_detail_by_member(self):
        organization = self.create_organization(
            owner=self.user,
            name="Detail Org",
            description="Organization for detail view.",
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/organizations/{organization.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Detail Org")
        self.assertEqual(response.json()["owner"], self.user.pk)

    def test_update_organization_by_owner_succeeds(self):
        organization = self.create_organization(
            owner=self.user,
            name="Update Org",
            description="Organization for update.",
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f"/api/organizations/{organization.pk}/",
            {"name": "Updated Org"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Updated Org")

        organization.refresh_from_db()
        self.assertEqual(organization.name, "Updated Org")

    def test_update_organization_by_non_owner_is_forbidden(self):
        organization = self.create_organization(
            owner=self.user,
            name="Shared Org",
            description="Organization with non-owner member.",
        )
        Membership.objects.create(
            organization=organization,
            user=self.other_user,
            role=Membership.Role.MEMBER,
        )

        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(
            f"/api/organizations/{organization.pk}/",
            {"name": "Hijacked Org"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_organization_by_owner_succeeds(self):
        organization = self.create_organization(
            owner=self.user,
            name="Delete Org",
            description="Organization to delete.",
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/organizations/{organization.pk}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Organization.objects.filter(pk=organization.pk).exists())

    def test_delete_organization_by_non_owner_is_forbidden(self):
        organization = self.create_organization(
            owner=self.user,
            name="Protected Org",
            description="Organization owned by another user.",
        )
        Membership.objects.create(
            organization=organization,
            user=self.other_user,
            role=Membership.Role.MEMBER,
        )

        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(f"/api/organizations/{organization.pk}/")

        self.assertEqual(response.status_code, 403)

    def test_list_organization_members_by_owner_admin_member_viewer(self):
        organization = self.create_organization(
            owner=self.user,
            name="Members Org",
            description="Organization with many roles.",
        )
        Membership.objects.create(
            organization=organization,
            user=self.other_user,
            role=Membership.Role.ADMIN,
        )
        viewer_user = User.objects.create_user(
            username="viewer",
            email="viewer@example.com",
            password="TestPass123!",
        )
        Membership.objects.create(
            organization=organization,
            user=viewer_user,
            role=Membership.Role.VIEWER,
        )

        for user in (self.user, self.other_user, viewer_user):
            self.client.force_authenticate(user=user)
            response = self.client.get(f"/api/organizations/{organization.pk}/members/")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.json()), 3)

    def test_promote_member_by_owner_and_admin(self):
        organization = self.create_organization(
            owner=self.user,
            name="Promote Org",
            description="Organization promotion.",
        )
        Membership.objects.create(
            organization=organization,
            user=self.other_user,
            role=Membership.Role.MEMBER,
        )

        self.client.force_authenticate(user=self.user)
        membership = Membership.objects.get(
            organization=organization,
            user=self.other_user,
        )
        response = self.client.patch(
            f"/api/organizations/{organization.pk}/members/{membership.pk}/",
            {"role": Membership.Role.ADMIN},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["role"], Membership.Role.ADMIN)

        admin_user = User.objects.create_user(
            username="orgadmin",
            email="admin@example.com",
            password="TestPass123!",
        )
        organization.members.add(admin_user)
        Membership.objects.filter(
            organization=organization,
            user=admin_user,
        ).update(role=Membership.Role.ADMIN)

        self.client.force_authenticate(user=admin_user)
        response = self.client.patch(
            f"/api/organizations/{organization.pk}/members/{membership.pk}/",
            {"role": Membership.Role.MEMBER},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["role"], Membership.Role.MEMBER)

    def test_promote_member_by_member_and_viewer_is_forbidden(self):
        organization = self.create_organization(
            owner=self.user,
            name="Forbidden Promote Org",
            description="Promotion should be forbidden.",
        )
        Membership.objects.create(
            organization=organization,
            user=self.other_user,
            role=Membership.Role.MEMBER,
        )
        viewer_user = User.objects.create_user(
            username="viewer2",
            email="viewer2@example.com",
            password="TestPass123!",
        )
        Membership.objects.create(
            organization=organization,
            user=viewer_user,
            role=Membership.Role.VIEWER,
        )

        self.client.force_authenticate(user=self.other_user)
        membership = Membership.objects.get(
            organization=organization,
            user=viewer_user,
        )
        response = self.client.patch(
            f"/api/organizations/{organization.pk}/members/{membership.pk}/",
            {"role": Membership.Role.ADMIN},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

        self.client.force_authenticate(user=viewer_user)
        response = self.client.patch(
            f"/api/organizations/{organization.pk}/members/{membership.pk}/",
            {"role": Membership.Role.ADMIN},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_cannot_modify_owner_role(self):
        organization = self.create_organization(
            owner=self.user,
            name="Owner Protected Org",
            description="Owner should be protected.",
        )
        Membership.objects.create(
            organization=organization,
            user=self.other_user,
            role=Membership.Role.ADMIN,
        )

        self.client.force_authenticate(user=self.other_user)
        owner_membership = Membership.objects.get(
            organization=organization,
            user=self.user,
        )
        response = self.client.patch(
            f"/api/organizations/{organization.pk}/members/{owner_membership.pk}/",
            {"role": Membership.Role.MEMBER},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_member_can_leave_organization_but_owner_cannot(self):
        organization = self.create_organization(
            owner=self.user,
            name="Leave Org",
            description="Leave org testing.",
        )
        Membership.objects.create(
            organization=organization,
            user=self.other_user,
            role=Membership.Role.MEMBER,
        )

        self.client.force_authenticate(user=self.other_user)
        membership = Membership.objects.get(
            organization=organization,
            user=self.other_user,
        )
        response = self.client.delete(
            f"/api/organizations/{organization.pk}/members/{membership.pk}/"
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Membership.objects.filter(pk=membership.pk).exists())

        self.client.force_authenticate(user=self.user)
        owner_membership = Membership.objects.get(
            organization=organization,
            user=self.user,
        )
        response = self.client.delete(
            f"/api/organizations/{organization.pk}/members/{owner_membership.pk}/"
        )
        self.assertEqual(response.status_code, 403)

    def test_assign_owner_role_is_forbidden(self):
        organization = self.create_organization(
            owner=self.user,
            name="Assign Owner Org",
            description="Cannot assign owner role through endpoint.",
        )
        Membership.objects.create(
            organization=organization,
            user=self.other_user,
            role=Membership.Role.MEMBER,
        )

        self.client.force_authenticate(user=self.user)
        membership = Membership.objects.get(
            organization=organization,
            user=self.other_user,
        )
        response = self.client.patch(
            f"/api/organizations/{organization.pk}/members/{membership.pk}/",
            {"role": Membership.Role.OWNER},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_owner_invites_existing_user_and_invitation_stays_pending(self):
        organization = self.create_organization(
            owner=self.user,
            name="Invite Org",
            description="Invitation lifecycle testing.",
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f"/api/organizations/{organization.pk}/invitations/",
            {"email": self.bob.email, "role": Membership.Role.MEMBER},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        invitation = OrganizationInvitation.objects.get(
            organization=organization,
            email=self.bob.email,
        )
        self.assertEqual(invitation.status, OrganizationInvitation.Status.PENDING)
        self.assertFalse(
            Membership.objects.filter(organization=organization, user=self.bob).exists()
        )

    def test_invitation_acceptance_creates_membership(self):
        organization = self.create_organization(
            owner=self.user,
            name="Accept Org",
            description="Invitation acceptance testing.",
        )
        invitation = OrganizationInvitation.objects.create(
            organization=organization,
            invited_by=self.user,
            email=self.bob.email,
            role=Membership.Role.MEMBER,
            token="accept-token",
            expires_at=timezone.now() + timedelta(days=7),
        )

        self.client.force_authenticate(user=self.bob)
        response = self.client.post(
            f"/api/organizations/invitations/{invitation.token}/accept/"
        )

        self.assertEqual(response.status_code, 200)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, OrganizationInvitation.Status.ACCEPTED)
        self.assertTrue(
            Membership.objects.filter(
                organization=organization,
                user=self.bob,
                role=Membership.Role.MEMBER,
            ).exists()
        )

    def test_re_accepting_invitation_returns_400(self):
        organization = self.create_organization(
            owner=self.user,
            name="Reaccept Org",
            description="Duplicate acceptance should fail.",
        )
        invitation = OrganizationInvitation.objects.create(
            organization=organization,
            invited_by=self.user,
            email=self.bob.email,
            role=Membership.Role.MEMBER,
            token="reaccept-token",
            expires_at=timezone.now() + timedelta(days=7),
            status=OrganizationInvitation.Status.ACCEPTED,
        )

        self.client.force_authenticate(user=self.bob)
        response = self.client.post(
            f"/api/organizations/invitations/{invitation.token}/accept/"
        )

        self.assertEqual(response.status_code, 400)

    def test_non_invited_user_cannot_accept_someone_else_s_invitation(self):
        organization = self.create_organization(
            owner=self.user,
            name="Wrong User Org",
            description="Only the invited user should accept.",
        )
        invitation = OrganizationInvitation.objects.create(
            organization=organization,
            invited_by=self.user,
            email=self.bob.email,
            role=Membership.Role.MEMBER,
            token="wrong-user-token",
            expires_at=timezone.now() + timedelta(days=7),
        )

        self.client.force_authenticate(user=self.charlie)
        response = self.client.post(
            f"/api/organizations/invitations/{invitation.token}/accept/"
        )

        self.assertEqual(response.status_code, 403)

    def test_expired_invitation_is_marked_expired_and_returns_400(self):
        organization = self.create_organization(
            owner=self.user,
            name="Expired Org",
            description="Expired invitations should be rejected.",
        )
        invitation = OrganizationInvitation.objects.create(
            organization=organization,
            invited_by=self.user,
            email=self.bob.email,
            role=Membership.Role.MEMBER,
            token="expired-token",
            expires_at=timezone.now() - timedelta(days=1),
        )

        self.client.force_authenticate(user=self.bob)
        response = self.client.post(
            f"/api/organizations/invitations/{invitation.token}/accept/"
        )

        self.assertEqual(response.status_code, 400)
        invitation.refresh_from_db()
        self.assertEqual(invitation.status, OrganizationInvitation.Status.EXPIRED)

    def test_member_cannot_invite_other_users(self):
        organization = self.create_organization(
            owner=self.user,
            name="Member Invite Org",
            description="Members should not invite others.",
        )
        Membership.objects.create(
            organization=organization,
            user=self.other_user,
            role=Membership.Role.MEMBER,
        )

        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(
            f"/api/organizations/{organization.pk}/invitations/",
            {"email": self.charlie.email, "role": Membership.Role.MEMBER},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_inviting_owner_role_is_rejected(self):
        organization = self.create_organization(
            owner=self.user,
            name="Owner Role Org",
            description="Owner role cannot be invited.",
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            f"/api/organizations/{organization.pk}/invitations/",
            {"email": self.charlie.email, "role": Membership.Role.OWNER},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
