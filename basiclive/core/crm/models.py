from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _
from model_utils import Choices
from model_utils.models import TimeStampedModel

from basiclive.core.lims.models import Project, Session, Beamline


class LikertScale(models.Model):
    statement = models.CharField(max_length=250, null=True)
    worst = models.CharField("-2", max_length=25)
    worse = models.CharField("-1", max_length=25)
    better = models.CharField("1", max_length=25)
    best = models.CharField("2", max_length=25)

    class Meta:
        verbose_name = _("Likert Scale")
        verbose_name_plural = _("Likert Scales")

    def __str__(self):
        return ' | '.join([self.worst, self.worse, self.better, self.best])

    def choices(self):
        return Choices(
            (-2, 'WORST', self.worst),
            (-1, 'WORSE', self.worse),
            (1, 'BETTER', self.better),
            (2, 'BEST', self.best),
            (0, 'NOT_APPLICABLE', _('N/A')),
        )


class SupportArea(models.Model):
    name = models.CharField(max_length=200)
    user_feedback = models.BooleanField(_('Add to User Experience Survey'), default=False)
    external = models.BooleanField(_("External (out of the beamline's control)"), default=False)
    scale = models.ForeignKey(LikertScale, on_delete=models.SET_NULL, null=True, blank=True, related_name='areas')

    class Meta:
        verbose_name = _("Support Area")
        verbose_name_plural = _("Support Areas")

    def __str__(self):
        return self.name


class Feedback(TimeStampedModel):
    session = models.ForeignKey(Session, blank=True, null=True, on_delete=models.SET_NULL, related_name='feedback')
    comments = models.TextField(blank=True, null=True)
    contact = models.BooleanField(_('Contact User'), default=False)

    class Meta:
        verbose_name = _("Feedback")
        verbose_name_plural = _("Feedbacks")

    def __str__(self):
        return f"Feedback #{self.pk} for {self.session}"


class AreaFeedback(models.Model):
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE, related_name='areas')
    area = models.ForeignKey(SupportArea, on_delete=models.CASCADE, related_name='impressions')
    rating = models.IntegerField(default=0)

    class Meta:
        verbose_name = _("Area Feedback")
        verbose_name_plural = _("Area Feedbacks")
        indexes = [
            models.Index(fields=['feedback', 'area']),
        ]

    def get_rating_display(self):
        return self.area.scale.choices()[self.rating]

    def __str__(self):
        return f"{self.area.name}: {self.get_rating_display()}"


class SupportRecord(TimeStampedModel):
    TYPE = Choices(
        ('problem', _('Problem')),
        ('info', _('Info')),
    )
    kind = models.CharField(_("Kind"), max_length=20, default=TYPE.info, choices=TYPE)
    area = models.ForeignKey(SupportArea, on_delete=models.SET_NULL, null=True, blank=True, related_name='records')
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='support_records'
    )
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, related_name='help')
    beamline = models.ForeignKey(Beamline, on_delete=models.SET_NULL, null=True, related_name='help')
    comments = models.TextField(blank=True, null=True)
    lost_time = models.FloatField(_('Time Lost (hours)'), default=0.0)
    staff_comments = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("Support Record")
        verbose_name_plural = _("Support Records")

    def __str__(self):
        return f"{self.staff} | {self.beamline} | {self.project}"

    @property
    def area_names(self):
        return self.area.name if self.area else ""

