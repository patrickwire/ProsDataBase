# Create your views here.
# -*- coding: UTF-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
import json
from django.contrib import auth

from ..response import *
from ..serializers import *
from ..forms import *
from .. import tablefactory
from .. import historyfactory
from django.utils.translation import ugettext_lazy as _


def session(request):
    if request.method == 'POST':
        return register(request)
    elif request.method == 'PUT':
        return login(request)
    elif request.method == 'DELETE':
        return logoff(request)


def users(request):
    if request.method == 'GET':
        return showAllUsers()


def user(request, name):
    if request.method == 'GET':
        return showOneUser(name)


def userRights(request):
    if request.user.userManager or request.user.admin :
        if request.method == 'GET':
            return showUserRights(request)
        if request.method == 'POST':
            return modifyUserRights(request)
    else:
        return HttpResponse('{"errors":[{"message":"'+(_("You have not the rights to do this opperation").__unicode__())+'"}]}',content_type="application/json")


def groups(request):
    if request.method == 'GET':
        return showAllGroups()
    elif request.method == 'POST':
        if request.user.userManager or request.user.admin :
            return addGroup(request)
        else:
            return HttpResponse('{"errors":[{"message":"'+(_("You have not the rights to do this opperation").__unicode__())+'"}]}',content_type="application/json")


def group(request, name):
    if request.method == 'GET':
        return showOneGroup(name)
    if request.user.userManager or request.user.admin :
        if request.method == 'PUT':
            return modifyGroup(request, name)
        if request.method == 'DELETE':
            return deleteGroup(request, name)
    else:
        return HttpResponse('{"errors":[{"message":"'+(_("You have not the rights to do this opperation").__unicode__())+'"}]}',content_type="application/json")


def myself(request):
    if request.method == 'GET':
        return showMyUser(request.user.username)


def myPassword(request):
    if request.method == 'POST':
        return checkMyPassword(request)
    if request.method == 'PUT':
        return changeMyPassword(request)


def categories(request):
    if request.method == 'GET':
        return showCategories()
    if request.user.admin :
        if request.method == 'PUT':
            return tablefactory.modifyCategories(request)
    else:
        return HttpResponse('{"errors":[{"message":"'+(_("You have not the rights to do this opperation").__unicode__())+'"}]}',content_type="application/json")



def category(request, name):
    if request.user.admin :
        if request.method == 'DELETE':
            return tablefactory.deleteCategory(name)
    else:
        return HttpResponse('{"errors":[{"message":"'+(_("You have not the rights to do this opperation").__unicode__())+'"}]}',content_type="application/json")



def tables(request):
    if request.method == 'GET':
        return showAllTables(request.user)
    if request.method == 'POST':
        if request.user.admin or request.user.tableCreator :
            return tablefactory.createTable(request)


def table(request, name):
    if request.method == 'GET':
        return showTable(name, request.user)
    if request.method == 'POST':
        return tablefactory.insertData(request, name)
    if request.method == 'PUT':
        return tablefactory.modifyTable(request, name)
    if request.method == "DELETE":
        return tablefactory.deleteTable(name, request.user)


def tableRights(request, tableName):
    if request.method == 'GET':
        return showTableRights(tableName)


def column(request, tableName, columnName):
    if request.method == 'DELETE':
        answer = tablefactory.deleteColumn(tableName, columnName, request.user)
        if not answer:
            return HttpResponse(json.dumps({"errors": [answer]}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"success": _("Successfully deleted column ").__unicode__() + columnName + _(" from table ").__unicode__() + tableName + "."}), content_type="application/json")


def export(request, tableName):
    if request.method == 'POST':
        return tablefactory.exportTable(json.loads(request.raw_post_data), tableName)


def tableHistory(request, tableName):
    if request.method == 'GET':
        response = TableSerializer.serializeHistory(tableName)
        if not response:
            return HttpResponse(json.dumps({"errors": [{"code": Error.TABLE_NOTFOUND, "message": _("Could not find table with name ").__unicode__() + tableName + "."}]}), content_type="application/json")
        return HttpResponse(json.dumps(response), content_type="application/json")


