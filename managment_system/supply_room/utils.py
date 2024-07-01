from django.contrib.auth.mixins import UserPassesTestMixin


class StudentRoleCheck(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.role == 'student'


class TeacherRoleCheck(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.role == 'teacher'


class AdminRoleCheck(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.role == 'admin'


class AdminOrTeacherRoleCheck(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.role == 'admin' or self.request.user.role == 'teacher'


class TeacherOrStudentRoleCheck(UserPassesTestMixin):

    def test_func(self):
        return self.request.user.role == 'teacher' or self.request.user.role == 'student'