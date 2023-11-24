from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class StockPurchase(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner.username} - {self.symbol} - {self.purchase_date}"
    
    class Meta:
        ordering : ['-purchase_date']