from django.db import models

# Create your models here.

class Customer(models.Model):
    PENDING = 'Pending'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'
    COMPLETE = 'Complete'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (COMPLETE, 'Complete')
    ]

    user_id = models.AutoField(primary_key=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    person_name = models.CharField(max_length=100)
    age = models.IntegerField(blank=True, null=True)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    appointment_end_time = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)

    class Meta:
        db_table = 'mytable'


class Users(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128)
    confirm_password = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        # Ensure password and confirm_password match before saving
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        super(Users, self).save(*args, **kwargs)

    def __str__(self):
        return self.username
