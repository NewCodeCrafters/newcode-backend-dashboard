from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from apps.users.models import User
from apps.payments.models import PaymentPlan
from apps.batch.models import Batch
from .models import Notification



@receiver(post_save, sender=User)
def create_signup_notification(sender, instance, created, **kwargs):
    if created:
        staff_members = User.objects.filter(is_staff=True).exclude(email__isnull=True)

        subject = "New User Signup"
        message = (
            f"A new user has signed up:\n\n"
            f"Name: {instance.get_full_name()}\n"
            f"Email: {instance.email}\n"
            f"User Type: {instance.user_type}\n"
        )

        recipient_list = [staff.email for staff in staff_members if staff.email]
        if recipient_list:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)

        for staff in staff_members:
            Notification.objects.create(
                recipient=staff,
                notification_type="NEW_SIGNUP",
                title="New User Signup",
                message=f"{instance.get_full_name()} just registered as a new user.",
                related_user=instance,
            )



@receiver(post_save, sender=PaymentPlan)
def payment_notification(sender, instance, created, **kwargs):
    if created:
        staff_members = User.objects.filter(is_staff=True).exclude(email__isnull=True)

        subject = "New Payment Plan Created"
        message = (
            f"A new payment plan has been created for {instance.student.get_full_name()}.\n\n"
            f"Total Amount: ₦{instance.total_amount}\n"
            f"Installments: {instance.number_of_installments}\n"
            f"Frequency: {instance.frequency}\n"
            f"Start Date: {instance.start_date.strftime('%Y-%m-%d')}\n"
        )

    

        for staff in staff_members:
            Notification.objects.create(
                recipient=staff,
                notification_type="PAYMENT_RECEIVED",
                title="New Payment Plan Created",
                message=f"A new payment plan was created for {instance.student.get_full_name()} (₦{instance.total_amount}).",
                related_payment=instance,
            )


@receiver(post_save, sender=Batch)
def batch_created_notification(sender, instance, created, **kwargs):
    if created:
        staff_members = User.objects.filter(is_staff=True).exclude(email__isnull=True)

        subject_staff = "New Batch Created"
        message_staff = f"A new batch '{instance.batch_name}' has been created."

        recipient_list_staff = [staff.email for staff in staff_members if staff.email]
        if recipient_list_staff:
            send_mail(subject_staff, message_staff, settings.DEFAULT_FROM_EMAIL, recipient_list_staff, fail_silently=False)

        for staff in staff_members:
            Notification.objects.create(
                recipient=staff,
                notification_type="BATCH_CREATED",
                title="New Batch Created",
                message=f"A new batch '{instance.batch_name}' has been created.",
                related_batch=instance,
            )

        student_users = User.objects.filter(is_staff=False).exclude(email__isnull=True)

        subject_students = "New Batch Available!"
        message_students = f"A new batch '{instance.batch_name}' is now open for enrollment."

        recipient_list_students = [student.email for student in student_users if student.email]
        if recipient_list_students:
            send_mail(subject_students, message_students, settings.DEFAULT_FROM_EMAIL, recipient_list_students, fail_silently=False)

        for student in student_users:
            Notification.objects.create(
                recipient=student,
                notification_type="NEW_BATCH_AVAILABLE",
                title="New Batch Available",
                message=f"A new batch '{instance.batch_name}' is now open for enrollment.",
                related_batch=instance,
            )

