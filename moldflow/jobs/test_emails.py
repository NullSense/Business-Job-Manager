from django.core import mail
from django.test import TestCase
from mixer.backend.django import mixer
from rest_framework.test import APITestCase

from jobs.emails import EmailJobClient


class TestEmailJobStaff(APITestCase):
    def test_send_mail_staff_good(self):
        user1 = mixer.blend(
            "users.CustomUser", is_staff=False, is_active=True, phone="+31230802611"
        )
        user2 = mixer.blend(
            "users.CustomUser", is_staff=False, is_active=False, phone="+31230802611"
        )
        staff1 = mixer.blend(
            "users.CustomUser", is_staff=True, is_active=True, phone="+31230802611"
        )
        staff2 = mixer.blend(
            "users.CustomUser", is_staff=True, is_active=False, phone="+31230852611"
        )
        staff3 = mixer.blend(
            "users.CustomUser", is_staff=True, is_active=True, phone="+31230852611"
        )

        # the mail gets sent on a job create event
        job = mixer.blend("jobs.Job", owner=user1)

        assert (
            "Please update the estimated time to job completion as soon as possible."
            in mail.outbox[0].body
        )

        assert (
            "Owner Company: " + job.owner.company in mail.outbox[0].body
        ), "The owner company details need to be sent"

        assert (
            "Owner Company: " + user1.company in mail.outbox[0].body
        ), "The owner company details need to be sent"

        assert (
            "Name: " + job.name in mail.outbox[0].body
        ), "The name of the job needs to be sent"

        assert (
            "Description: " + job.description in mail.outbox[0].body
        ), "The description of the job needs to be sent"

        assert (
            "Owner Email: " + job.owner.email in mail.outbox[0].body
        ), "The owner's email of the job needs to be sent"

        assert (
            "Owner Email: " + user1.email in mail.outbox[0].body
        ), "The owner's email of the job needs to be sent"

        # let's get the File url matched line
        # check that the url (first 6 chars are "File: ") has no spaces
        file_url_line = [
            line for line in mail.outbox[0].body.split("\n") if "File:" in line
        ][0][6:]
        assert " " not in file_url_line, "The url cannot have spaces"
        assert file_url_line is not False, "The url can't be empty"

        assert len(mail.outbox) == 1, "A single email has to be sent"
        assert len(
            mail.outbox[0].to) == 2, "There are 2 receiving staff members"
        assert (
            staff1.email in mail.outbox[0].to
        ), "The activated staff user should be sent the email"
        assert (
            staff3.email in mail.outbox[0].to
        ), "The activated staff user should be sent the email"
        assert (
            staff2.email not in mail.outbox[0].to
        ), "The unactivated staff user shouldn't be in the to list"

    def test_send_mail_staff_bad(self):
        user1 = mixer.blend(
            "users.CustomUser", is_staff=False, is_active=True, phone="+31230832611"
        )

        mixer.blend(
            "users.CustomUser", is_staff=True, is_active=False, phone="+31230832611"
        )
        self.client.force_authenticate(user1)

        job_name = "New job name"
        job_description = "New job description"
        job_file = "req.txt"
        with self.assertRaises(ValueError) as context:
            with open(job_file) as file:
                self.client.post(
                    "/api/jobs/",
                    {"name": job_name, "description": job_description, "project": file},
                )

            self.assertTrue(
                "The receiver of the email either does not exist or is not active"
                in context.exception
            )

        assert len(mail.outbox) == 0, "No email got sent"


class TestEmailJobClient(TestCase):
    def setUp(self):
        self.user = mixer.blend(
            "users.CustomUser", is_active=True, is_staff=False, phone="+31230802611"
        )
        # so the staff email gets sent and we don't get an exception
        mixer.blend(
            "users.CustomUser", is_active=True, is_staff=True, phone="+31230802611"
        )
        self.job = mixer.blend("jobs.Job", owner=self.user)
        mail.outbox.clear()

    def test_send_mail_client_no_update(self):
        self.job.result = "test"
        self.job.save()

        assert len(mail.outbox) == 1, "The client should receive a result upload email."
        assert len(
            mail.outbox[0].to) == 1, "Only the client should receive an email."

        assert self.job.name in mail.outbox[0].subject
        assert self.job.name in mail.outbox[0].body
        assert "/user/projects/" in mail.outbox[0].body, "The url needs to be there"
        assert "Kind Regards," in mail.outbox[0].body, "A closer needs to exist"
        assert "have been uploaded!" in mail.outbox[0].body, "The result first gets uploaded, not updated."
        assert "Dear Sir/Madam," in mail.outbox[0].body, "A greeting needs to exist"
        assert "Code-PS" in mail.outbox[0].body, "Code-PS company name needs to be there"

    def test_send_mail_client_update(self):
        self.job_email = EmailJobClient(job=self.job, update=True)
        self.job_email.send_mail()

        assert len(mail.outbox) == 1, "The client should receive an email with the job results update"
        assert len(
            mail.outbox[0].to) == 1, "There is exactly 1 receiving client member"

        assert self.job.name in mail.outbox[0].subject
        assert self.job.name in mail.outbox[0].body
        assert "/user/projects/" in mail.outbox[0].body, "The url needs to be there"
        assert "Kind Regards," in mail.outbox[0].body, "A closer needs to exist"
        assert "have been updated!" in mail.outbox[0].body, "The result first gets uploaded, not updated."
        assert "Dear Sir/Madam," in mail.outbox[0].body, "A greeting needs to exist"
        assert "Code-PS" in mail.outbox[0].body, "Code-PS company name needs to be there"


class TestEmailJobClientBad(TestCase):
    def setUp(self):
        self.user = mixer.blend(
            "users.CustomUser", is_active=False, is_staff=False, phone="+31230802611"
        )
        # so the staff email gets sent and we don't get an exception
        mixer.blend(
            "users.CustomUser", is_active=True, is_staff=True, phone="+31230802611"
        )
        self.job = mixer.blend("jobs.Job", owner=self.user)

    def test_send_mail_client_update(self):
        self.job_email = EmailJobClient(job=self.job, update=True)
        with self.assertRaises(ValueError) as context:
            self.job_email.send_mail()

            self.assertTrue(
                "The receiver of the email either does not exist or is not active"
                in context.exception
            )

    def test_send_mail_client_no_update(self):
        self.job_email = EmailJobClient(job=self.job, update=False)
        with self.assertRaises(ValueError) as context:
            self.job_email.send_mail()

            self.assertTrue(
                "The receiver of the email either does not exist or is not active"
                in context.exception
            )
