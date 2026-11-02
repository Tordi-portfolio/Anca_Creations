from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Only active staff users may use the view.

    * Anonymous visitors are redirected to the login page.
    * Logged-in users who are not staff get a 403 page.
    """

    def test_func(self):
        user = self.request.user
        return user.is_active and user.is_staff