def datasets(request, tableName):
    if request.method == 'POST':
        #if request.user.mayReadTable(tableName):
        return showDatasets(request, tableName)  # request.user)
        #else:
        #    return HttpResponse("Permission denied", status=403)
    if request.method == 'DELETE':
        #if request.user.mayDeleteTable(tableName):
        return tablefactory.deleteDatasets(request, tableName)

       # else:
       #     return HttpResponse("Permission denied", status=403)


def filterDatasets(request, tableName):
    if request.method == 'POST':
        datasets = DatasetSerializer.serializeBy(json.loads(request.raw_post_data), tableName, request.user)
        if datasets is None:
            return HttpResponse(json.dumps({"errors": [{"code": Error.DATASET_NOTFOUND, "message": _("No matching datasets.").__unicode__()}]}), content_type="application/json")
        return HttpResponse(json.dumps(datasets), content_type="application/json")


def dataset(request, tableName, datasetID):
    if request.method == 'GET':
        return showDataset(tableName, datasetID, user)
    elif request.method == 'PUT':
        return tablefactory.modifyData(request, tableName, datasetID)


def register(request):
    jsonRequest = json.loads(request.raw_post_data)
    try:
        DBUser.objects.get(username=jsonRequest["username"])
        return HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("user with name ").__unicode__() + jsonRequest["username"] + _(" already exists.").__unicode__()}]}),content_type="application/json")
    except DBUser.DoesNotExist:
        user = DBUser.objects.create_user(username=jsonRequest["username"], password=jsonRequest["password"])
        user.save()
        historyfactory.writeAuthHistory(None, user, HistoryAuth.USER_REGISTERED)
        return HttpResponse(json.dumps({"success": _("Account is created").__unicode__()}), content_type="application/json")


def login(request):
    jsonRequest = json.loads(request.raw_post_data)
    user = auth.authenticate(username=jsonRequest["username"], password=jsonRequest["password"])
    if user is not None and user.is_active:
        auth.login(request, user)
        return HttpResponse(json.dumps({"status": "ok"}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"status": "not_ok"}), content_type="application/json")


def logoff(request):
    auth.logout(request)
    return HttpResponse(_("logged off"))


def showAllUsers():
    users = UserSerializer.serializeAll()
    return HttpResponse(json.dumps(users), content_type="application/json")


def showOneUser(name):
    user = UserSerializer.serializeOne(name)
    if user is None:
        return HttpResponse(json.dumps({"errors": [{"code": -1, "message": _("User does not exist").__unicode__()}]}), content_type="application/json")
    else:
        return HttpResponse(json.dumps(user), content_type="application/json")


def showUserRights(request):
    rights = UserSerializer.serializeAllWithRights()
    return HttpResponse(json.dumps(rights), content_type="application/json")


def modifyUserRights(request):
    jsonRequest = json.loads(request.raw_post_data)

    message = ""  # message for writing into history
    for userObj in jsonRequest["users"]:
        # for tracking changes made
        tableCreatorChanged = False
        userManagerChanged = False
        activeChanged = False
        modified = False
        try:
            user = DBUser.objects.get(username=userObj["name"])
        except DBUser.DoesNotExist:
            HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("Could not find user with name ").__unicode__() + userObj["name"] + "."}]}), content_type="application/json")

        if userObj["tableCreator"] != user.tableCreator:
            modified = True
            tableCreatorChanged = True
        if userObj["userManager"] != user.userManager:
            modified = True
            userManagerChanged = True
        if userObj["active"] != user.is_active:
            modified = True
            activeChanged = True

        user.tableCreator = userObj["tableCreator"]
        user.userManager = userObj["userManager"]
        user.is_active = userObj["active"]
        if modified:
            user.save()

            message += "User " + userObj["name"] + ": "
            if activeChanged:
                if user.is_active:
                    message += "has been activated, "
                else:
                    message += "has been deactivated, "
            if tableCreatorChanged:
                if user.tableCreator:
                    message += "can create tables now, "
                else:
                    message += "cannot create tables anymore, "
            if userManagerChanged:
                if user.userManager:
                    message += "has become user manager."
                else:
                    message += "is no user manager anymore."
            message += "\n"  # cut off trailing comma

    historyfactory.writeAuthHistory(None, request.user, HistoryAuth.USER_MODIFIED, message)
    return HttpResponse(json.dumps({"success": _("Successfully modified user rights.").__unicode__()}), content_type="application/json")


