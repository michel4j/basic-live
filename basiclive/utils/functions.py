from django.db import models
from django.db.models import fields, FloatField, Aggregate
from django.utils import timezone
from datetime import datetime


def get_hours_per_shift() -> int:
    try:
        from basiclive.core.schedule.conf import settings as schedule_settings
        return schedule_settings.HOURS_PER_SHIFT
    except (ImportError, AttributeError):
        return 8


SHIFT = get_hours_per_shift()
SHIFT_DURATION = '{:d} hour'.format(SHIFT)
OFFSET = -timezone.make_aware(datetime.now(), timezone.get_default_timezone()).utcoffset().total_seconds()


class Hours(models.Func):
    function = 'HOUR'
    template = '%(function)s(%(expressions)s)'

    def as_postgresql(self, compiler, connection):
        self.arg_joiner = " - "
        return self.as_sql(compiler, connection, function="EXTRACT",
                           template="%(function)s(epoch FROM %(expressions)s)/3600")

    def as_mysql(self, compiler, connection):
        self.arg_joiner = " , "
        return self.as_sql(compiler, connection, function="TIMESTAMPDIFF",
                           template="-%(function)s(HOUR,%(expressions)s)")

    def as_sqlite(self, compiler, connection):
        # the template string needs to escape '%Y' to make sure it ends up in the final SQL. Because two rounds of
        # template parsing happen, it needs double-escaping ("%%%%").
        return self.as_sql(compiler, connection, function="strftime",
                           template="%(function)s(\"%%%%H\",%(expressions)s)")


class Minutes(models.Func):
    function = 'MINUTE'
    template = '%(function)s(%(expressions)s)'

    def as_postgresql(self, compiler, connection):
        self.arg_joiner = " - "
        return self.as_sql(compiler, connection, function="EXTRACT",
                           template="%(function)s(epoch FROM %(expressions)s)/60")

    def as_mysql(self, compiler, connection):
        self.arg_joiner = " , "
        return self.as_sql(compiler, connection, function="TIMESTAMPDIFF",
                           template="-%(function)s(MINUTE,%(expressions)s)")

    def as_sqlite(self, compiler, connection):
        # the template string needs to escape '%Y' to make sure it ends up in the final SQL. Because two rounds of
        # template parsing happen, it needs double-escaping ("%%%%").
        return self.as_sql(compiler, connection, function="strftime",
                           template="%(function)s(\"%%%%M\",%(expressions)s)")


class Shifts(models.Func):
    function = 'HOUR'
    template = '%(function)s(%(expressions)s)'
    output_field = FloatField()

    def as_postgresql(self, compiler, connection):
        self.arg_joiner = " - "
        return self.as_sql(compiler, connection, function="EXTRACT",
                           template="(%(function)s(epoch FROM %(expressions)s)/28800)")

    def as_mysql(self, compiler, connection):
        self.arg_joiner = " , "
        return self.as_sql(compiler, connection, function="TIMESTAMPDIFF",
                           template="-%(function)s(HOUR,%(expressions)s)/8")


class ShiftStart(models.Func):
    function = 'to_timestamp'
    template = '%(function)s(%(expressions)s)'

    def as_postgresql(self, compiler, connection):
        self.arg_joiner = " - "
        shift_duration = '{:d} hour'.format(get_hours_per_shift())
        return self.as_sql(
            compiler, connection, function="to_timestamp",
            template=(
                "%(function)s("
                "   floor((EXTRACT(epoch FROM %(expressions)s)) / EXTRACT(epoch FROM interval '{shift}'))"
                "   * EXTRACT(epoch FROM interval '{shift}') {offset:+}"
                ")"
            ).format(shift=shift_duration, offset=OFFSET)
        )


class ShiftEnd(models.Func):
    function = 'to_timestamp'
    template = '%(function)s(%(expressions)s)'

    def as_postgresql(self, compiler, connection):
        self.arg_joiner = " - "
        shift_duration = '{:d} hour'.format(get_hours_per_shift())
        return self.as_sql(
            compiler, connection, function="to_timestamp",
            template=(
                "%(function)s("
                "   ceil((EXTRACT(epoch FROM %(expressions)s)) / EXTRACT(epoch FROM interval '{shift}'))"
                "   * EXTRACT(epoch FROM interval '{shift}') {offset:+}"
                ")"
            ).format(shift=shift_duration, offset=OFFSET)
        )


class ListLength(models.Func):
    function = 'json_array_length'
    template = '%(function)s(%(expressions)s::json)'

    def as_postgresql(self, compiler, connection):
        self.arg_joiner = " - "
        return self.as_sql(
            compiler, connection, function="json_array_length",
            template="%(function)s(%(expressions)s::json)"
        )


class ShiftIndex(models.Func):
    function = 'floor'
    template = '%(function)s(%(expressions)s)'

    def as_postgresql(self, compiler, connection):
        self.arg_joiner = " - "
        shift = get_hours_per_shift()
        return self.as_sql(
            compiler, connection, function="floor",
            template=(
                "%(function)s("
                "   floor(date_part("
                "       'hour', "
                "       to_timestamp("
                "           EXTRACT("
                "               epoch FROM %(expressions)s"
                "           ) {offset:+} "
                "       )"
                "   )) / {shift}"
                ")::int"
            ).format(shift=shift, offset=-OFFSET)
        )


class Median(Aggregate):
    function = 'PERCENTILE_CONT'
    name = 'median'
    output_field = FloatField()
    template = '%(function)s(0.5) WITHIN GROUP (ORDER BY %(expressions)s)'