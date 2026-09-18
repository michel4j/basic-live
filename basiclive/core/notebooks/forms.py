from crisp_modals.forms import (
    Button,
    FullWidth,
    HalfWidth,
    ModalModelForm,
    Row,
    ThirdWidth,
)
from crispy_forms.layout import Field, Layout
from django import forms
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .models import Notebook


class NotebookForm(ModalModelForm):
    class Meta:
        model = Notebook
        fields = [
            'title',
            'description',
            'owner',
            'access',
            'editor',
            'members',
            'session',
            'project',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.instance.pk and not self.instance._state.adding:
            self.body.title = _("Edit Notebook")
            if not getattr(self.body, 'form_action', None):
                try:
                    self.body.form_action = reverse_lazy('notebooks:notebook-edit', kwargs={'pk': self.instance.pk})
                except Exception:
                    pass
        else:
            self.body.title = _("Create Notebook")
            if not getattr(self.body, 'form_action', None):
                try:
                    self.body.form_action = reverse_lazy('notebooks:create-notebook')
                except Exception:
                    pass

        if self.user and not self.user.is_superuser:
            if self.instance._state.adding:
                self.fields['owner'].initial = self.user
            self.fields['owner'].queryset = self.fields['owner'].queryset.filter(pk=self.user.pk)

        self.fields['members'].queryset = self.fields['members'].queryset.order_by('username')
        self.fields['owner'].queryset = self.fields['owner'].queryset.order_by('username')

        self.body.layout = Layout(
            Row(
                FullWidth('title'),
                FullWidth('description'),
                ThirdWidth(Field('owner', css_class='select')),
                ThirdWidth(Field('access', css_class='select')),
                ThirdWidth(Field('editor', css_class='select')),
                HalfWidth(Field('members', css_class='select')),
                HalfWidth(Field('session', css_class='select')),
                HalfWidth(Field('project', css_class='select')),
                style="g-2",
            )
        )
        self.footer.set_buttons(
            Button('Cancel', type='button', value='cancel', style="btn-secondary", data_bs_dismiss="modal"),
            Button('Save', type='submit', name="submit", value='save', style='btn-primary'),
        )
