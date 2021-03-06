from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.models import ModelForm, modelformset_factory
from django.forms.util import ErrorDict
from django.forms.widgets import HiddenInput, TextInput, DateInput
from django.template.defaultfilters import slugify
from django.utils.html import escape
from django.utils.safestring import mark_safe
from regimun_app.models import Conference, School, Committee, Country, \
    FeeStructure, Delegate, Payment, DelegatePosition, Fee, DatePenalty

invalid_names = ["secretariat", "ajax-error", "new-conference", "upload-progress", "school", "new-school","admin", "accounts", "media"]

def strip_data(data):
    for key,value in data.items():
        if isinstance(value, basestring):
            data[key] = value.strip() 
    return data

class CleanForm(forms.Form):
    def clean(self):
        return strip_data(self.cleaned_data)

class CleanModelForm(ModelForm):
    def clean(self):
        return strip_data(self.cleaned_data)

    def add_form_error(self, message):
        if not self._errors:
            self._errors = ErrorDict()
        if not NON_FIELD_ERRORS in self._errors:
            self._errors[NON_FIELD_ERRORS] = self.error_class()
        self._errors[NON_FIELD_ERRORS].append(message)

class jEditableForm(CleanForm):
    id = forms.CharField(max_length=200)
    value = forms.CharField(max_length=200)

class UploadFileForm(CleanForm):
    file = forms.FileField()

class DetailedUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",'first_name','last_name', 'email')

class NewSchoolForm(CleanForm):
    school_name = forms.CharField(label="Name", max_length=200)
    school_address_line_1 = forms.CharField(label="Mailing Address Line 1", max_length=200)
    school_address_line_2 = forms.CharField(label="Address, Line 2", max_length=200, required=False)
    school_city = forms.CharField(label="City", max_length=200)
    school_state = forms.CharField(label="State / Province / Region", max_length=200)
    school_zip = forms.CharField(label="ZIP / Postal Code", max_length=200, required=False)
    school_address_country = forms.CharField(label="Country", max_length=200, required=False)
    
    def clean_school_name(self):
        data = self.cleaned_data['school_name'].strip()
        slug = slugify(data)
        if data in invalid_names or slug in invalid_names or slug == '':
            raise forms.ValidationError("Invalid school name.")
        
        if School.objects.filter(Q(name__exact=data) | Q(url_name__exact=slug)).count() > 0:
            raise forms.ValidationError(mark_safe('School name already exists. <a href="/school/'+escape(slug)+'/">Click here</a> to see this school.'))
        
        if Conference.objects.filter(Q(name__exact=data) | Q(url_name__exact=slug)).count() > 0:
            raise forms.ValidationError("School name is not available.")
        
        return data

class SchoolNameForm(CleanModelForm):
    class Meta:
        model = School
        fields = ('name',)

class NewFacultySponsorForm(CleanForm):
    sponsor_username = forms.RegexField("\w+", label="Username", max_length=30, help_text="Alphanumeric characters only (letters, digits and underscores).")
    sponsor_password = forms.CharField(label="Password", max_length=128, widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput,
        help_text = "Enter the same password as above, for verification.")
    sponsor_first_name = forms.CharField(label="First name", max_length=30)
    sponsor_last_name = forms.CharField(label="Last name", max_length=30)
    sponsor_email = forms.EmailField(label="E-mail address", max_length=200)
    sponsor_phone = forms.CharField(label="Phone number", max_length=30)
    
    def clean_sponsor_username(self):
        username = self.cleaned_data['sponsor_username'].strip()
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError("A user with that username already exists.")
        
    def clean_password2(self):
        password1 = self.cleaned_data.get("sponsor_password", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return password2
    
class EditFacultySponsorForm(CleanForm):
    sponsor_pk = forms.DecimalField(widget=HiddenInput())
    sponsor_first_name = forms.CharField(label="First name", max_length=30)
    sponsor_last_name = forms.CharField(label="Last name", max_length=30)
    sponsor_email = forms.EmailField(label="E-mail address", max_length=200)
    sponsor_phone = forms.CharField(label="Phone number", max_length=30)
    
class ConferenceForm(CleanModelForm):
    class Meta:
        model = Conference
        exclude = ('url_name','no_refunds_start_date')
        widgets = {
            'start_date': DateInput(attrs={'class':'datepicker'}),
            'end_date': DateInput(attrs={'class':'datepicker'}),
        }
    
    def clean_name(self):
        data = self.cleaned_data['name'].strip()
        slug = slugify(data)
        
        if data in invalid_names or slug in invalid_names or slug == '':
            raise forms.ValidationError("Invalid conference name.")
        
        if School.objects.filter(Q(name__exact=data) | Q(url_name__exact=slug)).count() > 0:
            raise forms.ValidationError("Conference name is not available.")
        
        if Conference.objects.filter(Q(name__exact=data) | Q(url_name__exact=slug)).count() > 0:
            raise forms.ValidationError(mark_safe('Conference name already exists. <a href="/'+escape(slug)+'/">Click here</a> to see this conference.'))
        
        return data
    
class BasicConferenceInfoForm(CleanModelForm):
    class Meta:
        model = Conference
        fields = ('start_date','end_date','location','website_url','logo','no_refunds_start_date')
        widgets = {
            'start_date': DateInput(attrs={'class':'datepicker'}),
            'end_date': DateInput(attrs={'class':'datepicker'}),
            'no_refunds_start_date': DateInput(attrs={'class':'datepicker'}),
        }

class FeeForm(CleanModelForm):
    class Meta:
        model = Fee
        exclude = ('feestructure')
        widgets = {
            'amount': TextInput(attrs={'class': "auto {aNeg: '-', aSign: '$'}"}),
        }

class DatePenaltyForm(CleanModelForm):
    class Meta:
        model = DatePenalty
        exclude = ('feestructure')
        widgets = {
            'amount': TextInput(attrs={'class': "auto {aNeg: '-', aSign: '$'}"}),
            'start_date': DateInput(attrs={'class':'datepicker'}),
            'end_date': DateInput(attrs={'class':'datepicker'}),
        }

class OrganizationInfoForm(CleanModelForm):
    class Meta:
        model = Conference
        fields = ('organization_name','address_line_1','address_line_2','city','state','zip','address_country')

class SecretariatUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)

