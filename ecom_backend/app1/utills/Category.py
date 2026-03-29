from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Category
from ..serializers import CategorySerializer


@api_view(["GET"])
def category_list(request):
    cate = Category.objects.filter(is_active=True)
    data= CategorySerializer(cate,many=True,context={'request': request})
    return Response({"data":data.data})