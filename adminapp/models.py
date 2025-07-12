from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('adminuser','AdminUser'),
        ('regularuser', 'Regularuser'),
    )
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default=None, 
        null=True, 
        blank=True
    )

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey('User', related_name='reviews', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')  # Prevent duplicate reviews

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating})"

