


def get_client_ip(request):
	x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
	if x_forwarded_for:
		ip = x_forwarded_for.split(",")[0]
		print(ip, "En ligne")

	else:
		ip = request.META.get("REMOTE_ADDR",None)
		print(ip, "Local")


	return ip