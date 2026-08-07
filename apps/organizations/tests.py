from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Organization

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

    def test_list_organizations_returns_only_member_organizations(self):
        organization = Organization.objects.create(
            name="Owner Org",
            description="Owned by user.",
            owner=self.user,
        )
        organization.members.add(self.user)

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
        organization = Organization.objects.create(
            name="Detail Org",
            description="Organization for detail view.",
            owner=self.user,
        )
        organization.members.add(self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/organizations/{organization.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Detail Org")
        self.assertEqual(response.json()["owner"], self.user.pk)

    def test_update_organization_by_owner_succeeds(self):
        organization = Organization.objects.create(
            name="Update Org",
            description="Organization for update.",
            owner=self.user,
        )
        organization.members.add(self.user)

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
        organization = Organization.objects.create(
            name="Shared Org",
            description="Organization with non-owner member.",
            owner=self.user,
        )
        organization.members.add(self.user, self.other_user)

        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(
            f"/api/organizations/{organization.pk}/",
            {"name": "Hijacked Org"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_organization_by_owner_succeeds(self):
        organization = Organization.objects.create(
            name="Delete Org",
            description="Organization to delete.",
            owner=self.user,
        )
        organization.members.add(self.user)

        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/api/organizations/{organization.pk}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Organization.objects.filter(pk=organization.pk).exists())

    def test_delete_organization_by_non_owner_is_forbidden(self):
        organization = Organization.objects.create(
            name="Protected Org",
            description="Organization owned by another user.",
            owner=self.user,
        )
        organization.members.add(self.user, self.other_user)

        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(f"/api/organizations/{organization.pk}/")

        self.assertEqual(response.status_code, 403)
