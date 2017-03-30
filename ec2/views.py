from django.shortcuts import get_object_or_404
from .models import Instance as EC2Instance
from django.views.generic import View
from django.shortcuts import render
from django.views import generic
from django.http import Http404


class Homepage(View):
    template_name = 'homepage.html'

    def get(self, request):
        if EC2Instance.objects.all().count() == 0:
            return render(request, 'no_instances.html', )

        return render(request, self.template_name, {'basic_instance': EC2Instance.objects.all()[0].instance_id})


class Instance(generic.ListView):
    model = EC2Instance
    template_name = 'instance.html'

    def get_context_data(self, **kwargs):
        context = super(Instance, self).get_context_data(**kwargs)

        if self.kwargs['user'] == 'chief' or self.kwargs['user'] == 'employee':
            context['user'] = self.kwargs['user']
        else:
            raise Http404

        context['instances'] = EC2Instance.objects.all()
        context['instance'] = get_object_or_404(EC2Instance, instance_id=self.kwargs['instance'])

        return context
