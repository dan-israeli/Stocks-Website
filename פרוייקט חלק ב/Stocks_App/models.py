
from django.db import models


class Buying(models.Model):
    tdate = models.OneToOneField('Stock', models.DO_NOTHING, db_column='tDate', primary_key=True)
    id = models.ForeignKey('Investor', models.DO_NOTHING, db_column='ID')
    symbol = models.ForeignKey('Stock', models.DO_NOTHING, db_column='Symbol',related_name='+')
    bquantity = models.IntegerField(db_column='BQuantity', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Buying'
        unique_together = (('tdate', 'id', 'symbol'),)


class Company(models.Model):
    symbol = models.CharField(db_column='Symbol', primary_key=True, max_length=10)
    sector = models.CharField(db_column='Sector', max_length=40, blank=True, null=True)
    location = models.CharField(db_column='Location', max_length=40, blank=True, null=True)
    founded = models.IntegerField(db_column='Founded', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Company'


class Investor(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    name = models.CharField(db_column='Name', max_length=40, blank=True, null=True)
    availablecash = models.IntegerField(db_column='AvailableCash', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Investor'


class Stock(models.Model):
    symbol = models.OneToOneField(Company, models.DO_NOTHING, db_column='Symbol', primary_key=True)
    tdate = models.DateField(db_column='tDate')
    price = models.FloatField(db_column='Price', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Stock'
        unique_together = (('symbol', 'tdate'),)


class Transactions(models.Model):
    tdate = models.DateField(db_column='tDate', primary_key=True)
    id = models.ForeignKey(Investor, models.DO_NOTHING, db_column='ID')
    tquantity = models.IntegerField(db_column='TQuantity', blank=True, null=True) 

    class Meta:
        managed = False
        db_table = 'Transactions'
        unique_together = (('tdate', 'id'),)


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