def showAllGroups():
    groups = GroupSerializer.serializeAll()
    return HttpResponse(json.dumps(groups), content_type="application/json")


def showOneGroup(name):
    group = GroupSerializer.serializeOne(name)
    return HttpResponse(json.dumps(group), content_type="application/json")


def addGroup(request):
    request = json.loads(request.raw_post_data)

    groupNames = list()
    for name in DBGroup.objects.all():
        groupNames.append(name)

    if request["name"] in groupNames:
        HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("Group with name ").__unicode__() + request["name"] + _(" already exists.").__unicode__()}]}), content_type="application/json")

    groupF = DBGroupForm({"name": request["name"]})
    if groupF.is_valid():
        newGroup = groupF.save(commit=False)
        newGroup.tableCreator = request["tableCreator"]
        newGroup.save()

        failed = list()  # list of users whose names could not be found in the database

        for userName in set(request["users"]):
            try:
                user = DBUser.objects.get(username=userName)
            except DBUser.DoesNotExist:
                if len(userName) > 0:
                    failed.append(userName)
                continue
            membership = Membership(group=newGroup, user=user)
            membership.save()

    if len(failed) > 0:
        return HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("following users could not be added to the group: ") + str(failed) + _(". Have you misspelled them?")}]}), content_type="application/json")

    message = historyfactory.printGroup(request["name"])
    historyfactory.writeAuthHistory(None, request.user, HistoryAuth.GROUP_CREATED, historyfactory.writeAuthHistory(None, request.user, HistoryAuth.GROUP_CREATED, message))
    return HttpResponse(json.dumps({"success": _("Successfully saved group ").__unicode__() + request["name"] + "."}),content_type="application/json")


def modifyGroup(request, name):
    """
    {
        "name": "group1",
        "users": ["John Doe","Alex Anonymus"],
        "admins": ["admin1", "admin2"],
        "tableCreator": true,
    }
    """
    try:
        group = DBGroup.objects.get(name=name)
    except DBGroup.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("Could not find group with name ").__unicode__() + name + "."}]}), content_type="application/json")


    # will hold content for history entry
    oldName = None
    tableCreatorChanged = False
    userRemoved = list()
    userAdded = list()

    jsonRequest = json.loads(request.raw_post_data)
    if jsonRequest["name"] != group.name:
        try:
            DBGroup.objects.get(name=jsonRequest["name"])
            return HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("A group with name ").__unicode__() + jsonRequest["name"] + _(" already exists.").__unicode__()}]}), content_type="application/json")
        except DBGroup.DoesNotExist:
            oldName = group.name
            group.name = jsonRequest["name"]

    if jsonRequest["tableCreator"] != group.tableCreator:
        tableCreatorChanged = True
        group.tableCreator = jsonRequest["tableCreator"]
    group.save()

    usernames = list()
    for m in Membership.objects.filter(group=group):
        usernames.append(m.user.username)

    sendUsers = set(jsonRequest["users"])

    for user in set(sendUsers) - set(usernames):  # new users were added to the group
        if len(user) > 0:  # workaround. frontend always sends one empty string
            membershipF = MembershipForm({"isAdmin": False})
            if membershipF.is_valid():
                membership = membershipF.save(commit=False)
                membership.user = DBUser.objects.get(username=user)
                membership.group = group
                membership.save()
            userAdded.append(user)

    for user in set(usernames) - set(sendUsers):  # users were deleted from the group
        theUser = DBUser.objects.get(username=user)
        membership = Membership.objects.get(user=theUser, group=group)
        membership.delete()
        userRemoved.append(user)

    # write modification to history
    message = "Group " + jsonRequest["name"] + ": \n"
    if oldName is not None:
        message += _("Changed name from '").__unicode__() + oldName + _("' to '").__unicode__() + jsonRequest["name"] + "'.\n"
    if tableCreatorChanged:
        if group.tableCreator:
            message += "Can now create tables.\n"
        else:
            message += "Cannot create tables anymore.\n"
    if len(userAdded) > 0:
        message += "New users: "
        for user in userAdded:
            message += user + ", "
        message = message[:-2] + "\n"  # cut off trailing comma
    if len(userRemoved) > 0:
        message += "Removed users: "
        for user in userRemoved:
            message += user + ", "
        message = message[:-2] + "\n"  # cut off trailing comma
    historyfactory.writeAuthHistory(None, request.user, HistoryAuth.GROUP_MODIFIED, message)

    return HttpResponse(json.dumps({"success": _("Successfully modifed group ").__unicode__() + name + "."}), content_type="applciation/json")


