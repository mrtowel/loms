from django import forms
from django.forms import models
from django.contrib.auth.models import User
from django.contrib.formtools.wizard import FormWizard
from .models import Case, UserFullName, CaseFile, Event

from django.utils.encoding import force_unicode
from suit.widgets import SuitTimeWidget, SuitSplitDateTimeWidget
from django_select2.fields import AutoModelSelect2MultipleField
from filer.fields.folder import Folder


class AutoUserChoices(AutoModelSelect2MultipleField):
    queryset = UserFullName.objects
    search_fields = ['username__icontains', 'last_name__icontains', 'first_name__icontains', 'email__icontains', ]


class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        widgets = {
            'dispute_amount': forms.TextInput(attrs={'localization': True})
        }

    defendant = AutoUserChoices()
    prosecutor = AutoUserChoices()

    def clean(self):
        data = self.cleaned_data
        try:
            defendant = data['defendant']
            prosecutor = data['prosecutor']
            people = [x for x in prosecutor if x in defendant]

            if len(people) > 0:
                raise forms.ValidationError("defendant can't be a prosecutor")

        except KeyError:
            print 'defendant prosecutor admin form'

        return super(CaseForm, self).clean()


class CaseFileForm(forms.ModelForm):
    class Meta:
        model = CaseFile


class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = User

    STATUS = (
        (0, 'client'),
        (1, 'employee'),
        (2, 'partner'),
        )
    first_name = forms.CharField()
    last_name = forms.CharField()
    status = forms.ChoiceField(choices=STATUS)


class CaseSignatureForm(models.ModelForm):
    class Meta(CaseForm.Meta):
        fields = ('signature', )


class CaseSidesSelect(CaseForm):
    class Meta(CaseForm.Meta):
        fields = ('prosecutor', 'defendant', )


class CaseCreationWizard(FormWizard):
    @property
    def __name__(self):
        return self.__class__.__name__

    def done(self, request, form_list):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)

        case = Case(
            signature=data['signature'],
        )
        case.save()
        if data['prosecutor']:
            prosecutor = data['prosecutor']
            defendant = data['defendant']
            case.prosecutor = prosecutor
            case.defendant = defendant
            f, created = Folder.objects.get_or_create(name="case_%s" % case.signature)
            if created:
                case.folder = f
            case.save()
        return self._model_admin.response_add(request, case)


    def parse_params(self, request, admin=None, *args, **kwargs):
        self._model_admin = admin # Save this so we can use it later.
        opts = admin.model._meta # Yes, I know we could've done Employer._meta, but this is cooler :)
        self.extra_context.update({
            'title': u'Add %s' % force_unicode(opts.verbose_name),
            'current_app': admin.admin_site.name,
            'has_change_permission': admin.has_change_permission(request),
            'add': True,
            'opts': opts,
            #'root_path': admin.admin_site.root_path,
            'app_label': opts.app_label,
        })


    def render_template(self, request, form, previous_fields, step, context=None):
        from django.contrib.admin.helpers import AdminForm

        form = AdminForm(form, [(
                                    'Step %d of %d' % (step + 1, self.num_steps()),
                                    {'fields': form.base_fields.keys()}
                                    )], {})
        context = context or {}
        context.update({
            'media': self._model_admin.media + form.media
        })
        return super(CaseCreationWizard, self).render_template(request, form, previous_fields, step, context)


create_case = CaseCreationWizard([CaseSignatureForm, CaseSidesSelect])


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        widgets = {
            'date': SuitSplitDateTimeWidget,
            'time': SuitTimeWidget,
        }