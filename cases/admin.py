from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, User

from models import Case, Event, CaseFile
from .forms import CaseForm
from .forms import CustomUserCreationForm
from .forms import create_case
from .forms import EventForm
from django.conf.urls import url, patterns

from django.utils.functional import update_wrapper
from suit.admin import SortableTabularInline


class EventInline(admin.TabularInline):
    model = Event
    extra = 1
    form = EventForm


class EventAdmin(admin.ModelAdmin):
    model = Event


class CaseFilesInline(SortableTabularInline):
    model = CaseFile
    sortable = 'file'
    extra = 0


class CaseAdmin(admin.ModelAdmin):
    model = Case
    list_display = ('signature', 'prosecutor_names', 'defendant_names', 'dispute_amount', 'date_added',)
    inlines = (EventInline, CaseFilesInline,)
    form = CaseForm
    #filter_vertical = ('prosecutor',)
    def save_formset(self, request, form, formset, change):
        if formset.model != CaseFile:
            return super(CaseAdmin, self).save_formset(request, form, formset, change)
        else:
            instances = formset.save(commit=False)
            for instance in instances:
                instance.user = request.user
                file = str(instance.file)
                instance.content_type = file[file.rfind('.'):]
                instance.size = instance.file.size
                instance.save()

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                kwargs['admin'] = self
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        urlpatterns = patterns('',
            url(r'add/$', wrap(create_case), name='case_add'),
        )
        urlpatterns += super(CaseAdmin, self).get_urls()
        return urlpatterns


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'status')}
            ),
        )
    list_display = ('last_name', 'first_name', 'email',)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Case, CaseAdmin)
admin.site.register(Event, EventAdmin)
