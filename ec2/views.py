"""
Views for EC-2 application to work with AWS`s EC-2 instances.
"""

from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse
from django.views.generic import View
from django.shortcuts import render
from django.views import generic

from .models import Instance as EC2Instance


class Homepage(View):
    """
    View works with home page and provides empty (no instances) template, either list of
    positions, that render corresponding data.
    """
    template_name = 'homepage.html'

    def get(self, request):
        """
        Arguments:
            request (dict): Request data to handle.

        Model:
            object (EC2Instance): First instance of EC2Instance model.

        Templates:
            `no_instance.html`: If AWS-account has no instances or
            `homepage.html`
        """
        if EC2Instance.objects.all().count() == 0:
            return render(request, 'no_instances.html', )

        return render(request, self.template_name, )


class Instance(generic.ListView):
    """
    View present instance`s details and selection all instance menu.

    Model:
        `EC2Instance`

    Templates:
        `instance.html`: Detail for corresponding instance.
    """
    model = EC2Instance
    template_name = 'instance.html'

    def get_context_data(self, **kwargs):
        """
        Arguments:
            kwargs (dict): Request data to handle.

        Return:
            context (dict): {..., 'instances': ...,
                             'instance': ...,
                             'all_instances_cost': ...}}
            instances (querySet): QuerySet of instances from EC2Instance model.
            instance (EC2Instance): Needed object from `EC2Instance` model by id.
            all_instances_cost (float): Total cost of all instances from creation to now.
        """
        context = super(Instance, self).get_context_data(**kwargs)

        context['instances'] = EC2Instance.objects.all()
        context['instance'] = get_object_or_404(EC2Instance, instance_id=self.kwargs['instance'])

        all_instances_cost = sum([instance.overall_cost_all_time for instance in EC2Instance.objects.all()])
        context['all_instances_cost'] = round(all_instances_cost, 2)

        return context


class LoginError(View):
    """
    View render warning template, that user has bad credentials for login.

    Templates:
        `bad_credentials.html`
    """
    template_name = 'bad_credentials.html'

    def get(self, request):
        return render(request, self.template_name, )


class AfterLoginRedirect(RedirectView):
    """
    Redirect view generate first instance, because LOGIN_URL in setting does not provide slugs as like pk or name.
    """
    @staticmethod
    def get_redirect_url():
        return reverse('ec2:instance', kwargs={'instance': EC2Instance.objects.all()[0].instance_id})
