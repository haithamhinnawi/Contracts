from django.utils import timezone
from .models import Contract, Job, Profile
from .serializers import ContractSerializer, JobSerializer, ProfileSerializer
from django.contrib.auth import authenticate, login
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, F

@api_view(['POST'])
@permission_classes([AllowAny])
def user_signup(request):
    '''
    This view is to make a signup operation for user.
    '''
    serializer = ProfileSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'detail': 'User registered successfully.','data': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    '''
    This view is to make a login operation for user.
    '''
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    else:
        return Response({'detail': 'Invalid username and password'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def contract_detail(request, pk):
    '''
    This view is to let user see details of a specific contract
    from his contracts only.
    '''
    contract = get_object_or_404(Contract, pk=pk)
    user = request.user.pk
    if contract.client.pk == user or contract.contractor.pk == user:
        serializer = ContractSerializer(contract)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'detail': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def list_contracts(request):
    '''
    This view let the user see all of their contracts.
    '''
    contract_status = request.GET.get('status', None)
    user = request.user.pk
    queryset = Contract.objects.select_related('client', 'contractor').filter(
        Q(client__pk=user) | Q(contractor__pk=user))
    if contract_status is not None:
        contracts = queryset.filter(status=contract_status)
    else:
        contracts = queryset.filter(Q(status='new') | Q(status='in_progress'))
    if contracts:
        serializer = ContractSerializer(contracts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'No contracts found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_profile(request):
    '''
    This view let the user see his profile information.
    '''
    user = request.user.pk
    profile = Profile.objects.get(pk=user)
    serializer = ProfileSerializer(profile)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_jobs(request):
    '''
    This view let the user see his jobs.
    '''
    user = request.user.pk
    user_jobs = Job.objects.select_related('contract__client', 'contract__contractor').filter(
        Q(contract__client__pk=user) | Q(contract__contractor__pk=user))
    if user_jobs:
        serializer = JobSerializer(user_jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'No jobs found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_unpaid_jobs(request):
    '''
    This view is to let the user see his unpaid jobs.
    '''
    user = request.user.pk
    user_jobs = Job.objects.select_related('contract__client', 'contract__contractor').filter(
        Q(contract__client__pk=user) | Q(contract__contractor__pk=user))
    unpaid_jobs = user_jobs.filter(paid=False)
    if unpaid_jobs:
        serializer = JobSerializer(unpaid_jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'No jobs found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def pay_job(request, job_id):
    '''
    This view is to let the client pay one of his jobs. 
    '''
    user = request.user.pk
    job = get_object_or_404(Job, pk=job_id)
    if job.contract.client.pk == user:
        if job.paid == False:
            if job.contract.client.balance >= job.price:
                job.contract.client.balance = F('balance') - job.price
                job.contract.contractor.balance = F('balance') + job.price
                job.paid = True
                job.payment_date = timezone.now().date()
                job.save()
                job.contract.client.save()
                job.contract.contractor.save()
                serializer = JobSerializer(job)
                return (Response({'message': 'Job payed succesfully', 'job': serializer.data}, status=status.HTTP_200_OK))
            return (Response({'message': 'You dont have enough money to pay'}, status=status.HTTP_200_OK))
        return (Response({'message': 'Job already payed'}, status=status.HTTP_200_OK))
    return Response({'message': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def deposite_money(request, user_id):
    '''
    This view let the user to deposite money in his account,
    but the money should be less than 25% of his unpaid jobs price.
    '''
    user = request.user.pk
    money = request.data.get('money')
    check_user = get_object_or_404(Profile, pk=user_id)
    if check_user.pk != user:
        return Response({'message': 'Access denied.'}, status=status.HTTP_403_FORBIDDEN)
    balance = check_user.balance
    result = Job.objects.select_related('contract__client').filter(
        Q(contract__client__pk=user) & Q(paid=False)).aggregate(result=Sum('price'))['result'] or 0
    if money > (result * 0.25):
        return Response({'message': 'You cannot deposite more that 25% of total of jobs to pay'}, status=status.HTTP_200_OK)
    else:
        check_user.balance = F('balance') + money
        check_user.save()
        return Response({'message': 'Deposite succesfully'}, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def best_profession(request):
    '''
    This view is to see which profession got the best salary
    in a specific period of time.
    '''
    start = request.GET.get('start', None)
    end = request.GET.get('end', None)
    if start and end:
        result = (
            Profile.objects.filter(
                contractor_contracts__job__payment_date__range=[start, end], contractor_contracts__job__paid = True)
            .values('profession')
            .annotate(total_earning=Sum('contractor_contracts__job__price'))
            .order_by('-total_earning')
            .first()
        )
    if result:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'No data found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def best_clients(request):
    '''
    This view is to see which clients paid the most
    in a specific period of time.
    '''
    start = request.GET.get('start', None)
    end = request.GET.get('end', None)
    limit = request.GET.get('limit', 2)
    if start and end:
        result = (
            Profile.objects.filter(
                client_contracts__job__payment_date__range=[start, end],
                client_contracts__job__paid=True
            )
            .values('id', 'first_name', 'last_name')
            .annotate(total_spent=Sum('client_contracts__job__price'))
            .order_by('-total_spent')[:int(limit)]
        )
    if result:
        return Response(result, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'No data found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])   
def list_profiles(request):
    profile = Profile.objects.all()
    serializer = ProfileSerializer(profile, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
