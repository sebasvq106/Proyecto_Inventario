"""
This file contains utilitarian functions that can be used in the rest of the app
"""

from django.contrib.auth.mixins import UserPassesTestMixin


class StudentRoleCheck(UserPassesTestMixin):
    """
    View guard that checks if the current user is a student
    """

    def test_func(self):
        return self.request.user.role == "student"


class TeacherRoleCheck(UserPassesTestMixin):
    """
    View guard that checks if the current user is a teacher
    """

    def test_func(self):
        return self.request.user.role == "teacher"


class AdminRoleCheck(UserPassesTestMixin):
    """
    View guard that checks if the current user is an admin
    """

    def test_func(self):
        return self.request.user.role == "admin"


class AdminOrTeacherRoleCheck(UserPassesTestMixin):
    """
    View guard that checks if the current user is an admin or a teacher
    """

    def test_func(self):
        return self.request.user.role == "admin" or self.request.user.role == "teacher"


class TeacherOrStudentRoleCheck(UserPassesTestMixin):
    """
    View guard that checks if the current user is a teacher or a student
    """

    def test_func(self):
        return (
            self.request.user.role == "teacher" or self.request.user.role == "student"
        )
