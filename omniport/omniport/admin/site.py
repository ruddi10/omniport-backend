from django import forms as django_forms
from django.conf import settings
from django.contrib.admin import site, sites, forms

from formula_one.admin.model_admins.base import ModelAdmin
from kernel.utils.rights import has_omnipotence_rights


class OmniportAdminAuthenticationForm(forms.AdminAuthenticationForm):
    """
    Extends the default AdminAuthenticationForm provided by Django to modify the
    permission check method
    """

    def confirm_login_allowed(self, user):
        """
        Replace the check for is_staff with has_omnipotence_rights
        :param user: the user whose login privileges are being checked
        :raise: ValidationError if the user is not privileged enough
        """

        if not user.is_active or not has_omnipotence_rights(user):
            raise django_forms.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'username': self.username_field.verbose_name}
            )


class OmniportAdminSite(sites.AdminSite):
    """
    Extends the default AdminSite provided by Django to modify
    - the branding throughout the site
    - the authentication form used to login
    - the permission framework
    """

    site_header = f'{settings.SITE.nomenclature.verbose_name} administration'
    site_title = f'{settings.SITE.nomenclature.verbose_name} administration'
    index_title = f'{settings.SITE.nomenclature.verbose_name} administration'

    login_form = OmniportAdminAuthenticationForm

    def __init__(self, *args, **kwargs):
        """
        Add the registered model of the default Django admin site to Omnipotence
        :param args: arguments
        :param kwargs: keyword arguments
        """

        super(OmniportAdminSite, self).__init__(*args, **kwargs)
        for model, _ in site._registry.items():
            self.register(model)

    def has_permission(self, request):
        """
        Replace the check for is_staff with has_omnipotence_rights
        :param request: the request whose user is to be checked for permissions
        :return: True if the user of the request is active and privileged enough
        """

        return request.user.is_active and has_omnipotence_rights(request.user)

    def register(self, model_or_iterable, admin_class=None, **options):
        """
        Override Omnipotence's registration process to replace the standard
        ModelAdmin class with our enhanced ModelAdmin class
        :param model_or_iterable: the model being registered
        :param admin_class: the supplied ModelAdmin, if any
        :param options: keyword arguments for the registration function
        """

        admin_class = admin_class or ModelAdmin
        super().register(model_or_iterable, admin_class, **options)


omnipotence = OmniportAdminSite(name='omnipotence')
