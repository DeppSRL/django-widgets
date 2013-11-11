from __future__ import absolute_import
from django import forms
from widgets.models import Widget


class TestWidget(Widget):
    site_url = 'http://localhost:8001'
    embed_template = 'widgets/test_embed_code.html'


class BasicWidget(TestWidget):
    code = 'basic'
    name = 'Basic widget'

    def get_form(self):
        form = super(BasicWidget, self).get_form()
        form.fields['welcome'] = forms.CharField(required=True, label='Welcome')
        return form

    def get_initial(self):
        initial = super(BasicWidget, self).get_initial()
        initial['welcome'] = 'Hello World'
        return initial


class TwitterWidget(TestWidget):
    code = 'twitter'
    name = 'Twitter widget'
    embed_template = 'widgets/embed_twitter.html'
    twitter_id = 'YOUR-WIDGET-ID-HERE'
    href = 'https://twitter.com/twitterapi'


class MultipleChoicesWidget(TestWidget):
    code = 'choices'
    name = 'Component Choices'
    height = 120
    width = 180
    COMPONENTS = (
        ('a', 'First'),
        ('b', 'Second'),
        ('c', 'Third'),
    )

    def get_form(self):
        form = super(MultipleChoicesWidget, self).get_form()
        form.fields['component_set'] = forms.MultipleChoiceField(
            label="Components", required=False, choices=self.COMPONENTS,
            widget=forms.CheckboxSelectMultiple)
        return form

    def get_initial(self):
        initial = super(MultipleChoicesWidget, self).get_initial()
        initial['component_set'] = ['b', 'c']
        return initial


class ResizableWidget(TestWidget):

    code = 'resizable'
    name = 'Resizable Widget'
    height = 200
    width = 200

    def get_form(self):
        form = super(ResizableWidget, self).get_form()
        form.fields['height'] = forms.CharField()
        form.fields['width'] = forms.CharField()
        return form

    def get_initial(self):
        initial = super(ResizableWidget, self).get_initial()
        initial['height'] = self.height
        initial['width'] = self.width
        return initial
