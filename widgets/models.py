from __future__ import absolute_import, unicode_literals
from django import forms
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.forms import Form
from django.http import QueryDict
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.utils.translation import ugettext as _


def dict_to_querydict(dictionary):
    query = QueryDict('', mutable=True)
    for key, val in dictionary.items():
        if isinstance(val, (set, list)):
            query.setlist(key, val)
        else:
            query.setdefault(key, val)
    return query


class Widget(object):

    code = None
    title = 'Widget'
    form_class = Form
    form_fields = ('title', 'width', 'height', )
    template_name = None
    loader_url = None
    base_url = None

    def __init__(self, data):
        super(Widget, self).__init__()
        if not isinstance(data, QueryDict):
            data = dict_to_querydict(data)
        self.raw_data = data

    @property
    def form(self):
        """
        retrieve or build the widget's form
        """
        if not hasattr(self, '_form'):
            setattr(self, '_form', self.build_form())
        return getattr(self, '_form')

    @property
    def cleaned_data(self):
        """
        returns form.cleaned_data or empty dict
        """
        if self.form.is_valid():
            return self.form.cleaned_data
        return {}

    def build_form(self):
        """
        retrieve a form class, then initialize it
        """
        form_class = self.get_form_class()
        defaults = self.raw_data if len(self.raw_data.items()) > 0 else self.get_defaults()
        form = form_class(defaults, initial=self.get_initial())
        self.build_form_fields(form)

        return form

    def get_form_class(self):
        """
        override this method to customize the form class
        """
        return self.form_class

    def build_form_fields(self, form):
        """
        override this method to manage the form fields
        """
        pass
        #if 'title' in self.form_fields:
        #    form.fields['title'] = forms.CharField(label=_('Title'), max_length=200, required=False)
        #if 'height' in self.form_fields:
        #    form.fields['height'] = forms.IntegerField(label=_('Height'), min_value=100, required=False)
        #if 'width' in self.form_fields:
        #    form.fields['width'] = forms.IntegerField(label=_('Width'), min_value=100, required=False)

    def get_title(self):
        """
        override this method to specialize the widget title
        """
        return self.title

    def get_initial(self):
        """
        this method provide the initial raw data of configuration
        """
        return {
            'title': self.get_title(),
            'height': 460,
            'width': 400
        }

    def get_defaults(self):
        """
        this method provide the default QueryDict of configuration
        """
        return dict_to_querydict(self.get_initial())

    def get_embed_code(self):
        if self.form.is_bound and not self.form.is_valid():
            return ''
        data = {}
        for key, val in self.cleaned_data.items():
            if isinstance(val, (list, set)):
                if not key.endswith('_set'):
                    raise ImproperlyConfigured("Multi value form field '{0}.{1}' "
                                               "needs a name with '_set' as suffix.".format(self.__class__, key))
                val = ",".join(val)
            elif isinstance(val, bool):
                val = int(val)
            data[key] = val
        return render_to_string('widgets/embed_code.html', {
            'widget': self,
            'data': data,
        })

    def get_template_name(self):
        if getattr(self, 'template_name', None):
            return getattr(self, 'template_name')
        return "widgets/{0}_widget.html".format(self.code)

    def get_context_data(self):
        return {
            'widget': self,
            'params': self.cleaned_data
        }

    def render(self):
        return render_to_string(self.get_template_name(), self.get_context_data())

    def get_absolute_url(self):
        return reverse('widgets-detail', kwargs={'widget': self.code})

    def get_base_url(self):
        if getattr(self, 'base_url', None):
            return getattr(self, 'base_url').rstrip('/')
        return 'http://{0}'.format(Site.objects.get_current().domain.rstrip('/'))

    def get_full_url(self):
        return "{0}{1}".format(self.get_base_url(), self.get_absolute_url())

    def get_loader_url(self):
        if getattr(self, 'loader_url', None):
            return getattr(self, 'loader_url')
        return "{0}{1}".format(self.get_base_url(), static('js/widgets.js'))