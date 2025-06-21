# frisque/scans/forms.py

from django import forms

class RunScanForm(forms.Form):
    """
    Form for initiating a new due diligence scan.
    Captures the company's name and website for analysis.
    """
    company_name = forms.CharField(
        label="Company Name",
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-brand-blue-light focus:border-brand-blue-light sm:text-sm',
            'placeholder': 'e.g., Innovatech Solutions'
        })
    )
    company_website = forms.URLField(
        label="Company Website (URL)",
        max_length=255,
        required=True,
        widget=forms.URLInput(attrs={
            'class': 'mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-brand-blue-light focus:border-brand-blue-light sm:text-sm',
            'placeholder': 'e.g., https://innovatech.com'
        })
    )

