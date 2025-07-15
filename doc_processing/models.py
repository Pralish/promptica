from django.db import models
import os

class Document(models.Model):
    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # If title is empty and we have a file, use the filename
        if not self.title and self.file:
            # Get the filename without extension
            filename = os.path.splitext(self.file.name)[0]
            # Remove any path components to get just the filename
            self.title = os.path.basename(filename)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title