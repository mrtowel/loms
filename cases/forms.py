from django import forms
from django.contrib.auth.models import User
from django.contrib.admin.widgets import FilteredSelectMultiple

from .models import Case, UserFullName, CaseFile


class CaseForm(forms.ModelForm):
    class Meta:
        model = Case
        widgets = {
            'dispute_amount': forms.TextInput(attrs={'localization': True})
        }

    defendant = forms.ModelMultipleChoiceField(
        queryset=UserFullName.objects.all(),
        widget=FilteredSelectMultiple('defendants', False)
    )
    prosecutor = forms.ModelMultipleChoiceField(
        queryset=UserFullName.objects.all(),
        widget=FilteredSelectMultiple('prosecutors', False))

    def clean(self):
        data = self.cleaned_data
        print data
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
