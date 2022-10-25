import peewee as orm
from playhouse.shortcuts import ThreadSafeDatabaseMetadata


db_proxy = orm.DatabaseProxy()


class BaseModel(orm.Model):
    class Meta:
        database = db_proxy
        model_metadata_class = ThreadSafeDatabaseMetadata


class Aircraft(BaseModel):
    class Meta:
        table_name = "aircrafts"
    
    tail_no = orm.CharField(8, column_name='tail_no', primary_key=True)
    mfr = orm.CharField(column_name='mfr')
    model = orm.CharField(column_name='model')
    bday = orm.DateField(column_name='bday')
    photo = orm.CharField(column_name='photo')


class Airport(BaseModel):
    class Meta:
        table_name = "airports"

    iata = orm.CharField(3, column_name='iata', primary_key=True)
    fullname = orm.CharField(column_name='fullname')
    city = orm.CharField(column_name='city')
    state = orm.CharField(column_name='_state')
    country = orm.CharField(column_name='country')
    lat = orm.DecimalField(6, 3, column_name='lat')
    lng = orm.DecimalField(6, 3, column_name='lng')


class Airline(BaseModel):
    class Meta:
        table_name = "airlines"
    
    airline_id = orm.CharField(2, column_name='airline_id', primary_key=True)
    fullname = orm.CharField(column_name='fullname')
    addr = orm.CharField(column_name='addr')
    phone_no = orm.CharField(22, column_name='phone_no')   


class Flight(BaseModel):
    class Meta:
        table_name = "delays"
    
    # flight_id = orm.AutoField(primary_key=True, column_name='delay_id')
    id = orm.IdentityField(primary_key=True, generate_always=True, column_name='delay_id')
    flight_date = orm.DateField(column_name='flight_date')
    day_of_week = orm.IntegerField(column_name='day_of_week')
    tail_no = orm.ForeignKeyField(Aircraft, to_field='tail_no', column_name='tail_no')
    airline_id = orm.ForeignKeyField(Airline, to_field='airline_id', column_name='airline_id')
    flight_id = orm.IntegerField(column_name='flight_id')
    origin = orm.ForeignKeyField(Airport, to_field='iata', column_name='origin')
    dest = orm.ForeignKeyField(Airport, to_field='iata', column_name='dest')
    dist = orm.DecimalField(7, 2, column_name='dist')
    scheduled_time = orm.TimeField(column_name='scheduled_time')
    real_time = orm.TimeField(column_name='real_time')
    delayed = orm.BitField(column_name='delayed')
    diverted = orm.BitField(column_name='diverted')
    cancelled = orm.BitField(column_name='cancelled')


class GrantedRole(BaseModel):
    class Meta:
        table_name = "admin_grantedroles"

    id = orm.IdentityField(primary_key=True, generate_always=True, column_name='role_id')
    role_name = orm.CharField(column_name='role_name')
    token = orm.CharField(column_name='token')