from django import forms
from apps.core.templatetags.site_copy import ui
from .models import Inquiry
from apps.products.models import Product

class InquiryForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Inquiry
        fields = ('name', 'organization', 'email', 'phone', 'product', 'kind', 'message')
        labels = {'name': 'نام و نام خانوادگی', 'organization': 'شرکت / سازمان', 'email': 'ایمیل', 'phone': 'تلفن', 'product': 'محصول', 'kind': 'موضوع درخواست', 'message': 'پیام شما'}
        widgets = {'message': forms.Textarea(attrs={'rows': 5})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(published=True)

        for field in self.fields.values():
            field.label = ui(field.label)
        self.fields['kind'].choices = [(value, ui(label)) for value, label in self.fields['kind'].choices]
