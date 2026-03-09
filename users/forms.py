from django import forms

from users.models import User

_INPUT_CLASSES = (
    "w-full px-3.5 py-2.5 rounded-xl border border-gray-200 dark:border-white/10 "
    "bg-gray-50 dark:bg-zinc-800 text-gray-900 dark:text-white text-sm "
    "placeholder-gray-400 dark:placeholder-gray-500 "
    "focus:outline-none focus:ring-2 focus:ring-[#3C7564]/50 focus:border-[#3C7564] dark:focus:border-[#57AA97] "
    "transition-colors"
)

_TEXTAREA_CLASSES = _INPUT_CLASSES + " resize-none min-h-[100px]"


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "bio", "whatsapp_link", "profile_photo"]
        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": _INPUT_CLASSES,
                "placeholder": "First name",
                "autocomplete": "given-name",
            }),
            "last_name": forms.TextInput(attrs={
                "class": _INPUT_CLASSES,
                "placeholder": "Last name",
                "autocomplete": "family-name",
            }),
            "username": forms.TextInput(attrs={
                "class": _INPUT_CLASSES,
                "placeholder": "Your username",
                "autocomplete": "username",
            }),
            "bio": forms.Textarea(attrs={
                "class": _TEXTAREA_CLASSES,
                "placeholder": "Tell the community a little about yourself…",
                "rows": 4,
            }),
            "whatsapp_link": forms.URLInput(attrs={
                "class": _INPUT_CLASSES.replace("px-3.5", "pl-10 pr-3.5"),
                "placeholder": "https://wa.me/yourphonenumber",
            }),
        }

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        username_exists = User.objects.exclude(pk=self.instance.pk).filter(
            username=username
        )
        if username_exists.exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username
