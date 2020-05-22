import logging

from django import forms
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from smartmin.views import SmartCRUDL, SmartFormView

from temba.orgs.models import Org
from temba.orgs.views import InferOrgMixin, OrgPermsMixin
from temba.utils.views import NonAtomicMixin

from .models import get_org


class MigrationPermsMixin(OrgPermsMixin):

    def has_permission(self, request, *args, **kwargs):
        """
        Figures out if the current user has permissions for this view.
        """
        self.kwargs = kwargs
        self.args = args
        self.request = request
        self.org = self.derive_org()

        return True if self.get_user().is_superuser else False


class MigrateCRUDL(SmartCRUDL):
    actions = (
        "migration",
    )

    model = Org

    class Migration(NonAtomicMixin, InferOrgMixin, MigrationPermsMixin, SmartFormView):
        template_name = "migrator/org_migration.haml"

        class MigrationForm(forms.Form):
            org_name = forms.CharField(label="Organization name", required=True,
                                       help_text="The organization name on live server")
            org_id = forms.CharField(label="Organization ID", required=True, help_text="The organization ID on live server")

            def __init__(self, *args, **kwargs):
                self.org = kwargs["org"]
                del kwargs["org"]
                super().__init__(*args, **kwargs)

            def clean_org_id(self):
                org_id = self.cleaned_data.get("org_id")

                try:
                    org_id = int(org_id)
                except Exception:
                    raise ValidationError(
                        _("Please type the correct organization ID, only integer is acceptable.")
                    )

                org = get_org(org_id=org_id)
                if not org:
                    raise ValidationError(
                        _("The organization ID was not found on live server.")
                    )

                return org

            def clean(self):
                data = self.cleaned_data
                org_name = self.cleaned_data.get("org_name")
                org = self.cleaned_data.get("org_id")

                if org and org_name != org.get("name"):
                    raise ValidationError(
                        _("The organization name does not match with the organization name on live server.")
                    )

                return data

        success_message = _("Data migration started successfully")
        form_class = MigrationForm
        submit_button_name = "Start migration"

        def get_success_url(self):  # pragma: needs cover
            return reverse("migrator.org_migration")

        def get_form_kwargs(self):
            kwargs = super().get_form_kwargs()
            kwargs["org"] = self.request.user.get_org()
            return kwargs

        def form_valid(self, form):
            try:
                org = self.request.user.get_org()
                # TODO call task here to star the migration of the data
            except Exception as e:
                # this is an unexpected error, report it to sentry
                logger = logging.getLogger(__name__)
                logger.error("Exception on the migration: %s" % str(e), exc_info=True)
                form._errors["org_id"] = form.error_class([_("Sorry, something went wrong on the migration.")])
                return self.form_invalid(form)

            return super().form_valid(form)
