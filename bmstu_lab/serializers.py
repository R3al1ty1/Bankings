from rest_framework import serializers
from .models import Account, AccountApplication, AccountStatus, Applications, CardTerms, CreditTerms, \
    DepositTerms, SaveTerms, CustomUser, Agreement


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'type', 'name', 'amount', 'number', 'currency', 'bic', 'account_status_refer', 'user_id_refer', 'icon', 'available', 'delete_date']


class CardTermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardTerms
        fields = ['id', 'number', 'cvv', 'holder_first_name', 'holder_last_name', 'maintenance_cost', 'exp_date',
                  'number_ref']

class AccountCardSerializer(serializers.ModelSerializer):
    card = CardTermsSerializer(many=True, read_only=True, source='cardterms_set')
    class Meta:
        model = Account
        fields = ['id', 'type', 'name', 'amount', 'number', 'currency', 'bic', 'account_status_refer', 'user_id_refer', 'icon', 'available', 'card']

class CreditTermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditTerms
        fields = ['id', 'interest_rate', 'payment_amount', 'creation_date', 'end_date', 'agreement',
                  'payments_number', 'purpose', 'number_ref']


class AccountCreditSerializer(serializers.ModelSerializer):
    credit = CreditTermsSerializer(many=True, read_only=True, source='creditterms_set')

    class Meta:
        model = Account
        fields = ['id', 'type', 'name', 'amount', 'number', 'currency', 'bic', 'account_status_refer', 'user_id_refer',
                  'icon', 'available', 'credit']

class DepositTermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositTerms
        fields = ['id', 'interest_rate', 'creation_date', 'end_date', 'agreement', 'days', 'number_ref']


class AccountDepositSerializer(serializers.ModelSerializer):
    deposit = DepositTermsSerializer(many=True, read_only=True, source='depositterms_set')

    class Meta:
        model = Account
        fields = ['id', 'type', 'name', 'amount', 'number', 'currency', 'bic', 'account_status_refer', 'user_id_refer',
                  'icon', 'available', 'deposit']

class SaveTermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaveTerms
        fields = ['id', 'interest_rate', 'number_ref']


class AccountSaveSerializer(serializers.ModelSerializer):
    save = SaveTermsSerializer(many=True, read_only=True, source='saveterms_set')

    class Meta:
        model = Account
        fields = ['id', 'type', 'name', 'amount', 'number', 'currency', 'bic', 'account_status_refer', 'user_id_refer',
                  'icon', 'available', 'save']

class AgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agreement
        fields = ['id', 'type', 'description', 'small_desc', 'available']

class AccountApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountApplication
        fields = ['id', 'application_id', 'account_id', 'account', 'number', 'agreement_id']

class AccountApplicationSmallSerializer(serializers.ModelSerializer):
    account = AccountSerializer()
    class Meta:
        model = AccountApplication
        fields = ['account']

class AccountStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountStatus
        fields = ['id', 'frozen']

class ApplicationsSerializer(serializers.ModelSerializer):
    accounts = AccountApplicationSerializer(many=True, read_only=True)

    class Meta:
        model = Applications
        fields = ['id', 'creation_date', 'procession_date', 'completion_date', 'user', 'agreement_refer', 'status', 'moderator', 'accounts']


# class UsersSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Users
#         fields = ['id', 'full_name', 'email', 'password', 'is_staff', 'is_superuser']
#
# class UserSerializer(serializers.ModelSerializer):
#     is_staff = serializers.BooleanField(default=False, required=False)
#     is_superuser = serializers.BooleanField(default=False, required=False)
#     class Meta:
#         model = Users
#         fields = ['email', 'password', 'is_staff', 'is_superuser']

class UserRegisterSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(required=False)
    is_superuser = serializers.BooleanField(required=False)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'password', 'full_name', 'is_staff', 'is_superuser')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        is_staff = validated_data.pop('is_staff', False)
        is_superuser = validated_data.pop('is_superuser', False)

        user = CustomUser.objects.create(
            full_name=validated_data['full_name'],
            email=validated_data['email']
        )


        user.set_password(validated_data['password'])

        user.is_staff = is_staff
        user.is_superuser = is_superuser

        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class RefreshTokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)