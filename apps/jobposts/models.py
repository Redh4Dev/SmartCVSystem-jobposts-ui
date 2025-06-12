from django.db import models

from apps.authx.models import User

class JobPost(models.Model):
    JobPostID           = models.AutoField(primary_key=True, db_column='JobPostID')
    Recruiter           = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='RecruiterID',
        related_name='job_posts'
    )
    Title               = models.CharField(max_length=255, db_column='Title')
    Description         = models.TextField(db_column='Description')
    RequiredSkills      = models.TextField(db_column='RequiredSkills')
    Location            = models.CharField(max_length=255, db_column='Location')
    
    EMPLOYMENT_CHOICES = [
        ('FT', 'Full-time'),
        ('PT', 'Part-time'),
        ('CT', 'Contract'),
        ('IN', 'Internship'),
    ]
    EmploymentType      = models.CharField(
        max_length=2,
        choices=EMPLOYMENT_CHOICES,
        default='FT',
        blank=True,
        db_column='EmploymentType'
    )
    
    MinSalary           = models.IntegerField(null=True, blank=True, db_column='MinSalary')
    MaxSalary           = models.IntegerField(null=True, blank=True, db_column='MaxSalary')
    
    REMOTE_CHOICES = [
        ('Onsite', 'On-site'),
        ('Remote', 'Remote'),
        ('Hybrid', 'Hybrid'),
    ]
    RemoteOption        = models.CharField(
        max_length=6,
        choices=REMOTE_CHOICES,
        db_column='RemoteOption'
    )
    
    Industry            = models.CharField(max_length=100, null=True, blank=True, db_column='Industry')
    
    EXPERIENCE_LEVELS = [
        ('Entry',  'Entry'),
        ('Mid',    'Mid'),
        ('Senior', 'Senior'),
        ('Dir',    'Director'),
    ]
    ExperienceLevel     = models.CharField(
        max_length=6,
        choices=EXPERIENCE_LEVELS,
        default='BA',
        blank=True, 
        db_column='ExperienceLevel'
    )
    
    EDUCATION_LEVELS = [
        ('HS',  'High School'),
        ('BA',  'Bachelor’s'),
        ('MA',  'Master’s'),
        ('PhD', 'PhD'),
    ]
    EducationLevel      = models.CharField(
        max_length=3,
        null=True,
        blank=True,
        choices=EDUCATION_LEVELS,
        db_column='EducationLevel'
    )
    
    ApplicationDeadline = models.DateField(null=True, blank=True, db_column='ApplicationDeadline')
    Benefits            = models.TextField(null=True, blank=True, db_column='Benefits')
    
    CreatedAt           = models.DateTimeField(auto_now_add=True, db_column='CreatedAt')
    UpdatedAt           = models.DateTimeField(auto_now=True,     db_column='UpdatedAt')
    IsActive            = models.BooleanField(default=True,       db_column='IsActive')

    class Meta:
        db_table = 'JobPost'
        ordering = ['-CreatedAt']
        verbose_name = 'Job Post'
        verbose_name_plural = 'Job Posts'

    def __str__(self):
        return f"{self.Title} (by {self.Recruiter.username})"
    
class UserJob(models.Model):
    UserJobID     = models.AutoField(primary_key=True, db_column='UserJobID')
    User          = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column='UserID',
        related_name='user_jobs'
    )
    JobPost       = models.ForeignKey(
        JobPost,
        on_delete=models.CASCADE,
        db_column='JobPostID',
        related_name='applicants'
    )
    IsApplied     = models.BooleanField(default=False,              db_column='IsApplied')
    IsSaved       = models.BooleanField(default=False,              db_column='IsSaved')
    IsUnapplied   = models.BooleanField(default=False,              db_column='IsUnapplied')
    CreatedAt     = models.DateTimeField(auto_now_add=True,         db_column='CreatedAt')
    SoftDelete    = models.BooleanField(default=False,              db_column='SoftDelete')
    DeletedAt     = models.DateTimeField(null=True, blank=True,     db_column='DeletedAt')

    class Meta:
        db_table = 'UserJob'
        verbose_name = 'User–Job Link'
        verbose_name_plural = 'User–Job Links'
        constraints = [
            models.UniqueConstraint(
                fields=['User', 'JobPost'],
                name='uq_userjob_user_job'
            )
        ]
        indexes = [
            models.Index(fields=['User'], name='ix_userjob_user'),
            models.Index(fields=['JobPost'], name='ix_userjob_job'),
        ]

    def __str__(self):
        return f"{self.User.username} → {self.JobPost.Title}"