class SchoolMailingAddressForm(CleanModelForm):
    class Meta:
        model = School
        fields = ('address_line_1','address_line_2','city','state','zip','address_country')

class NewCommitteeForm(CleanModelForm):
    class Meta:
        model = Committee
        fields=('name',)

    def is_valid(self, conference):
        valid = CleanModelForm.is_valid(self)
        if valid:
            return self.check_duplicates(conference)
        return valid

    def check_duplicates(self, conference):
        data = self.cleaned_data['name'].strip()
        slug = slugify(data)
        
        if len(slug) > 0:
            if Committee.objects.filter(Q(name__exact=data) | Q(url_name__exact=slug),conference=conference).count() > 0:
                self.add_form_error("A committee already exists with this name.")
                return False
        return True

    def clean_name(self):
        data = self.cleaned_data['name'].strip()
        slug = slugify(data)
        
        if slug == '':
            raise forms.ValidationError("Invalid committee name.")
                
        return data

class NewCountryForm(CleanModelForm):
    class Meta:
        model = Country
        fields=('name','country_code',)

    def is_valid(self, conference):
        valid = CleanModelForm.is_valid(self)
        if valid:
            return self.check_duplicates(conference)
        return valid

    def check_duplicates(self, conference):
        data = self.cleaned_data['name'].strip()
        slug = slugify(data)
        
        if len(slug) > 0:
            if Country.objects.filter(Q(name__exact=data) | Q(url_name__exact=slug),conference=conference).count() > 0:
                self.add_form_error("A country already exists with this name.")
                return False
        return True

    def clean_name(self):
        data = self.cleaned_data['name'].strip()
        slug = slugify(data)
        
        if slug == '':
            raise forms.ValidationError("Invalid country name.")
        
        return data

class NewPaymentForm(CleanModelForm):
    class Meta:
        model = Payment
        exclude = ('conference')
        widgets = {
            'amount': TextInput(attrs={'class': "auto {aNeg: '-', aSign: '$'}"}),
        }

class DelegateNameForm(CleanModelForm):
    class Meta:
        model = Delegate
        fields=('first_name','last_name')

def delegate_position_form_factory(conference):
    class NewDelegatePositionForm(CleanModelForm):
        country = forms.ModelChoiceField(queryset=Country.objects.filter(conference=conference))
        committee = forms.ModelChoiceField(queryset=Committee.objects.filter(conference=conference))
        school = forms.ModelChoiceField(queryset=School.objects.filter(conferences__id__exact=conference.id), required=False)
        title = forms.CharField(max_length=200, initial="Delegate", help_text="Ambassador, Judge, etc")
        
        class Meta:
            model = DelegatePosition
 
    return NewDelegatePositionForm

CommitteeFormSet = modelformset_factory(Committee, can_delete=True, fields=('name',))

CountryFormSet = modelformset_factory(Country, can_delete=True, fields=('name','country_code',))
