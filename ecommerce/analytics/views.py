from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, Avg
from django.utils import timezone

from orders.models import Order

import datetime

# Create your views here.

class SalesAjaxView(View):
    def get(self, request, *args, **kwargs):
        json_data = {}
        if request.user.is_staff:
            qs = Order.objects.all().by_weeks_range(weeks_ago = 10, number_of_weeks = 10)
            if request.GET.get('type') == 'week':
                days = 7
                start_date = timezone.now().today() - datetime.timedelta(days = days - 1)
                datetime_list, labels, sales_items = [], [], []
                for x in range(0, days):
                    new_time = start_date + datetime.timedelta(days = x)
                    datetime_list.append(new_time)
                    labels.append(new_time.strftime('%a'))
                    new_qs = qs.filter(updated__day = new_time.day, updated__month = new_time.month)
                    sales_total = new_qs.totals_data()['total__sum'] or 0
                    sales_items.append(sales_total)

                json_data['labels'] = labels
                json_data['data'] = sales_items
            if request.GET.get('type') == '4weeks':
                json_data['labels'] = ['Fifth week', 'Fourth week', 'Third week', 'Last week', 'This week']
                current = 5
                json_data['data'] = []
                for i in range(0, 5):
                    new_qs = qs.by_weeks_range(weeks_ago = current, number_of_weeks = 1)
                    sales_total = new_qs.totals_data()['total__sum'] or 0
                    json_data['data'].append(sales_total)
                    current -= 1
        return JsonResponse(json_data)

class SalesView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/sales.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_staff:
            return render(request, '403.html', {})
        return super(SalesView, self).dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super(SalesView, self).get_context_data(**kwargs)
        qs = Order.objects.all().by_weeks_range(weeks_ago = 10, number_of_weeks = 10)
        context['today'] = qs.by_range(start_date = timezone.now().date()).get_sales_breakdown()
        context['this_week'] = qs.by_weeks_range(weeks_ago = 1, number_of_weeks = 1).get_sales_breakdown()
        context['last_four_weeks'] = qs.by_weeks_range(weeks_ago = 4, number_of_weeks = 4).get_sales_breakdown()
        return context

        # context['orders'] = qs
        # context['recent_orders'] = qs.recent().not_refunded()
        # context['recent_orders_data'] = context['recent_orders'].totals_data()
        # context['recent_orders_cart_data'] = context['recent_orders'].cart_data()
        # context['shipped_orders'] = qs.recent().not_refunded().by_status(status = 'shipped')
        # context['shipped_orders_data'] = context['shipped_orders'].totals_data()
        # context['paid_orders'] = qs.recent().not_refunded().by_status(status = 'paid')
        # context['paid_orders_data'] = context['paid_orders'].totals_data()
    