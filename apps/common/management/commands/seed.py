import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.authx.models     import Role, Permission, UsersRole, RolePermission
from apps.profiles.models  import UserProfile
from apps.common.models    import Company, CompanyUser, ShortlistStatus

User = get_user_model()

class Command(BaseCommand):
    help = "Seed initial roles, permissions, companies, statuses, users, and company-user links"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("⏳ Seeding Roles…"))
        role_names = ["Admin", "Consultant", "CompanyHR", "Candidate"]
        roles = {}
        for name in role_names:
            role, created = Role.objects.get_or_create(
                role_name=name,
                defaults={"role_description": f"{name} role"}
            )
            roles[name] = role
            if created:
                self.stdout.write(f"  • Created Role: {name}")

        self.stdout.write(self.style.NOTICE("⏳ Seeding Permissions…"))
        perm_names = [
            "create_jobpost", "edit_jobpost", "delete_jobpost",
            "view_resume", "parse_resume",
            "match_candidate", "shortlist_candidate",
            "export_report"
        ]
        perms = {}
        for pname in perm_names:
            perm, created = Permission.objects.get_or_create(
                permission_name=pname
            )
            perms[pname] = perm
            if created:
                self.stdout.write(f"  • Created Permission: {pname}")

        self.stdout.write(self.style.NOTICE("⏳ Assigning Permissions to Roles…"))
        RolePermission.objects.all().delete()
        # Admin gets everything
        for perm in perms.values():
            RolePermission.objects.create(role=roles["Admin"], permission=perm)
        # Consultant: jobpost + view + match
        for pname in ["create_jobpost", "edit_jobpost", "delete_jobpost", "view_resume", "match_candidate"]:
            RolePermission.objects.create(role=roles["Consultant"], permission=perms[pname])
        # CompanyHR: view, match, shortlist, export
        for pname in ["view_resume", "match_candidate", "shortlist_candidate", "export_report"]:
            RolePermission.objects.create(role=roles["CompanyHR"], permission=perms[pname])
        # Candidate: view own resume, export report
        for pname in ["view_resume", "export_report"]:
            RolePermission.objects.create(role=roles["Candidate"], permission=perms[pname])

        self.stdout.write(self.style.NOTICE("⏳ Seeding Shortlist Statuses…"))
        statuses = ["shortlisted", "interview", "rejected"]
        for s in statuses:
            status_obj, created = ShortlistStatus.objects.get_or_create(name=s)
            if created:
                self.stdout.write(f"  • Created ShortlistStatus: {s}")

        self.stdout.write(self.style.NOTICE("⏳ Seeding Companies…"))
        company_data = [
            ("Acme Corp", "123 Acme Way", "https://acme.example.com"),
            ("Globex Inc", "456 Globex Blvd", "https://globex.example.com"),
        ]
        companies = {}
        for name, addr, site in company_data:
            comp, created = Company.objects.get_or_create(
                name=name,
                defaults={"address": addr, "website": site}
            )
            companies[name] = comp
            if created:
                self.stdout.write(f"  • Created Company: {name}")

        self.stdout.write(self.style.NOTICE("⏳ Seeding Users…"))
        sample_users = ["admin", "consultant1", "hr1", "candidate1"]
        User.objects.filter(username__in=sample_users).delete()

        samples = [
            ("admin",      "admin@smartcv.local",     "adminpass",   "Admin",      None),
            ("consultant1","consult1@smartcv.local",  "consultpass", "Consultant", "Globex Inc"),
            ("hr1",        "hr1@smartcv.local",       "hrpass",      "CompanyHR",  "Acme Corp"),
            ("candidate1", "cand1@smartcv.local",     "candpass",    "Candidate",  None),
        ]
        for username, email, pw, role_name, company_name in samples:
            user = User.objects.create_user(
                username=username, email=email, password=pw, status=role_name.lower()
            )
            UsersRole.objects.create(user=user, role=roles[role_name])
            UserProfile.objects.create(
                user=user,
                phone=f"000-{random.randint(100,999)}-{random.randint(1000,9999)}",
                location=role_name
            )
            # link user to company if provided
            if company_name:
                CompanyUser.objects.create(user=user, company=companies[company_name])
            self.stdout.write(f"  • Created User: {username} ({role_name})")

        self.stdout.write(self.style.SUCCESS("✅ Database seeding complete!"))
