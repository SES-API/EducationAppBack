import os
from django import template
from django.conf import settings
from django.http.response import FileResponse
from django.shortcuts import render
from rest_framework.views import APIView

from .settings import MEDIA_ROOT
from .models import UploadedFile
from .serializers import UploadedFileSerializer
from django.http import HttpResponse
from django.template import Context, Template



from rest_framework import status
from rest_framework import parsers
from rest_framework import renderers
from rest_framework.response import Response


def files_list(request):
    return render(request,'CFG/files_list.html',{'total_files':os.listdir(MEDIA_ROOT/'files')})   




def download(request,file_name):
    print(MEDIA_ROOT)
    file_path = MEDIA_ROOT/"files"/file_name
    file_wrapper = open(file_path,"rb")
    # file_mimetype = mimetypes.guess_type(file_path)
    response = HttpResponse(file_wrapper)
    response['X-Sendfile'] = file_path
    response['Content-Length'] = os.stat(file_path).st_size
    response['Content-Disposition'] = 'attachment; filename={}'.format(os.path.basename(file_path))
    return response





class UploadFile(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.JSONParser,parsers.MultiPartParser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = UploadedFileSerializer

    def post(self, request):
        if not request.user.is_superuser:
            return Response('permision denied', status=status.HTTP_403_FORBIDDEN)

        uploaded_file = request.FILES.get('file',None)
        if not uploaded_file:
            return Response('No upload file was specified.', status=status.HTTP_400_BAD_REQUEST)
        instance = UploadedFile.objects.create(
                file = uploaded_file,)
        return Response("detail:done",status=status.HTTP_200_OK)