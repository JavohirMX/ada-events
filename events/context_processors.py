def notifications_unread_count(request):
    if request.user.is_authenticated:
        return {
            "notifications_unread_count": request.user.notifications.filter(
                is_read=False
            ).count()
        }
    return {"notifications_unread_count": 0}
