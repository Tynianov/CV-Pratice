import cv2
import numpy as np

from rest_framework.response import Response
from rest_framework.views import APIView

from iris.iris_recognition.recognition import encode_photo
from iris.models import PersonIris


class IrisRecognizeAPIView(APIView):
    def post(self, request, *args, **kwargs):
        image = request.FILES.get('image')

        if not image:
            return Response('Image required', status=400)

        try:
            image_bytes = image.read()
            np_array = np.asarray(bytearray(image_bytes), dtype=np.uint8)

            encoded_image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
            code, mask = encode_photo(encoded_image)

            result = []
            for iris in PersonIris.objects.all():
                recognize = iris.compare_iris(code, mask)
                if recognize:
                    result.append(recognize)

            if result:
                return Response(result, status=200)
            return Response('Not Found', status=404)
        except Exception as e:
            print(e)
            return Response('Smth went wrong', status=400)
