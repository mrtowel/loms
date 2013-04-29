from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, User

from models import Case, Event, CaseFile
from .forms import CaseForm
from .forms import CustomUserCreationForm
from .forms import CaseFileForm


class EventInline(admin.TabularInline):
    model = Event
    extra = 2


class CaseFileInline(admin.StackedInline):
    model = CaseFile
    extra = 1
    fields = ('file','size', 'content_type', 'date_added', 'user',)
    readonly_fields = ('date_added', 'user', 'size', 'content_type',)
    form = CaseFileForm

    def decrypt_date_added(self, obj):
        if obj.date_added:
            decrypt(obj.date_added)

class CaseAdmin(admin.ModelAdmin):
    model = Case
    list_display = ('signature', 'prosecutor_names', 'defendant_names', 'dispute_amount', 'date_added', )
    inlines = (EventInline, CaseFileInline,)
    form = CaseForm
    
    def save_formset(self,request,form,formset,change):
	if formset.model != CaseFile:
	    return super(CaseAdmin, self).save_formset(request,form,formset,change)
	else:
	    instances = formset.save(commit=False)
	    for instance in instances:
		if change:
		    instance.user = request.user
		    file = str(instance.file)
		    instance.content_type = file[file.rfind('.'):]
		    instance.size = instance.file.size
		instance.save()
		


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
