
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.utils import timezone

from .models import Category, ServiceRequest, WorkOrder


class ServiceRequestModelTests(TestCase):

    def setUp(self):
        user_model = get_user_model()

        self.requester = user_model.objects.create_user(
            username="requester"
        )

        self.technician = user_model.objects.create_user(
            username="technician"
        )

        self.category = Category.objects.create(
            name="Electrical"
        )

    def make_request(self, **overrides):
        values = {
            "requester": self.requester,
            "category": self.category,
            "title": "Faulty socket",
            "description": "Socket does not supply power.",
            "location": "Software Engineering Lab",
            "priority": 2,
        }

        values.update(overrides)

        return ServiceRequest.objects.create(**values)

    def test_default_status_is_open(self):
        item = self.make_request()

        self.assertEqual(
            item.status,
            ServiceRequest.Status.OPEN,
        )

    def test_priority_validator_rejects_zero(self):
        item = ServiceRequest(
            requester=self.requester,
            category=self.category,
            title="Invalid",
            description="Invalid priority.",
            location="Lab",
            priority=0,
        )

        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_database_constraint_rejects_priority_six(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.make_request(priority=6)

    def test_category_in_use_is_protected(self):
        self.make_request()

        with self.assertRaises(ProtectedError):
            self.category.delete()

    def test_request_accepts_only_one_work_order(self):
        item = self.make_request()

        WorkOrder.objects.create(
            service_request=item,
            technician=self.technician,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                WorkOrder.objects.create(
                    service_request=item,
                    technician=self.technician,
                )

    def test_due_date_can_be_saved(self):
        due_date = timezone.now() + timedelta(days=2)

        item = self.make_request(due_at=due_date)

        self.assertEqual(item.due_at, due_date)

    def test_requests_can_be_filtered_by_due_date(self):
        chosen_time = timezone.now()

        overdue = self.make_request(
            title="Overdue request",
            due_at=chosen_time - timedelta(days=1),
        )

        self.make_request(
            title="Future request",
            due_at=chosen_time + timedelta(days=1),
        )

        results = ServiceRequest.objects.filter(
            due_at__lt=chosen_time
        )

        self.assertIn(overdue, results)
        self.assertEqual(results.count(), 1)

    def test_resolved_request_requires_summary_and_date(self):
        for status in (
            ServiceRequest.Status.RESOLVED,
            ServiceRequest.Status.CLOSED,
        ):
            item = ServiceRequest(
                requester=self.requester,
                category=self.category,
                title="Resolved test",
                description="Testing resolution.",
                location="Lab",
                priority=2,
                status=status,
            )

            with self.assertRaises(ValidationError):
                item.full_clean()

    def test_resolved_request_requires_non_empty_summary(self):
        item = ServiceRequest(
            requester=self.requester,
            category=self.category,
            title="Resolved test",
            description="Testing resolution.",
            location="Lab",
            priority=2,
            status=ServiceRequest.Status.RESOLVED,
            resolved_at=timezone.now(),
            resolution_summary="   ",
        )

        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_resolved_request_accepts_summary_and_date(self):
        item = ServiceRequest(
            requester=self.requester,
            category=self.category,
            title="Resolved test",
            description="Testing resolution.",
            location="Lab",
            priority=2,
            status=ServiceRequest.Status.RESOLVED,
            resolved_at=timezone.now(),
            resolution_summary="The electrical socket has been repaired.",
        )

        item.full_clean()
