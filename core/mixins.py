import uuid
from django import forms
from django.contrib import messages
from django.http import HttpResponseRedirect


class PreventDuplicateFormMixin:
    token_field_name = "submission_token"

    def get_initial(self):
        initial = super().get_initial()
        token = str(uuid.uuid4())
        self._submission_token = token
        initial[self.token_field_name] = token
        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if self.token_field_name not in form.fields:
            form.fields[self.token_field_name] = forms.CharField(
                widget=forms.HiddenInput()
            )

        if not form.initial.get(self.token_field_name):
            form.initial[self.token_field_name] = self._submission_token

        return form

    def form_valid(self, form):
        request = self.request
        token = form.cleaned_data.get(self.token_field_name)

        if not token:
            messages.error(request, "Invalid submission (missing token).")
            return HttpResponseRedirect(self.get_success_url())

        used_tokens = request.session.get("used_form_tokens", [])

        if token in used_tokens:
            messages.warning(request, "This form was already submitted.")
            return HttpResponseRedirect(self.get_success_url())

        used_tokens.append(token)
        request.session["used_form_tokens"] = used_tokens
        return super().form_valid(form)
