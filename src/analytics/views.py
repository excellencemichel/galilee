import datetime
import random

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from django.utils.decorators import method_decorator
from django.utils import timezone

from django.contrib.auth.decorators import login_required


from django.views.generic import TemplateView , View

from django.db.models import Avg, Count, Sum

#Local import

from orders.models import Order 
# Create your views here.

@method_decorator(login_required, name='dispatch')
class SalesAjaxView(View):
	template_name = "analytics/sales.html"

	def get(self, request, *args, **kwargs):
		data = {}
		if request.user.is_staff_user:
			qs = Order.objects.all().by_weeks_range(weeks_ago=5, number_of_weeks=5)

			if request.GET.get("type") == "week":
				days = 7
				start_date = timezone.now().today() - datetime.timedelta(days=days-1)
				print(start_date)
				# datetime_list = [start_date + datetime.timedelta(days=x) for x in range(0, days)]
				datetime_list = []
				labels = []
				salesItems = []
				for x in range(0, days):
					new_time = start_date + datetime.timedelta(days=x)
					datetime_list.append(
						new_time
						)

					labels.append(
						new_time.strftime("%a"))

					new_qs = qs.filter(updated__day=new_time.day, updated__month=new_time.month)
					day_total = new_qs.totals_data()["total__sum"] or 0

					salesItems.append(
						day_total
						)

				# print(datetime_list)
				data["labels"] = labels
				data["data"] = salesItems

			if request.GET.get("type") == "4weeks":
				data["labels"] = ["Four weeks ago", "Three weeks ago", "Two weeks ago", "Last weeks", "This week"]
				current = 5
				data["data"] = []
				for i in range(0,5):
					print(i)
					new_qs = qs.by_weeks_range(weeks_ago=current, number_of_weeks=1)
					sales_total = new_qs.totals_data()["total__sum"] or 0

					data["data"].append(sales_total)
					current -=1
		return JsonResponse(data)


@method_decorator(login_required, name='dispatch')
class SalesView(TemplateView):
	template_name = "analytics/sales.html"

	def dispatch(self, *args, **kwargs):
		user = self.request.user
		if not user.is_staff_user:
			return render(self.request, "400.html",  {})

		return super(SalesView, self).dispatch(*args, **kwargs)


	def get_context_data(self, *args, **kwargs):
		context = super(SalesView, self).get_context_data(*args, **kwargs)
		# two_weeks_ego = timezone.now() - datetime.timedelta(days=7)
		# two_weeks_ego = timezone.now() - datetime.timedelta(days=7)

		qs = Order.objects.all().by_weeks_range(weeks_ago=10, number_of_weeks=10)
		context["today"] = qs.by_range(start_date=timezone.now().date()).get_sales_breakdown()
		context["this_week"] = qs.by_weeks_range(weeks_ago=1, number_of_weeks=1).get_sales_breakdown()
		context["last_four_weeks"] = qs.by_weeks_range(weeks_ago=5, number_of_weeks=4).get_sales_breakdown()


		return context