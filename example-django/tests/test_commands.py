

import sys

from django.core.management import CommandError
from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO


class ShowcredentialsTest(TestCase):
    def test_command_output(self):
        """Test showcredentials command"""
        out = StringIO()
        call_command('showcredentials', 'Alpha', stdout=out)
        self.assertIn('\n', out.getvalue())

    def test_command_invalid_datasrouce(self):
        """Test showcredentials invalid datasource"""
        out = StringIO()
        with self.assertRaisesMessage(CommandError, 'DataSource "Foo" does not exist'):
            call_command('showcredentials', 'Foo', stderr=out)


class CredentialsFormatTest(TestCase):
    def test_command_output(self):
        """Test credentialsformat command"""
        out = StringIO()
        call_command('credentialsformat', 'Alpha', stdout=out)
        self.assertIn('There is no credentials format set.', out.getvalue())

    def test_command_invalid_datasrouce(self):
        """Test credentialsformat invalid datasource"""
        out = StringIO()
        with self.assertRaisesMessage(CommandError, 'DataSource "Foo" does not exist'):
            call_command('credentialsformat', 'Foo', stderr=out)


class UploadcredentialsTest(TestCase):
    def test_command_output(self):
        """Test uploadcredentials command"""
        oldstdin = sys.stdin
        sys.stdin = StringIO('username: Foo\npassword: Bar\n')
        out = StringIO()

        call_command('uploadcredentials', 'Alpha', stdin=input, stdout=out)
        self.assertIn("Credentials have been uploaded to Data Source 'Alpha'", out.getvalue())

        sys.stdin = oldstdin

    def test_command_invalid_datasrouce(self):
        """Test uploadcredentials invalid datasource"""
        out = StringIO()
        with self.assertRaisesMessage(CommandError, 'DataSource "Foo" does not exist'):
            call_command('uploadcredentials', 'Foo', stderr=out)
