from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(max_length=200, upload_to="files/")
    # sha256 = models.CharField(max_length=64,db_index=True)