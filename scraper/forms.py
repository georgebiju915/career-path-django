from django import forms

class ResumeUploadForm(forms.Form):
    resume_file = forms.FileField(required=False, help_text="Upload a PDF or TXT resume")
    resume_text = forms.CharField(widget=forms.Textarea, required=False, help_text="Or paste resume text")

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("resume_file") and not cleaned.get("resume_text"):
            raise forms.ValidationError("Please provide a resume file or paste the resume text.")
        return cleaned

class ScrapeForm(forms.Form):
    keywords = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={"placeholder": "e.g. python django data engineer"}))
    location = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={"placeholder": "optional location"}))
    max_results = forms.IntegerField(min_value=1, max_value=500, initial=50)