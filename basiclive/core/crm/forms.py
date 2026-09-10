from crisp_modals.forms import (
    Button,
    FullWidth,
    HalfWidth,
    ModalModelForm,
    Row,
    ThirdWidth,
)
from crispy_forms.layout import HTML, Div, Field, Layout
from django import forms
from django.urls import reverse_lazy
from django.utils.text import slugify

from .models import SupportRecord, SupportArea, Feedback, LikertScale
from basiclive.core.lims.models import Project


class SupportAreaForm(ModalModelForm):

    class Meta:
        model = SupportArea
        fields = ['name', 'user_feedback', 'external', 'scale']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.body.title = "Edit Support Area"
            self.body.form_action = reverse_lazy('supportarea-edit', kwargs={'pk': self.instance.pk})
        else:
            self.body.title = "New Support Area"
            self.body.form_action = reverse_lazy('new-supportarea')

        self.body.layout = Layout(
            Row(
                FullWidth('name'),
                HalfWidth(Div('user_feedback', css_class="mt-3 ms-3 ps-1")),
                HalfWidth('scale'),
                FullWidth(Div('external', css_class="mt-3 ms-3 ps-1")),
            ),
        )
        self.footer.set_buttons(
            Button('Revert', type='reset', value='Reset', style="btn-secondary"),
            Button('Save', type='submit', name="submit", value='save', style='btn-primary'),
        )


class LikertTable(Div):
    template = "crm/forms/likert-table.html"

    def __init__(self, *fields, **kwargs):
        super().__init__(*fields, **kwargs)
        self.options = kwargs.get('options')


class LikertEntry(Field):
    template = "crm/forms/likert-entry.html"


class FeedbackForm(ModalModelForm):

    class Meta:
        model = Feedback
        fields = ['comments', 'contact', 'session']
        widgets = {
            'session': forms.HiddenInput(),
            'comments': forms.Textarea(attrs={"cols": 40, "rows": 7})
        }
        labels = {
            'contact': 'I would like to be contacted about my recent experience.',
            'comments': 'Provide comments to explain or give context to the ratings you selected.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.body.title = "User Experience Survey"
        self.body.form_action = reverse_lazy('session-feedback', kwargs={'key': self.initial['session'].feedback_key()})

        likert_tables = []
        area_pks = SupportArea.objects.filter(user_feedback=True).values_list('scale__pk', flat=True)
        for scale in LikertScale.objects.filter(pk__in=area_pks):
            likert_tables.append(HTML(scale.statement))
            likert_table = LikertTable(options=scale.choices())
            for area in SupportArea.objects.filter(user_feedback=True, scale=scale):
                name = slugify(area.name)
                self.fields[name] = forms.MultipleChoiceField(choices=scale.choices(), label=area.name, initial=0)
                likert_table.append(LikertEntry(slugify(name)))
            likert_tables.append(likert_table)
            likert_tables.append(HTML("""<br/>"""))

        self.body.layout = Layout(
            'session',
            HTML("""<p class="text-large text-condensed">
                    Help us improve your next visit or session by letting us know how we did this time.</p>"""),
            *likert_tables,
            Row(
                FullWidth('comments'),
                FullWidth('contact', style="mx-3 px-1"),
            ),
        )
        self.footer.set_buttons(
            Button('Revert', type='reset', value='Reset', style="btn-secondary"),
            Button('Save', type='submit', name="submit", value='save', style='btn-primary'),
        )


class SupportEntryForm(ModalModelForm):
    staff = forms.ModelChoiceField(queryset=Project.objects.filter(kind__name="Staff"))

    class Meta:
        model = SupportRecord
        fields = ['kind', 'areas', 'staff', 'project', 'beamline', 'comments', 'staff_comments', 'lost_time']
        widgets = {
            'comments': forms.Textarea(attrs={
                "cols": 40, "rows": 7, "placeholder": 'Question/Concern from User:\nMy Response/Action Taken:'}),
            'staff_comments': forms.Textarea(attrs={'cols': 40, 'rows': 7})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.body.title = "Edit Record of User Support"
            self.body.form_action = reverse_lazy('supportrecord-edit', kwargs={'pk': self.instance.pk})
        else:
            self.body.title = "New Record of User Support"
            self.body.form_action = reverse_lazy('new-supportrecord')
            self.fields['staff_comments'].widget = forms.HiddenInput()

        self.body.layout = Layout(
            Row(
                ThirdWidth('staff'),
                ThirdWidth('beamline'),
                ThirdWidth('project'),
            ),
            Row(
                HalfWidth('kind'),
                HalfWidth('lost_time'),
                FullWidth(Field('areas', css_class="select")),
            ),
            Row(
                FullWidth('comments'),
                FullWidth('staff_comments'),
            ),
        )
        self.footer.set_buttons(
            Button('Revert', type='reset', value='Reset', style="btn-secondary"),
            Button('Save', type='submit', name="submit", value='save', style='btn-primary'),
        )
