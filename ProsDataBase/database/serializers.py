# -*- coding: utf-8 -*-
__author__ = 'My-Tien Nguyen'

from models import *


import json


# TODO: how to convert CharFields to String? unicode(model.CharField()) or model.CharField().__unicode__()? Or entirely different?


class TableSerializer:
    @staticmethod
    def serializeOne(tableName):
        """
        return the table with specified name, along with its columns and datasets.

        {
            "name": "example",
            "columns": ["columname", "anothercolum"],
            "datasets": [
                [value, value],
                [value, value]
            ]
        }
        """
        table = Table.objects.get(name=tableName)

        if table is None:  # table does not exist!
            return False

        columns = table.getColumns()
        columnNames = []

        for col in columns:
            columnNames.append(col.name)

        datasets = table.getDatasets()
        for dataset in datasets:
            row = []
            data = dataset.getData()

            for primitiveData in data[0:Type.BOOL]:
                for item in primitiveData:
                    dataObj = dict()
                    dataObj["column"] = item.column.name
                    dataObj["value"] = item.content
                    row.push(dataObj)

            for tableData in data[Type.TABLE]:
                pass
        result = dict()
        result["name"] = table.name
        result["column"] = columnNames

        return json.dumps(result)

    @staticmethod
    def serializeAll():
        """
        return all tables with their columns

        {
            "tables": [
                {"name": "example", "columns": ["columname","anothercolum"]},
                {"name": "2nd", "columns": ["columname","anothercolum"]}
            ]
        }
        """
        tables = Table.objects.all()
        result = dict()
        result["tables"] = []

        for table in tables:
            columns = table.getColumns()
            columnNames = []

            for col in columns:
                columnNames.append(col.name)

            result["tables"].append({"name": table.name, "column": columnNames})

        return json.dumps(result)

    @staticmethod
    def serializeStructure(tableName):
        """
        return the table with its columns and the column's datatypes as well as ranges

        {
          "columns": [
            {"name": "columnname0", "type": 0, "length": 100},
            {"name": "columnname1", "type": 1, "min": "a decimal", "max": "a decimal"},
            {"name": "columnname2", "type": 2, "min": "a date", "max": "a date"},
            {"name": "columnname3", "type": 3, "options": {"0": "opt1", "1": "opt2", "2": "opt3"},
            {"name": "columnname4", "type": 4, "table": "tablename"},
          ]
        }
        """
        table = Table.objects.get(name=tableName)
        if table is None:
            return None

        columns = table.getColumns()
        colStructs = []
        for col in columns:
            type = col.type.type
            if type is Type.TEXT:
                colStructs.append({"name": col.name, "type": Type.TEXT, "legnth": col.type.getType().length})

            elif type is Type.NUMERIC or type is Type.DATE:
                colStructs.append({"name": col.name, "type": Type.DATE, "min": col.type.getType().min, "max": col.type.getType().max})

            elif type is Type.SELECTION:
                options = dict()
                for value in col.type.getType().values():
                    options[unicode(value.index)] = value.content
                colStructs.append({"name": col.name, "type": Type.SELECTION, "options": options})
            elif type is Type.BOOL:
                colStructs.append({"name": col.name, "type": Type.BOOL})
            elif type is Type.TABLE:
                colStructs.append({"name": col.name, "type": Type.TABLE, "table": col.type.getType().table.name})
            else:
                return None

        result = dict()
        result["columns"] = colStructs
        return json.dumps(result)


class UserSerializer:
    @staticmethod
    def serializeOne(id):
        """
        return table with specified id

        {"id":"1","name": "example"}
        """
        user = AbstractUser.objects.get(pk=id)

        result = dict()
        result["name"] = user.username
        result["id"] = user.id

        return json.dumps(result)

    @staticmethod
    def serializeAll():
        """
        return all tables with their columns

        {
            "users": [
                {"id":"1","name": "example"},
                {"id":"2","name": "example2"}]}
            ]
        }
        """
        users = DBUser.objects.all()
        result = dict()
        result["users"] = []

        for user in users:
            result["users"].append(user.username)

        return json.dumps(result)


class GroupSerializer:
    @staticmethod
    def serializeOne(id):
        """
        return table with specified id

        {"id":"1","name": "example"}
        """
        user = AbstractUser.objects.get(pk=id)

        result = dict()
        result["name"] = user.username
        result["id"] = user.id

        return json.dumps(result)

    @staticmethod
    def serializeAll():
        """
        return all tables with their columns

        {
            "users": [
               {"id":"1","name": "example"},
                {"id":"2","name": "example2"}]}
            ]
        }
        """
        groups = DBGroup.objects.all()
        result = dict()
        result["groups"] = []

        for group in groups:
            result["groups"].append(group.name)

        return json.dumps(result)


class DatasetSerializer:

    def serializeAll(self, tableRef):
        """
        return all datasets of table tableRef

        {
            "name": "example",
            "columns": ["columname", "anothercolum"],
            "datasets": [
                [value, value],
                [value, value]
            ]
        }
        """
        result = dict()
        result["name"] = tableRef.name

        columns = Column.objects.filter(table=tableRef)
        columnNames = []
        for col in columns:
            columnNames.append(col.name)
        result["columns"] = columnNames

        datasetList = []
        datasets = Dataset.objects.filter(table=tableRef)
        for dataset in datasets:
            values = dataset.getData().values()
            datasetList.append(values)
        result["datasets"] = datasetList

        return json.dumps(result)

    def serializeBy(self, tableRef, rangeFlag, filter):  # tuple of criteria-dicts
        result = dict()
        result["name"] = tableRef.name

        columns = Column.objects.filter(table=tableRef)
        columnNames = []
        for col in columns:
            columnNames.append(col.name)
        result["column"] = columnNames

        datasetList = []
        datasets = Dataset.objects.filter(table=tableRef)
        for crit in filter:
            if len(crit) < 3 and rangeFlag:
                for dataset in datasets:
                    field = crit.iterkeys().next()