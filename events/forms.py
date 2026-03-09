from django import forms
from django.conf import settings


class EventForm(forms.Form):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "required": True,
            "placeholder": "Event title",
            "class": "w-full px-4 py-3 bg-gray-50 dark:bg-zinc-800 border border-gray-200 dark:border-white/10 rounded-2xl focus:ring-2 focus:ring-black dark:focus:ring-white focus:border-transparent transition-all text-gray-900 dark:text-white",
        }),
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            "required": True,
            "rows": 4,
            "placeholder": "Describe your event",
            "class": "w-full px-4 py-3 bg-gray-50 dark:bg-zinc-800 border border-gray-200 dark:border-white/10 rounded-2xl focus:ring-2 focus:ring-black dark:focus:ring-white focus:border-transparent transition-all text-gray-900 dark:text-white resize-none",
        }),
    )
    event_date = forms.DateField(
        widget=forms.DateInput(attrs={
            "type": "date",
            "required": True,
            "class": "w-full px-4 py-3 bg-gray-50 dark:bg-zinc-800 border border-gray-200 dark:border-white/10 rounded-2xl focus:ring-2 focus:ring-black dark:focus:ring-white focus:border-transparent transition-all text-gray-900 dark:text-white",
        }),
    )
    event_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={
            "type": "time",
            "class": "w-full px-4 py-3 bg-gray-50 dark:bg-zinc-800 border border-gray-200 dark:border-white/10 rounded-2xl focus:ring-2 focus:ring-black dark:focus:ring-white focus:border-transparent transition-all text-gray-900 dark:text-white",
        }),
    )
    location = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "required": True,
            "placeholder": "Where is it?",
            "class": "w-full px-4 py-3 bg-gray-50 dark:bg-zinc-800 border border-gray-200 dark:border-white/10 rounded-2xl focus:ring-2 focus:ring-black dark:focus:ring-white focus:border-transparent transition-all text-gray-900 dark:text-white",
        }),
    )
    location_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            "type": "url",
            "placeholder": "https://maps.google.com/...",
            "class": "w-full px-4 py-3 bg-gray-50 dark:bg-zinc-800 border border-gray-200 dark:border-white/10 rounded-2xl focus:ring-2 focus:ring-black dark:focus:ring-white focus:border-transparent transition-all text-gray-900 dark:text-white",
        }),
    )
    category = forms.IntegerField(
        required=False,
        widget=forms.Select(attrs={
            "class": "w-full px-4 py-3 bg-gray-50 dark:bg-zinc-800 border border-gray-200 dark:border-white/10 rounded-2xl focus:ring-2 focus:ring-black dark:focus:ring-white focus:border-transparent transition-all text-gray-900 dark:text-white appearance-none cursor-pointer",
        }),
    )
    max_attendees = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={
            "type": "number",
            "min": "1",
            "placeholder": "Leave blank for unlimited",
            "class": "w-full px-4 py-3 bg-gray-50 dark:bg-zinc-800 border border-gray-200 dark:border-white/10 rounded-2xl focus:ring-2 focus:ring-black dark:focus:ring-white focus:border-transparent transition-all text-gray-900 dark:text-white",
        }),
    )
    is_public_attendees = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            "class": "rounded",
        }),
    )
    whatsapp_group_link = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            "type": "url",
            "placeholder": "https://chat.whatsapp.com/...",
            "class": "w-full px-4 py-3 bg-gray-50 dark:bg-zinc-800 border border-gray-200 dark:border-white/10 rounded-2xl focus:ring-2 focus:ring-black dark:focus:ring-white focus:border-transparent transition-all text-gray-900 dark:text-white",
        }),
    )
    gallery_link = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            "type": "url",
            "placeholder": "https://photos.google.com/...",
            "class": "w-full px-4 py-3 bg-gray-50 dark:bg-zinc-800 border border-gray-200 dark:border-white/10 rounded-2xl focus:ring-2 focus:ring-black dark:focus:ring-white focus:border-transparent transition-all text-gray-900 dark:text-white",
        }),
    )

    def clean_location_url(self):
        url = self.cleaned_data.get("location_url", "")
        return url or ""

    def clean_whatsapp_group_link(self):
        url = self.cleaned_data.get("whatsapp_group_link", "")
        return url or ""

    def clean_gallery_link(self):
        url = self.cleaned_data.get("gallery_link", "")
        return url or ""


class AttachmentValidationMixin:
    """Mixin / standalone helper used by views to validate uploaded attachments."""

    @staticmethod
    def validate(files, event=None):
        """Return error string or None."""
        max_count = settings.ATTACHMENT_MAX_COUNT
        max_size = settings.ATTACHMENT_MAX_SIZE_MB * 1024 * 1024
        allowed_exts = {
            ext.strip().lower() for ext in settings.ATTACHMENT_ALLOWED_EXTENSIONS
        }

        existing_count = event.attachments.count() if event else 0
        if existing_count + len(files) > max_count:
            return f"Maximum {max_count} attachments allowed per event."

        for f in files:
            ext = f.name.rsplit(".", 1)[-1].lower() if "." in f.name else ""
            if ext not in allowed_exts:
                return f"File type .{ext or 'unknown'} is not allowed."
            if f.size > max_size:
                return f"{f.name} exceeds {settings.ATTACHMENT_MAX_SIZE_MB}MB size limit."
        return None
