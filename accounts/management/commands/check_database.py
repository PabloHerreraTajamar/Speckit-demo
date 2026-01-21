"""
Management command to check database contents.
"""
from django.core.management.base import BaseCommand
from accounts.models import User
from tasks.models import Task
from attachments.models import Attachment


class Command(BaseCommand):
    help = 'Check database contents - users, tasks, and attachments'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== DATABASE CHECK ===\n'))
        
        # Users
        self.stdout.write(self.style.HTTP_INFO('USERS:'))
        user_count = User.objects.count()
        self.stdout.write(f'Total users: {user_count}\n')
        
        for user in User.objects.all().order_by('-date_joined')[:10]:
            self.stdout.write(f'  - {user.email} ({user.username})')
            self.stdout.write(f'    Name: {user.first_name} {user.last_name}')
            self.stdout.write(f'    Active: {user.is_active}, Staff: {user.is_staff}')
            self.stdout.write(f'    Joined: {user.date_joined}')
            self.stdout.write(f'    Tasks: {user.tasks.count()}')
            self.stdout.write('')
        
        # Tasks
        self.stdout.write(self.style.HTTP_INFO('\nTASKS:'))
        task_count = Task.objects.count()
        self.stdout.write(f'Total tasks: {task_count}\n')
        
        for task in Task.objects.all().order_by('-created_at')[:10]:
            self.stdout.write(f'  - {task.title}')
            self.stdout.write(f'    Status: {task.get_status_display()}, Priority: {task.get_priority_display()}')
            self.stdout.write(f'    Owner: {task.owner.email}')
            self.stdout.write(f'    Created: {task.created_at}')
            self.stdout.write(f'    Attachments: {task.attachments.count()}')
            self.stdout.write('')
        
        # Attachments
        self.stdout.write(self.style.HTTP_INFO('\nATTACHMENTS:'))
        attachment_count = Attachment.objects.count()
        self.stdout.write(f'Total attachments: {attachment_count}\n')
        
        for attachment in Attachment.objects.all().order_by('-uploaded_at')[:10]:
            self.stdout.write(f'  - {attachment.original_filename}')
            self.stdout.write(f'    Task: {attachment.task.title}')
            self.stdout.write(f'    Owner: {attachment.task.owner.email}')
            self.stdout.write(f'    Size: {attachment.file_size / 1024:.2f} KB')
            self.stdout.write(f'    Uploaded: {attachment.uploaded_at}')
            self.stdout.write('')
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== SUMMARY ==='))
        self.stdout.write(f'Users: {user_count}')
        self.stdout.write(f'Tasks: {task_count}')
        self.stdout.write(f'Attachments: {attachment_count}')
        self.stdout.write(self.style.SUCCESS('\nDatabase check completed!\n'))
