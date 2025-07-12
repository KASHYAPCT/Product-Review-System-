from rest_framework.response import Response
from rest_framework.decorators import APIView
from rest_framework import status
from .serializers import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import Product, Review
from rest_framework.permissions import AllowAny




class AdminCreate(APIView):
    def get(self, request, format=None):
        superadmin = User.objects.filter(role='adminuser')
        serializer = UserSerializer(superadmin, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
        
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():   
            serializer.save(role='adminuser')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Login(APIView):
    def post(self, request, format=None):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        
        u = authenticate(request, username=username, password=password)
        if u and u.role in ['adminuser', 'regularuser']:
            serializer = UserSerializer(u)
            token, created = Token.objects.get_or_create(user=u)
            return Response({
                "user": serializer.data,
                "role": u.role,
                "token": token.key
            }, status=status.HTTP_200_OK)
        return Response({"details": "invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class RegularUserCreate(APIView):
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(role='regularuser')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductListCreate(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
   
    def get(self, request, format=None):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        if request.user.role != 'adminuser':
            return Response({'detail': 'Only admin users can add products.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetail(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes=[TokenAuthentication]
    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return None

    def put(self, request, pk, format=None):
        if request.user.role != 'adminuser':
            return Response({'detail': 'Only admin users can edit products.'}, status=status.HTTP_403_FORBIDDEN)
        product = self.get_object(pk)
        if not product:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        if request.user.role != 'adminuser':
            return Response({'detail': 'Only admin users can delete products.'}, status=status.HTTP_403_FORBIDDEN)
        product = self.get_object(pk)
        if not product:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        product.delete()
        return Response({'message':'successfully deleted the product'},status=status.HTTP_204_NO_CONTENT)

class ReviewListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, product_id, format=None):
        reviews = Review.objects.filter(product_id=product_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, product_id, format=None):
        if request.user.role != 'regularuser':
            return Response({'detail': 'Only regular users can submit reviews.'}, status=status.HTTP_403_FORBIDDEN)
        # Prevent duplicate reviews
        if Review.objects.filter(product_id=product_id, user=request.user).exists():
            return Response({'detail': 'You have already reviewed this product.'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data.copy()
        data['product'] = product_id
        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)