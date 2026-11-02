from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    # Honeypot: real visitors never see or fill this field; bots usually do.
    website = forms.CharField(
        required=False,
        label="Leave this empty",
        widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
    )

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "interest", "message"]
        labels = {
            "name": "Your name",
            "email": "Email address",
            "phone": "Phone / WhatsApp (optional)",
            "interest": "What are you interested in?",
            "message": "Tell us about your idea",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Maria Lopez", "autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com", "autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"placeholder": "(555) 123-4567", "autocomplete": "tel"}),
            "message": forms.Textarea(
                attrs={
                    "rows": 6,
                    "placeholder": "Dates, group size, colours, names to include, or just a rough idea. "
                    "También puede escribirnos en español.",
                }
            ),
        }

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Spam detected.")
        return ""
