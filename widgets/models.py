from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.forms import Form
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.utils.http import urlencode


class WidgetFormMixin(object):

    form = None
    form_class = Form
    initial = {}
    prefix = None

    def __init__(self, raw_data=None):
        super(WidgetFormMixin, self).__init__()

        self.raw_data = raw_data or {}
        self.data = self.get_initial()
        self.form = self.get_form()

        if self.form.is_valid():
            self.data.update(**self.form.cleaned_data)

    def get_form_class(self):
        """
        Returns the form class to use in this view
        """
        return self.form_class

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        return self.initial.copy()

    def get_prefix(self):
        """
        Returns the prefix to use for forms on this view.
        """
        return self.prefix

    def get_data(self):
        """
        Returns the widget configuration.
        """
        return self.data

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
            'data': self.raw_data or self.get_initial(),
        }
        return kwargs

    def get_form(self):
        if self.form is None:
            return self.get_form_class()(**self.get_form_kwargs())
        return self.form

    def is_valid(self):
        return self.form.is_valid()

    def errors(self):
        return self.form.errors


class WidgetTemplateMixin(object):

    widget_element = 'widget'
    template_name = None

    def get_template_name(self):
        return self.template_name

    def get_context_data(self):
        context = {
            self.widget_element: self,
        }
        return context

    def render(self):
        return render_to_string(self.get_template_name(), self.get_context_data())


class Widget(WidgetTemplateMixin, WidgetFormMixin):

    code = None
    name = ''
    site_url = None
    loader_url = None
    loader_js = 'js/widgets.js'
    height = 460
    width = 400
    html_element = 'div'
    class_name_suffix = '_widget'
    embed_template = 'widgets/embed_code.html'

    def get_title(self):
        return getattr(self, 'title', self.name)

    def get_height(self):
        return self.data.get('height', self.height)

    def get_width(self):
        return self.data.get('width', self.width)

    def get_template_name(self):
        return super(Widget, self).get_template_name() or 'widgets/{0}_widget.html'.format(self.code)

    def get_html_data(self):
        data = {}
        for key, val in self.get_data().items():
            if isinstance(val, (list, set)):
                if not key.endswith('_set'):
                    raise ImproperlyConfigured("Multi value form field '{0}.{1}' "
                                               "needs a name with '_set' as suffix.".format(self.__class__, key))
                val = ",".join(val)
            elif isinstance(val, bool):
                val = int(val)
            data[key] = val
        return data

    def get_url_params(self):
        params = []
        for key, val in self.get_data().items():
            if isinstance(val, (list, set)):
                if not key.endswith('_set'):
                    raise ImproperlyConfigured("Multi value form field '{0}.{1}' "
                                               "needs a name with '_set' as suffix.".format(self.__class__, key))
                for v in val:
                    params.append(urlencode({key: v}))
            elif isinstance(val, bool):
                params.append(urlencode({key: int(val)}))
            else:
                params.append(urlencode({key: str(val)}))
        return "&".join(params)

    def get_site_url(self):
        return self.site_url or 'http://{0}'.format(Site.objects.get_current().domain.rstrip('/'))

    def get_base_url(self):
        return "{0}{1}".format(self.get_site_url(), reverse('widgets-detail', kwargs={'widget': self.code}))

    def get_builder_base_url(self):
        return "{0}{1}".format(self.get_site_url(), reverse('widgets-build', kwargs={'widget': self.code}))

    def _append_params_to_url(self, url):
        if self.get_data():
            url = '{0}?{1}'.format(url, self.get_url_params())
        return url

    def get_absolute_url(self):
        return self._append_params_to_url(self.get_base_url())

    def get_builder_url(self):
        return self._append_params_to_url(self.get_builder_base_url())

    def get_loader_url(self):
        return self.loader_url or "{0}{1}".format(self.get_site_url(), static(self.loader_js))

    def get_class_name(self):
        return "{0}{1}".format(self.code, self.class_name_suffix)

    def get_embed_code(self):
        if not self.is_valid():
            return ''
        return render_to_string(self.embed_template, {'widget': self})

