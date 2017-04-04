"""
Views for EC-2 application to work with AWS`s EC-2 instances.
"""

from django.shortcuts import get_object_or_404
from .models import Instance as EC2Instance
from django.views.generic import View
from django.shortcuts import render
from django.views import generic
from django.http import Http404


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
            object (EC2Instance): first instance of EC2Instance model

        Templates:
            `no_instance.html`: If AWS-account has no instances
            `homepage.html` and object (EC2Instance): first one EC2Instance object`s data.
        """
        if EC2Instance.objects.all().count() == 0:
            return render(request, 'no_instances.html', )

        return render(request, self.template_name, {'basic_instance': EC2Instance.objects.all()[0].instance_id})


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
            context (dict): {..., 'user': ...,
                             'instances': ...,
                             'instance': ...}}
            user (str): URL-parameter, that consider as position`s choice.
            instances (querySet): QuerySet of instances from EC2Instance model.
            instance (EC2Instance): Needed object from `EC2Instance` model by id.

        Raises:
            Http404 if type of position or instance id does not exist.
        """
        context = super(Instance, self).get_context_data(**kwargs)

        if self.kwargs['user'] == 'chief' or self.kwargs['user'] == 'employee':
            context['user'] = self.kwargs['user']
        else:
            raise Http404

        context['instances'] = EC2Instance.objects.all()
        context['instance'] = get_object_or_404(EC2Instance, instance_id=self.kwargs['instance'])

        return context
