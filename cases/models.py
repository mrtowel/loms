# coding=utf-8
import random

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, ValidationError
from django.db.models.signals import m2m_changed, pre_save
from filer.fields.file import FilerFileField
from filer.fields.folder import FilerFolderField


class UserFullName(User):
    class Meta:
        proxy = True

    def __unicode__(self):
        return_string = '%s ' % (self.get_full_name())
        if self.email:
            return_string += '<%s>' % self.email
        return return_string


class Case(models.Model):
    """docstring for Case"""
    prosecutor = models.ManyToManyField(User, related_name='prosecutor')
    defendant = models.ManyToManyField(User, related_name='defendant')
    signature = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^(?P<department>\w{1,4})(?P<serial_number>\d{1,4})(\/)(?P<year>\d{2})',
                message='invalid signature'
            )
        ],
        blank=True,
        default='NA00/0000'
    )

    dispute_amount = models.TextField(max_length=31)
    date_added = models.DateTimeField(auto_now=True)
    folder = FilerFolderField(blank=True, null=True)

    def __unicode__(self):
        return self.signature

    def prosecutor_names(self):
        return ', '.join([p.get_full_name() for p in self.prosecutor.all()])

    def defendant_names(self):
        return ', '.join([d.get_full_name() for d in self.defendant.all()])

    prosecutor_names.short_description = 'Prosecutors'
    defendant_names.short_description = 'Defendants'


class Event(models.Model):
    case = models.ForeignKey(Case)
    name = models.CharField(max_length=255)
    date = models.DateTimeField()
    time = models.TimeField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name


class CaseFile(models.Model):
    def get_folder_name(instance):
        return instance.case.folder

    case = models.ForeignKey(Case)
    file = FilerFileField(blank=True, null=True, parent_link=get_folder_name)


def check_prosecutor(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        instance.save()


def check_defendants(sender, instance, **kwargs):
    if kwargs['action'] == 'post_add':
        people = [x for x in instance.prosecutor.all() if x in instance.defendant.all()]
        if len(people) > 0:
            raise ValidationError('defendant - prosecutor conflict')


def set_user(sender, instance, **kwargs):
    if not instance.username:
        username = instance.first_name.lower() + instance.last_name.lower()
        users = User.objects.all()
        unames = [u.username for u in users]
        while True:
            if username in unames:
                username = username + str(random.randint(0, 9))
            else:
                instance.username = username
                return


m2m_changed.connect(check_prosecutor, Case.prosecutor.through)
m2m_changed.connect(check_defendants, Case.defendant.through)
pre_save.connect(set_user, User)