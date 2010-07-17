from django.db import models
from django.contrib.auth.models import User

class Conference(models.Model):
	name = models.CharField("Name", max_length=200, unique=True, help_text="This year's event name, such as CMUN 2010 or CMUN XXI")
	url_name = models.SlugField("Short Name", max_length=200, unique=True, help_text="You will use this name in your unique registration URL. Only alphanumeric characters, underscores, and hyphens are allowed. For example, CMUN2010.")
	date = models.DateField()
	location = models.CharField(max_length=200)
	logo = models.ImageField(upload_to="conference_logos")
	website_url = models.URLField("Website URL", blank=True)
	organization_name = models.CharField("Organization / Company / School", max_length=200, help_text="Who checks should be written to; Who issues invoices")
	address_line_1 = models.CharField("Street Address", max_length=200)
	address_line_2 = models.CharField("Address Line 2", max_length=200, blank=True)
	city = models.CharField(max_length=200)
	state = models.CharField("State / Province / Region", max_length=200)
	zip = models.CharField("ZIP / Postal Code", max_length=200,blank=True)
	address_country = models.CharField("Country", max_length=200, blank=True)
	def __init__(self, *args, **kwargs):
		super(Conference,self).__init__()
		self.url_name = self.name.replace(' ','')
	def __unicode__(self):
		return self.name
	
class Committee(models.Model):
	conference = models.ForeignKey(Conference)
	name = models.CharField(max_length=200)
	url_name = models.SlugField("Short Name", max_length=200, help_text="You will use this name in unique registration URLs. Only alphanumeric characters, underscores, and hyphens are allowed.")
	def __unicode__(self):
		return self.name
	
class Country(models.Model):
	conference = models.ForeignKey(Conference)
	name = models.CharField(max_length=200)
	url_name = models.SlugField("Short Name", max_length=200, help_text="You will use this name in unique registration URLs. Only alphanumeric characters, underscores, and hyphens are allowed.")
	flag_icon = models.ImageField(upload_to="flag_icons")
	def __unicode__(self):
		return self.name
	
class School(models.Model):
	name = models.CharField(max_length=200, unique=True)
	url_name = models.SlugField("Short Name", max_length=200, unique=True, help_text="You will use this name in unique registration URLs. Only alphanumeric characters, underscores, and hyphens are allowed.")
	address_line_1 = models.CharField("Address Line 1", max_length=200)
	address_line_2 = models.CharField("Address, Line 2", max_length=200, blank=True)
	city = models.CharField(max_length=200)
	state = models.CharField("State / Province / Region", max_length=200)
	zip = models.CharField("ZIP / Postal Code", max_length=200,blank=True)
	address_country = models.CharField("Country", max_length=200, blank=True)
	def __unicode__(self):
		return self.name

class DelegatePosition(models.Model):
	country = models.ForeignKey(Country)
	committee = models.ForeignKey(Committee)
	school = models.ForeignKey(School)
	title = models.CharField(max_length=200, default="Delegate", help_text="Ambassador, Judge, etc")
	def __unicode__(self):
		return self.country + ", " + self.committee + self.school
	
class Delegate(models.Model):
	position_assignment = models.OneToOneField(DelegatePosition)
	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=30)
	created = models.DateField(auto_now_add=True)
	last_modified = models.DateField(auto_now=True)
	def get_full_name(self):
		self.first_name + " " + self.last_name
	def __unicode__(self):
		return self.get_full_name()

class FacultySponsor(models.Model):
	user = models.OneToOneField(User)
	school = models.ForeignKey(School, null=True)
	phone = models.CharField(max_length=30)
	
	class Meta:
		ordering = ('user','phone',)

	