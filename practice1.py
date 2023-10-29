import logging

logger = logging.getLogger(__name__)


class UpdateSerializer:

    fields = None

    def serialize(self, data):

        result = ''

        keys = list(data.keys())
        if keys:
            key = keys[0]
            if data.get(key):
                result += f'{key}=%({key})s'
            for key in keys[1:]:
                if data.get(key):
                    result += f', {key}=%({key})s'

        return result

    def updatefields(self, data):

        if not (data and isinstance(data, dict)):
            logger.error('SerializerError: data is not valid')
            return None

        return self.serialize(data)


class UserUpdateSerializer(UpdateSerializer):

    fields = ['first_name', 'last_name', 'email']


class ClientSerializer(UpdateSerializer):

    fields = ['first_name', 'last_name', 'email', 'phone']


class InsertSerializer:

    fields = None

    def serialize(self, data):

        columns, values = '', ''

        if self.fields:
            field = self.fields[0]
            if data.get(field):
                columns += f'{field}'
                values += f'%({field})s'
            for field in self.fields[1:]:
                if data.get(field):
                    columns += f', {field}'
                    values += f', %({field})s'

        return columns, values

    def insertfields(self, data):

        if not (data and isinstance(data, dict)):
            logger.error('SerializerError: data is not valid')
            return None

        return self.serialize(data)


class UserInsertSerializer(InsertSerializer):

    fields = ['username', 'password', 'email']


class AppointmentSerializer(InsertSerializer):

    fields = ['pet_id', 'reason', 'datetime', 'description', 'doctor_id']


class AddressSerializer(InsertSerializer):

    fields = ['line_1', 'line_2', 'city', 'state']
