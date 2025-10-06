from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import StudentBatchEnrollment


@receiver(post_save, sender=StudentBatchEnrollment)
def notify_admin_on_enrollment(sender, instance, created, **kwargs):
    if created:
        student = instance.student
        batch = instance.batch
        course = instance.course

        subject = f"New Student Enrollment: {student.get_full_name()}"
        message = (
            f"Hello Mr Bello Abdulhakeem,\n\n"
            f"A new student has just enrolled in a course.\n\n"
            f"👤 Student Name: {student.get_full_name()}\n"
            f"📧 Email: {student.email}\n"
            f"📘 Course: {course}\n"
            f"🏷️ Batch: {batch.batch_name}\n"
            f"💰 Total Fee: ₦{instance.total_fee}\n"
            f"💸 Discount: ₦{instance.discount_amount}\n"
            f"✅ Final Fee: ₦{instance.final_fee}\n"
            f"📅 Enrollment Date: {instance.enrollment_date}\n"
            f"📍 Status: {instance.status}\n\n"
            f"Kind regards,\n"
            f"Your Academy Management System"
        )

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                fail_silently=False,
            )
            print(f"✅ Enrollment email sent to {settings.ADMIN_EMAIL}")
        except Exception as e:
            print(f"❌ Failed to send enrollment email: {e}")
