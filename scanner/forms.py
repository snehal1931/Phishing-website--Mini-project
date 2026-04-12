from django import forms
import re

def find_url(text):
    """Extract the first URL from a block of text."""
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    match = url_pattern.search(text)
    return match.group(0) if match else text


class ScanForm(forms.Form):
    url = forms.CharField(
        label='',
        max_length=2048,
        widget=forms.TextInput(attrs={
            'class': 'form-control scan-input',
            'placeholder': 'Paste a suspicious URL or link here...',
            'id': 'id_scan_url',
            'autocomplete': 'off',
        })
    )

    category = forms.ChoiceField(
        choices=[
            ('Link', 'Link'),
            ('Email', 'Email'),
            ('Message', 'Message'),
        ],
        initial='Link',
        widget=forms.HiddenInput(attrs={'id': 'id_scan_category'})
    )

    def clean_url(self):
        url = self.cleaned_data['url'].strip()
        
        # Extract URL if user pasted a text block
        url = find_url(url)

        if len(url) < 4:
            raise forms.ValidationError("Please enter a valid URL.")
        # Auto-prefix http:// if missing
        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = 'http://' + url
        return url
