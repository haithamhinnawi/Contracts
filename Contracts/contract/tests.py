from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import Contract, Job, Profile
from rest_framework.authtoken.models import Token

class ProfileTests(APITestCase):
    '''
    This class is to test signup and login to ensure that
    both work successfully.
    '''
    def setUp(self):
        self.client_data = {
            'first_name': 'test',
            'last_name': 'client',
            'profession': 'tester',
            'balance': 50000,
            'type': 'Client',
            'username': 'test_client',
            'password': 'testclient'
        }
        self.tmp_data = {
            'first_name': 'test',
            'last_name': 'client',
            'profession': 'tester',
            'balance': 50000,
            'type': 'Client',
            'username': 'tmp_client',
            'password': 'testclient'
        }
        self.contractor_data = {
            'first_name': 'test',
            'last_name': 'contractor',
            'profession': 'tester',
            'balance': 50000,
            'type': 'Contractor',
            'username': 'test_contractor',
            'password': 'testcontractor'
        }
        self.tmp_user = Profile.objects.create_user(**self.tmp_data)
        self.client_user = Profile.objects.create_user(**self.client_data)
        self.contractor_user = Profile.objects.create_user(**self.contractor_data)
        self.contract_data = {
            'client': self.client_user,
            'contractor': self.contractor_user, 
            'terms': 'Test Contract',
            'status': 'new',
        }
        self.contract1_data = {
            'client': self.tmp_user,
            'contractor': self.contractor_user, 
            'terms': 'Temp cont',
            'status': 'new',
        }
        self.contract = Contract.objects.create(**self.contract_data)
        self.contract1 = Contract.objects.create(**self.contract1_data)
        self.job_data = {
            'description': 'test job',
            'price': 1200, 
            'paid': False,
            'payment_date': '2023-12-01',
            'contract': self.contract,
        }
        self.job_tmp = {
            'description': 'test job',
            'price': 1200, 
            'paid': False,
            'payment_date': '2023-12-01',
            'contract': self.contract1,
        }
        self.job = Job.objects.create(**self.job_data)
        self.job1 = Job.objects.create(**self.job_tmp)
        self.client.login(username = 'test_client', password = 'testclient') 
        token = Token.objects.get(user__username='test_client')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def tearDown(self):
        self.client.logout()

    def test_user_signup(self):
        test_data = {
            'first_name': 'test',
            'last_name': 'user',
            'profession': 'tester',
            'balance': 50000,
            'type': 'Client',
            'username': 'testuser',
            'password': 'testuser'
        }
        response_signup = self.client.post(reverse('user-signup'), test_data, format='json')
        self.assertEqual(response_signup.status_code, status.HTTP_201_CREATED)

    def test_user_login(self):
        data_login = {
            'username': 'test_client',
            'password': 'testclient'
        }
        response_login = self.client.post(reverse('user-login'), data_login, format='json')
        self.assertEqual(response_login.status_code, status.HTTP_200_OK)
        self.assertIn('token', response_login.data)

    def test_user_login_unregistered(self):
        data_login = {
            'username': 'test',
            'password': 'testclient'
        }
        response_login = self.client.post(reverse('user-login'), data_login, format='json')
        self.assertEqual(response_login.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_contract_detail(self):
        url = reverse('contract-detail', args=[self.contract.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['terms'], 'Test Contract')

    def test_contract_detail_for_other_user(self):
        url = reverse('contract-detail', args=[self.contract1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_contracts(self):
        url = reverse('contract-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_contracts_unauthenticated(self):
        url = reverse('contract-list')
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_profile(self):
        url = reverse('profile-detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'test_client')

    def test_user_profile_unauthenticated(self):
        url = reverse('profile-detail')
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_jobs(self):
        url = reverse('user-jobs')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_jobs_unauthenticated(self):
        url = reverse('user-jobs')
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_unpaid_jobs(self):
        url = reverse('user-unpaid-jobs')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_user_unpaid_jobs_unauthenticated(self):
        url = reverse('user-unpaid-jobs')
        self.client.credentials()
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pay_user_job(self):
        url = reverse('pay-job', args=[self.job.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Job payed succesfully')
        self.assertEqual(response.data['job']['paid'], True)

    def test_pay_user_job_no_enough_money(self):
        url = reverse('pay-job', args=[self.job.id])
        self.job.price = 100000
        self.job.save()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'You dont have enough money to pay')

    def test_pay_user_job_already_paid(self):
        url = reverse('pay-job', args=[self.job.id])
        self.job.paid = True
        self.job.save()
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Job already payed')

    def test_pay_user_job_no_access_on_it(self):
        url = reverse('pay-job', args=[self.job1.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Access denied.')

    def test_deposite_money(self):
        url = reverse('deposite-money', args=[self.client_user.id])
        data = {'money': 200}
        money_before = self.client_user.balance
        response = self.client.post(url, data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Deposite succesfully')
        self.assertEqual(response.data['user']['balance'], (money_before + 200))

    def test_deposite_money_more_than_ratio(self):
        url = reverse('deposite-money', args=[self.client_user.id])
        data = {'money': 800}
        response = self.client.post(url, data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'You cannot deposite more that 25% of total of jobs to pay')

    def test_deposite_money_no_access_user(self):
        url = reverse('deposite-money', args=[self.contractor_user.id])
        data = {'money': 200}
        response = self.client.post(url, data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Access denied.')

    def test_best_profession(self):
        url = reverse('pay-job', args=[self.job.id])
        response = self.client.post(url) #pay job first
        url = reverse('best-profession')
        data =  {'start': '2023-11-26', 'end': '2023-11-28'}
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['profession'], self.client_user.profession)

    def test_best_profession_no_paid_jobs(self):
        url = reverse('best-profession')
        data =  {'start': '2023-11-26', 'end': '2023-11-28'}
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_best_clients(self):
        url = reverse('pay-job', args=[self.job.id])
        response = self.client.post(url) #pay job first
        url = reverse('best-clients')
        data =  {'start': '2023-11-26', 'end': '2023-11-28'}
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['first_name'], self.client_user.first_name)

    def test_best_clients_no_paid_jobs(self):
        url = reverse('best-clients')
        data =  {'start': '2023-11-26', 'end': '2023-11-28'}
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'No data found')