def deleteGroup(request, name):
    try:
        group = DBGroup.objects.get(name=name)
    except DBGroup.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("Could not find group with name ").__unicode__() + name + "."}]}), content_type="application/json")

    Membership.objects.filter(group=group).delete()
    group.delete()

    historyfactory.writeAuthHistory(None, request.user, HistoryAuth.GROUP_DELETED)
    return HttpResponse(json.dumps({"success": _("Successfully deleted group ").__unicode__() + name + "."}), content_type="application/json")


def showMyUser(user):
    myself = UserSerializer.serializeOne(user)
    return HttpResponse(json.dumps(myself), content_type="application/json")


def checkMyPassword(request):
    jsonRequest = json.loads(request.raw_post_data)

    response = dict()
    response["valid"] = request.user.check_password(jsonRequest["password"])

    return HttpResponse(json.dumps(response), content_type="application/json")


def changeMyPassword(request):
    jsonRequest = json.loads(request.raw_post_data)
    request.user.set_password(jsonRequest["password"])
    request.user.save()
    #TODO JSON
    return HttpResponse(json.dumps({"success" : _("Saved password successfully.")}),content_type="application/jon")


def showCategories():
    categories = TableSerializer.serializeCategories()
    return HttpResponse(json.dumps(categories), content_type="application/json")


def showTableRights(name):
    rights = TableSerializer.serializeRightsFor(name)
    return HttpResponse(json.dumps(rights), content_type="application/json")


def tableStructure(request, name):
    if request.method == 'GET':
        structure = TableSerializer.serializeStructure(name, request.user)
        return HttpResponse(json.dumps(structure), content_type="application/json")


def showDatasets(request, tableName):
    try:
        Table.objects.get(name=tableName, deleted=False)
    except Table.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("Could not find table with name ").__unicode__() + tableName + "."}]}), content_type="application/json")

    jsonRequest = json.loads(request.raw_post_data)
    result = dict()
    result["datasets"] = list()
    for obj in jsonRequest["datasets"]:
        result["datasets"].append(DatasetSerializer.serializeOne(obj["id"], request.user))

    return HttpResponse(json.dumps(result), content_type="application/json")


def showDataset(tableName, datasetID, user):
    try:
        table = Table.objects.get(name=tableName, deleted=False)
    except Table.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("Table with name ").__unicode__() + tableName + _(" could not be found.").__unicode__()}]}), content_type="application/json")
    try:
        dataset = Dataset.objects.get(datasetID=datasetID, table=table)
    except Dataset.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("dataset with id ").__unicode__() + datasetID + _(" could not be found in table ").__unicode__() + tableName + "."}]}), content_type="application/json")

    if dataset.deleted:
        return HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("The requested dataset does not exist.").__unicode__()}]}),content_type="application/json")
    else:
        dataset = DatasetSerializer.serializeOne(datasetID, user)
        return HttpResponse(json.dumps(dataset), content_type="application/json")


def showAllTables(user):
    tables = TableSerializer.serializeAll(user)
    return HttpResponse(json.dumps(tables), content_type="application/json") if tables is not None \
        else HttpResponse(json.dumps({"errors": [{"code": Error.USER_NOTFOUND, "message": _("Table could not be found").__unicode__()}]}),content_type="application/json")


def showTable(name, user):
    table = TableSerializer.serializeOne(name, user)
    return HttpResponse(json.dumps(table), content_type="application/json")