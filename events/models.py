from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
import calendar


class Event(models.Model):
    FREQUENCY_CHOICES = [
        ('once', _('One-time')),
        ('daily', _('Daily')),
        ('weekly', _('Weekly')),
        ('monthly', _('Monthly')),
        ('monthly_ordinal', _('Monthly (specific weekday)')),
        ('yearly', _('Yearly')),
    ]
    
    ORDINAL_CHOICES = [
        (1, _('First')),
        (2, _('Second')),
        (3, _('Third')),
        (4, _('Fourth')),
        (-1, _('Last')),
    ]
    
    WEEKDAY_CHOICES = [
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name=_('Title'),
        help_text=_('Enter a descriptive name for the event')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description'),
        help_text=_('Optional description of the event')
    )
    link = models.URLField(
        blank=True,
        verbose_name=_('Link'),
        help_text=_('Optional link to event details, registration, or location')
    )
    place = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Place'),
        help_text=_('Optional event location or venue')
    )
    start_date = models.DateTimeField(
        verbose_name=_('Start Date'),
        help_text=_('When does the event start?')
    )
    end_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('End Date'),
        help_text=_('When does the event end? (optional)')
    )
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='once',
        verbose_name=_('Frequency'),
        help_text=_('How often does this event repeat?')
    )
    monthly_ordinal = models.IntegerField(
        blank=True,
        null=True,
        choices=ORDINAL_CHOICES,
        verbose_name=_('Week of month'),
        help_text=_('For monthly ordinal events: which week? (e.g., First, Second, Last)')
    )
    monthly_weekday = models.IntegerField(
        blank=True,
        null=True,
        choices=WEEKDAY_CHOICES,
        verbose_name=_('Day of week'),
        help_text=_('For monthly ordinal events: which day of the week? (e.g., Monday, Tuesday)')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
        help_text=_('Uncheck to disable this event')
    )
    is_public = models.BooleanField(
        default=True,
        verbose_name=_('Public'),
        help_text=_('Public events are visible to everyone. Private events are only visible to logged-in users.')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date']
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('events:detail', kwargs={'pk': self.pk})

    def _get_nth_weekday_of_month(self, year, month, weekday, nth):
        """
        Get the date of the nth occurrence of a weekday in a month.
        
        Args:
            year: Year
            month: Month (1-12)
            weekday: Weekday (0=Monday, 6=Sunday)
            nth: Which occurrence (1=first, 2=second, etc., -1=last)
        
        Returns:
            datetime object or None if invalid
        """
        # Get all days in the month
        month_calendar = calendar.monthcalendar(year, month)
        
        if nth == -1:
            # Get the last occurrence
            for week in reversed(month_calendar):
                if week[weekday] != 0:
                    day = week[weekday]
                    # Combine with the time from start_date
                    result = self.start_date.replace(year=year, month=month, day=day)
                    return result
        else:
            # Get the nth occurrence (1-indexed)
            occurrence_count = 0
            for week in month_calendar:
                if week[weekday] != 0:
                    occurrence_count += 1
                    if occurrence_count == nth:
                        day = week[weekday]
                        # Combine with the time from start_date
                        result = self.start_date.replace(year=year, month=month, day=day)
                        return result
        
        return None

    def get_next_occurrence(self):
        """Get the next occurrence of this event based on frequency"""
        if self.frequency == 'once':
            return self.start_date if self.start_date > timezone.now() else None
        
        now = timezone.now()
        next_date = self.start_date
        
        if self.frequency == 'daily':
            while next_date <= now:
                next_date += timedelta(days=1)
        elif self.frequency == 'weekly':
            while next_date <= now:
                next_date += timedelta(weeks=1)
        elif self.frequency == 'monthly':
            while next_date <= now:
                if next_date.month == 12:
                    next_date = next_date.replace(year=next_date.year + 1, month=1)
                else:
                    next_date = next_date.replace(month=next_date.month + 1)
        elif self.frequency == 'monthly_ordinal':
            # For monthly ordinal, we need to find the next occurrence of the specified weekday
            if self.monthly_ordinal is None or self.monthly_weekday is None:
                return None
            
            # Start from the current month
            year = now.year
            month = now.month
            
            # Find the next occurrence
            while True:
                next_date = self._get_nth_weekday_of_month(
                    year, month, self.monthly_weekday, self.monthly_ordinal
                )
                
                if next_date and next_date > now:
                    break
                
                # Move to next month
                if month == 12:
                    month = 1
                    year += 1
                else:
                    month += 1
                
                # Safety check to avoid infinite loop
                if year > now.year + 10:
                    return None
        elif self.frequency == 'yearly':
            while next_date <= now:
                next_date = next_date.replace(year=next_date.year + 1)
        
        return next_date

    def is_upcoming(self):
        """Check if event has upcoming occurrences"""
        if not self.is_active:
            return False
        return self.get_next_occurrence() is not None
