import threading
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

from .models import User, Role, UsersRole, Company, CompanyUser, UserProfile


def _send_welcome_email(user):
    """
    Compose and send a welcome email synchronously.
    """
    subject = f"Welcome to {settings.SITE_NAME}!"
    html_body = render_to_string("emails/welcome.html", {
        "user": user,
        "site_name": settings.SITE_NAME,
    })
    text_body = (
        f"Hi {user.first_name},\n\n"
        f"Thanks for registering at {settings.SITE_NAME}.\n\n"
        "— The Team"
    )
    email = EmailMessage(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    # Uncomment for HTML
    # email.body = html_body
    # email.content_subtype = 'html'
    email.send(fail_silently=False)


def send_welcome_email_async(user):
    """
    Fire off the welcome email in a background thread.
    """
    threading.Thread(
        target=_send_welcome_email,
        args=(user,),
        daemon=True
    ).start()


def register_user(user_data, company_data=None):
    """
    Create a new User and related objects (role, company, profile),
    then send a welcome email asynchronously.

    `user_data` should include keys:
      first_name, last_name, email, username, password (raw), role_id

    `company_data` (optional) should include:
      name, address, website
    """
    with transaction.atomic():
        # 1) Create the user (raw password is stored as-is)
        user = User.objects.create(
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            email=user_data['email'],
            username=user_data['username'],
            password=user_data['password'],
            is_active=True,
            is_staff=False,
        )

        # 2) Assign role via UsersRole
        role_id = user_data.get('role_id')
        print(role_id)
        if role_id:
            UsersRole.objects.create(
                user_id=user.users_id,
                role_id=int(role_id),
            )
            role_obj = Role.objects.get(pk=role_id)
            print(  role_obj  )
            # 3) If company_hr, create Company + CompanyUser
            role_name = role_obj.role_name.lower()
            print(  role_name  )
            print(  role_name in ('company hr', 'recruiter')  )
            print(  company_data  )
            if role_name in ('company hr', 'recruiter') and company_data:
                print(  company_data  )
                company = Company.objects.create(
                    name=company_data['name'],
                    address=company_data['address'],
                    website=company_data['website'],
                )
                CompanyUser.objects.create(
                    user_id=user.users_id,
                    company_id=company.id,
                )

        # 4) Create a blank profile
        UserProfile.objects.create(
            user_id=user.users_id,
            phone='',
            location='',
            avatar='',
        )

    # 5) Send welcome email without blocking
    send_welcome_email_async(user)
    return user
