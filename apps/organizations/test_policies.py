from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Organization, Membership
from .policies import (
    get_membership,
    is_member,
    is_admin,
    is_owner,
    can_manage_members,
)

User = get_user_model()


class PoliciesTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owneruser",
            email="owner@example.com",
            password="TestPass123!",
        )
        self.admin = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="TestPass123!",
        )
        self.member = User.objects.create_user(
            username="memberuser",
            email="member@example.com",
            password="TestPass123!",
        )
        self.viewer = User.objects.create_user(
            username="vieweruser",
            email="viewer@example.com",
            password="TestPass123!",
        )

        self.org = Organization.objects.create(
            name="Policy Org",
            description="Org for policy tests",
            owner=self.owner,
        )

        Membership.objects.create(
            organization=self.org,
            user=self.owner,
            role=Membership.Role.OWNER,
        )
        Membership.objects.create(
            organization=self.org,
            user=self.admin,
            role=Membership.Role.ADMIN,
        )
        Membership.objects.create(
            organization=self.org,
            user=self.member,
            role=Membership.Role.MEMBER,
        )
        Membership.objects.create(
            organization=self.org,
            user=self.viewer,
            role=Membership.Role.VIEWER,
        )

    def test_membership_and_role_matrix(self):
        # OWNER
        self.assertTrue(is_member(self.owner, self.org))
        self.assertTrue(is_admin(self.owner, self.org))
        self.assertTrue(is_owner(self.owner, self.org))
        self.assertTrue(can_manage_members(self.owner, self.org))

        # ADMIN
        self.assertTrue(is_member(self.admin, self.org))
        self.assertTrue(is_admin(self.admin, self.org))
        self.assertFalse(is_owner(self.admin, self.org))
        self.assertTrue(can_manage_members(self.admin, self.org))

        # MEMBER
        self.assertTrue(is_member(self.member, self.org))
        self.assertFalse(is_admin(self.member, self.org))
        self.assertFalse(is_owner(self.member, self.org))
        self.assertFalse(can_manage_members(self.member, self.org))

        # VIEWER
        self.assertTrue(is_member(self.viewer, self.org))
        self.assertFalse(is_admin(self.viewer, self.org))
        self.assertFalse(is_owner(self.viewer, self.org))
        self.assertFalse(can_manage_members(self.viewer, self.org))

    def test_get_membership_returns_correct_instance(self):
        m = get_membership(self.admin, self.org)
        self.assertIsNotNone(m)
        self.assertEqual(m.role, Membership.Role.ADMIN)
