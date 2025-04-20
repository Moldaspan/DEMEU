from celery import shared_task
from .models import Publication
from django.utils import timezone
from datetime import timedelta


@shared_task
def check_publication_status():
    print("🕒 Циклическая задача запущена: проверка публикаций")

    now = timezone.now()
    three_months_ago = now - timedelta(days=90)
    publications = Publication.objects.filter(status='active')
    for pub in publications:
        donated = pub.total_donated()
        if donated >= pub.amount:
            pub.status = 'successful'
            pub.is_archived = True
            pub.save()
            print(f"[✓] {pub.title} marked as successful.")
        elif pub.expires_at and pub.expires_at <= now:
            pub.status = 'expired'
            pub.is_archived = True
            pub.save()
            print(f"[⌛] {pub.title} expired and archived.")

    # Удаляем публикации, которые были архивированы более 3 месяцев назад
    old_archived = Publication.objects.filter(is_archived=True, updated_at__lte=three_months_ago)
    count = old_archived.count()
    old_archived.delete()
    if count:
        print(f"[🗑] Удалено {count} архивных публикаций старше 3 месяцев.")


@shared_task
def notify_expiring_publications():
    from django.utils import timezone
    from datetime import timedelta
    from publications.models import Publication
    from notifications.utils import notify_user

    now = timezone.now()
    tomorrow = now + timedelta(days=1)
    today = now.date()

    # За день до истечения
    almost_expired = Publication.objects.filter(
        expires_at__date=tomorrow.date(),
        status='active',
    )

    for pub in almost_expired:
        notify_user(
            user=pub.author,
            verb="⏰ Ваша публикация скоро истекает",
            target=pub.title,
            url=f"/post/{pub.id}"
        )

    # В день истечения
    expiring_today = Publication.objects.filter(
        expires_at__date=today,
        status='active',
    )

    for pub in expiring_today:
        notify_user(
            user=pub.author,
            verb="❗ Сегодня заканчивается срок вашей публикации",
            target=pub.title,
            url=f"/post/{pub.id}"
        )
