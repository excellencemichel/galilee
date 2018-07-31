
from django.contrib.auth import get_user_model

from django import forms



User =get_user_model()




class ContactForm(forms.Form):
	fullname = forms.CharField(widget=forms.TextInput(attrs = {"class": "form-control", "placeholder": "your fullname..."}))
	email = forms.EmailField(widget = forms.EmailInput(attrs={"class":"form-control", "placeholder":"Your email"}))
	content = forms.CharField(widget = forms.Textarea(attrs={"class":"form-control", "placeholder":"Your content"}))





	def clean_email(self):
		email = self.cleaned_data.get("email")
		if not "gmail.com" in email:
			raise forms.ValidationError("Email has to be gmail.com")

		return email


	# def clean_content(self):
	# 	# content = self.cleaned_data.get("content")
	# 	raise forms.ValidationError("Conten is wrong")



