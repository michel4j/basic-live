from django import forms
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from crisp_modals.forms import (
    Button,
    FullWidth,
    HalfWidth,
    ModalModelForm,
    Row,
)
from crispy_forms.layout import Div, Field, Layout, HTML

from basiclive.core.lims.models import Project
from .models import Beamtime, BeamlineSupport, Downtime, EmailNotification


class BeamtimeForm(ModalModelForm):

    notify = forms.BooleanField(label=_("Schedule email notification"), widget=forms.CheckboxInput(), required=False)

    class Meta:
        model = Beamtime
        fields = ['project', 'beamline', 'start', 'end', 'comments', 'access', 'notify']
        widgets = {
            'comments': forms.Textarea(attrs={"cols": 40, "rows": 7}),
            'beamline': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        errors = Div()
        if self.initial.get('warning'):
            errors = Div(
                Div(
                    HTML(self.initial.get('warning')),
                    css_class="card-header"
                ),
                css_class="card bg-danger text-white"
            )

        if self.instance.pk:
            self.body.title = "Edit Beamtime"
            self.body.form_action = reverse_lazy('beamtime-edit', kwargs={'pk': self.instance.pk})
        else:
            self.body.title = "New Beamtime"
            self.body.form_action = reverse_lazy('new-beamtime')
        self.body.layout = Layout(
            errors,
            Row(
                FullWidth('project'),
                FullWidth('beamline'),
            ),
            Row(
                HalfWidth(Field('start')),
                HalfWidth(Field('end')),
            ),
            Row(
                HalfWidth(Field('access', css_class="select")),
                HalfWidth(Field('notify'), style="px-4 pt-4"),
            ),
            Row(
                FullWidth('comments'),
            ),
        )
        self.footer.set_buttons(
            Button('Revert', type='reset', value='Reset', style="btn-secondary"),
            Button('Save', type='submit', name="submit", value='save', style='btn-primary'),
        )


class BeamlineSupportForm(ModalModelForm):

    staff = forms.ModelChoiceField(queryset=Project.objects.filter(kind__name="Staff"))

    class Meta:
        model = BeamlineSupport
        fields = ['staff', 'date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.body.title = "Edit Beamline Support"
            self.body.form_action = reverse_lazy('support-edit', kwargs={'pk': self.instance.pk})
        else:
            self.body.title = "New Beamline Support"
            self.body.form_action = reverse_lazy('new-support')
        self.body.layout = Layout(
            Row(
                FullWidth('staff'),
                FullWidth(Field('date', readonly=True)),
            )
        )
        self.footer.set_buttons(
            Button('Revert', type='reset', value='Reset', style="btn-secondary"),
            Button('Save', type='submit', name="submit", value='save', style='btn-primary'),
        )


class DowntimeForm(ModalModelForm):

    class Meta:
        model = Downtime
        fields = ['scope', 'beamline', 'start', 'end', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={"cols": 40, "rows": 7}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        buttons = []
        if self.instance.pk:
            self.body.title = "Edit Downtime"
            self.body.form_action = reverse_lazy('downtime-edit', kwargs={'pk': self.instance.pk})
            buttons.append(Button('Delete', type='delete', value='Delete', style="btn-danger me-auto"))
        else:
            self.body.title = "Mark Downtime"
            self.body.form_action = reverse_lazy('new-downtime')

        buttons.extend([
            Button('Revert', type='reset', value='Reset', style="btn-secondary"),
            Button('Save', type='submit', name="submit", value='save', style='btn-primary'),
        ])

        self.body.layout = Layout(
            Row(
                FullWidth('scope'),
            ),
            Row(
                HalfWidth(Field('start')),
                HalfWidth(Field('end')),
            ),
            Row(
                FullWidth('beamline'),
                FullWidth('comments'),
            ),
        )
        self.footer.set_buttons(*buttons)


class EmailNotificationForm(ModalModelForm):
    recipients = forms.CharField(required=False)

    class Meta:
        model = EmailNotification
        fields = ['beamtime', 'send_time', 'email_subject', 'email_body', 'recipients']
        widgets = {
            'email_body': forms.Textarea(attrs={"cols": 42, "rows": 10}),
            'beamtime': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        errors = Div()
        if self.initial.get('warning'):
            errors = Div(
                Div(
                    HTML(self.initial.get('warning')),
                    css_class="card-header"
                ),
                css_class="card bg-danger text-white"
            )

        self.body.title = "Edit Email Notification"
        self.body.form_action = reverse_lazy('email-edit', kwargs={'pk': self.instance.pk})

        self.body.layout = Layout(
            errors,
            Row(
                FullWidth(Field('recipients', readonly=True)),
                FullWidth('beamtime'),
                FullWidth('send_time'),
            ),
            Row(
                FullWidth('email_subject'),
                FullWidth('email_body'),
            ),
        )
        self.footer.set_buttons(
            Button('Revert', type='reset', value='Reset', style="btn-secondary"),
            Button('Save', type='submit', name="submit", value='save', style='btn-primary'),
        )
