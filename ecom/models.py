from django.db import models

class Product_Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
class Producer(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    description = models.CharField(blank=True)
    
    def __str__(self):
        return self.name    
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField()
    price = models.DecimalField(max_digits=10, decimal_places=2, min=0)
    quantity_in_stock = models.IntegerField(min=0)
    category = models.ForeignKey(Product_Category, on_delete=models.CASCADE)
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
        
    
    
    