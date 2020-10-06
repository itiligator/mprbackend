import os
import random
import uuid
import time

import jsonschema
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import ChecklistQuestionSerializer, PriceSerializer, ProductSerializer
from rest_framework.parsers import JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Order, Visit, ChecklistQuestion, ChecklistAnswer, Client, Photo, Price, Product


clients_path = os.path.join(settings.BASE_DIR, "static", "clients.json")
clients_schema = {
    "type": "array",
    "items": {
        "title": "Клиент",
        "type": "object",
        "description": "Данные клиента",
        "x-examples": {},
        "x-tags": [
            "1С",
            "Офис",
            "Фронтенд"
        ],
        "properties": {
            "name": {
                "type": "string",
                "description": "Наименование клиента для отображения пользователю"
            },
            "inn": {
                "type": "string",
                "description": "ИНН"
            },
            "clientType": {
                "type": "string",
                "description": "Тип клиента (хорека, драфт, магазин etc)"
            },
            "priceType": {
                "type": "string",
                "description": "Тип цен для клиента"
            },
            "delay": {
                "type": "integer",
                "default": 0,
                "description": "Отсрочка по договору",
                "format": "int32",
                "example": 0,
                "minimum": 0
            },
            "limit": {
                "type": "integer",
                "default": 0,
                "description": "Лимит",
                "format": "int64",
                "example": 0,
                "minimum": 0
            },
            "authorizedManagersID": {
                "type": "array",
                "description": "Массив ID менеджеров, для которых доступен клиент",
                "items": {
                    "type": "string"
                }
            },
            "email": {
                "type": "string",
                "format": "email"
            },
            "phone": {
                "type": "string"
            },
            "manager": {
                "type": "string",
                "description": "ID основного менеджера"
            },
            "longitude": {
                "type": "string"
            },
            "latitude": {
                "type": "string"
            },
            "status": {
                "type": "boolean",
                "default": "1",
                "description": "Действует/не действует"
            },
            "dataBase": {
                "type": "boolean",
                "description": "false - тест, true - ПБК"
            },
            "address": {
                "type": "string",
                "description": "Адрес клиента"
            }
        },
        "required": [
            "inn"
        ]
    },
}

visit_schema = {
    "title": "Визит",
    "type": "object",
    "description": "Данные по визитам",
    "properties": {
        "orders": {
            "type": "array",
            "description": "Массив данных о заказанных продуктах, остатке, продажах",
            "items": {
                "title": "Объект заказа",
                "type": "object",
                "description": "Объект описания заказанного, рекомендованного к заказу, остаточного и отгруженного "
                               "товара",
                "properties": {
                    "productItem": {
                        "type": "string",
                        "description": "Артикул продукта. Генерируется приложением МПР, никогда не изменяется"
                    },
                    "order": {
                        "type": "integer",
                        "description": "Заказанное количество продукта. Генерируется приложением МПР, изменяется "
                                       "приложением офиса "
                    },
                    "delivered": {
                        "description": "Количество поставленного продукт. По умолчанию установлено в 0, обновляется "
                                       "со стороны 1С",
                        "type": "integer"
                    },
                    "recommend": {
                        "type": "integer",
                        "description": "Рекомендованное к заказу количесво. Генерируется приложением МПР и никогда не "
                                       "изменяется "
                    },
                    "balance": {
                        "description": "Остаток продукта у клиента. Генерируется приложением МПР, изменяется "
                                       "приложением офиса",
                        "type": "integer"
                    },
                    "sales": {
                        "type": "integer",
                        "description": "Продажи продкукта. Генерируется приложением МПР, изменяется приложением офиса"
                    }
                },
                "required": [
                    "productItem"
                ]
            }
        },
        "UUID": {
            "type": "string",
            "description": "Уникальный идентификатор визита. Генерируется приложением МПР или офиса и никогда не изменяется",
            "format": "uuid"
        },
        "date": {
            "type": "string",
            "format": "date",
            "description": "Дата совершения визита. Генерируется приложением МПР и никогда не изменяется"
        },
        "dataBase": {
            "type": "boolean"
        },
        "clientINN": {
            "type": "string",
            "description": "ИНН клиента. Генерируется приложением МПР или офиса и никогда не изменяется"
        },
        "payment": {
            "description": "Сумма денег, принятых в счет оплаты. Генерируется приложением МПР, обновляется приложением офиса",
            "type": "integer"
        },
        "processed": {
            "type": "string",
            "description": "Номер накладной. Устанавливается в true со стороны 1С при создании накладной"
        },
        "invoice": {
            "type": "string",
            "description": "Номер ПКО. Устанавливается в true со стороны 1С при создании ПКО"
        },
        "status": {
            "type": "integer",
            "description": "Статус визита 0: не начат, 1: в работе, 2: завершен. Генерируется и обновляется приложениями МПР и офиса"
        },
        "managerID": {
            "type": "string",
            "description": "ID менеджера, который совершил (совершает) визит. Генерируется приложением МПР или офиса, никогда не изменяется"
        },
        "paymentPlan": {
            "type": "integer"
        },
        "author": {
            "type": "string",
            "description": "ID автора визита"
        },
        "id": {
            "type": "integer",
            "description": "Человекочитаемый ID"
        },
        "deliveryDate": {
            "type": "string",
            "format": "date",
            "description": "Дата доставки"
        }
    },
}

checklistanswers_schema = {
    "type": "array",
    "items":
        {
            "type": "object",
            "properties": {
                "questionUUID": {
                    "type": "string",
                    "description": "UUID вопроса",
                    "format": "uuid"
                },
                "visitUUID": {
                    "type": "string",
                    "description": "UUID визита, в котором был дан ответ",
                    "format": "uuid"
                },
                "answer1": {
                    "type": [
                        "string",
                        "boolean"
                    ],
                    "description": "Ответ на вопрос/количество"
                },
                "answer2": {
                    "type": "string",
                    "description": "Примечание/цена"
                },
                "UUID": {
                    "type": "string",
                    "description": "UUID ответа",
                    "format": "uuid"
                }
            },
            "required": [
                "questionUUID",
                "visitUUID"
            ]
        }
}


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def products(request):
    if request.method == 'GET':
        productsQ = Product.objects.all()
        active = request.query_params.get('active', None)
        if active:
            active = True if (active == "true" or active == "True") else False
            productsQ = productsQ.filter(active=active)
        serializer = ProductSerializer(productsQ, many=True)
        return JsonResponse(serializer.data, safe=False)
    if request.method == 'PUT':
        if request.user.userprofile.role == 'MPR':
            return Response("Only 1S and office can do it", status=status.HTTP_403_FORBIDDEN)
        data = JSONParser().parse(request)
        for product in data:
            try:
                instance = Product.objects.get(item=product['item'])
            except (KeyError, Product.DoesNotExist):
                instance = None
            serializer = ProductSerializer(instance=instance, data=product)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('Ok', status=status.HTTP_200_OK)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def prices(request):
    if request.method == 'GET':
        product_item = request.query_params.get('productItem', None)
        price_type = request.query_params.get('priceType', None)
        database = request.query_params.get('DB', None)
        pricesQ = Price.objects.all()
        if product_item:
            product_item = True if (product_item == "true" or product_item == "True") else False
            pricesQ = pricesQ.filter(product_item=product_item)
        if price_type:
            price_type = True if (price_type == "true" or price_type == "True") else False
            pricesQ = pricesQ.filter(price_type=price_type)
        if database:
            database = True if (database == "true" or database == "True") else False
            pricesQ = pricesQ.filter(database=database)
        serializer = PriceSerializer(pricesQ, many=True)
        return JsonResponse(serializer.data, safe=False)
    if request.method == 'PUT':
        if request.user.userprofile.role != '1S':
            return Response("Only 1S can do it", status=status.HTTP_403_FORBIDDEN)
        data = JSONParser().parse(request)
        for price in data:
            try:
                instance = Price.objects.get(
                    product_item=price['productItem'],
                    price_type=price['priceType'],
                    database=price['dataBase'])
            except (KeyError, Price.DoesNotExist):
                instance = None
            serializer = PriceSerializer(instance=instance, data=price)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('Ok', status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def users(request):
    if request.user.userprofile.role == 'MPR' or request.user.userprofile.role == '1S':
        data = {
            'firstName': request.user.first_name,
            'lastName': request.user.last_name,
            'ID': request.user.userprofile.manager_ID
        }
        return JsonResponse(data, safe=False)
    elif request.user.userprofile.role == 'OFFICE':
        managers = User.objects.all()
        data = []
        for user in managers:
            data.append({
                'firstName': user.first_name,
                'lastName': user.last_name,
                'ID': user.userprofile.manager_ID,
                'role': user.userprofile.role
            })
        return JsonResponse(data, safe=False)
    return Response({}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def usersme(request):
    data = {
        'firstName': request.user.first_name,
        'lastName': request.user.last_name,
        'ID': request.user.userprofile.manager_ID
    }
    return JsonResponse(data, safe=False)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def clients(request):
    if request.method == 'GET':
        q = Client.objects.all()
        manager = None

        if request.user.userprofile.role == 'MPR':
            manager = request.user
        managerID = request.query_params.get('managerID', None)
        if managerID:
            try:
                manager = User.objects.get(userprofile__manager_ID=managerID)
            except User.DoesNotExist:
                return Response("Can't find manager with such ID", status=status.HTTP_400_BAD_REQUEST)

        inn = request.query_params.get('inn', None)
        client_type = request.query_params.get('clientType', None)
        price_type = request.query_params.get('priceType', None)
        client_status = request.query_params.get('status', None)

        if inn:
            q = q.filter(INN=inn)
        if client_type:
            q = q.filter(client_type=client_type)
        if price_type:
            q = q.filter(price_type=price_type)
        if manager:
            q = q.filter(Q(authorized_managers=manager) | Q(manager=manager)).distinct()
        if client_status:
            client_status = True if (client_status == "true" or client_status == "True") else False
            q = q.filter(status=client_status)

        result = [c.to_dict() for c in q]
        return JsonResponse(result, safe=False, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        if request.user.userprofile.role == 'MPR':
            return Response("You can't do that", status=status.HTTP_403_FORBIDDEN)
        else:
            try:
                jsonschema.validate(instance=request.data, schema=clients_schema)
            except jsonschema.exceptions.ValidationError as e:
                print(e)
                return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
            for c in request.data:
                try:
                    client = Client.objects.get(INN=c['inn'])
                except Client.DoesNotExist:
                    client = Client.objects.create(name=c['name'], INN=c['inn'])
                client.update_from_dict(c)

            return Response('Client list have been putted', status=status.HTTP_200_OK)
    else:
        return Response('Method not allowed', status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def visits(request):
    if request.method == 'GET':
        # собираем в кучку параметры запроса
        # ВНИМАНИЕ! лютый говнокод
        # TODO: переписать по-человечески выборку из визитов
        manager = None
        author = None
        if request.user.userprofile.role == 'MPR':
            manager = User.objects.get(userprofile__manager_ID=request.user.userprofile.manager_ID)
        else:
            managerid = request.query_params.get('managerID', None)
            if managerid:
                try:
                    manager = User.objects.get(userprofile__manager_ID=managerid)
                except User.DoesNotExist:
                    return Response({}, status=status.HTTP_204_NO_CONTENT)
        authorID = request.query_params.get('author', None)
        if authorID:
            try:
                author = User.objects.get(userprofile__manager_ID=authorID)
            except User.DoesNotExist:
                return Response({}, status=status.HTTP_204_NO_CONTENT)

        processed = request.query_params.get('processed', None)
        invoice = request.query_params.get('invoice', None)
        visit_status = request.query_params.get('status', None)
        client_inn = request.query_params.get('clientINN', None)
        date = request.query_params.get('date', None)
        limit = request.query_params.get('limit', None)
        database = request.query_params.get('dataBase', None)
        if limit:
            try:
                limit = int(limit)
            except ValueError:
                return Response("Bad limit value", status=status.HTTP_400_BAD_REQUEST)
        # делаем последовательную фильтрацию
        # потому что https://docs.djangoproject.com/en/3.0/topics/db/queries/#querysets-are-lazy
        # и это ничего не стоит
        q = Visit.objects.all().order_by('date')
        if manager:
            q = q.filter(manager=manager)
        if author:
            q = q.filter(author=author)
        if processed:
            processed = True if (processed == "true" or processed == "True") else False
            if processed:
                q = q.exclude(processed=None)
            else:
                q = q.filter(processed=None)
        if invoice:
            invoice = True if (invoice == "true" or invoice == "True") else False
            if invoice:
                q = q.exclude(invoice=None)
            else:
                q = q.filter(invoice=None)
        if visit_status:
            q = q.filter(status=visit_status)
        if client_inn:
            q = q.filter(client_INN=client_inn)
        if date:
            q = q.filter(date__gte=date)
        if limit:
            q = q[:limit]
        if database:
            database = True if (database == "true" or database == "True") else False
            q = q.filter(database=database)
        result = [v.to_dict() for v in q]
        return JsonResponse(result, safe=False, status=status.HTTP_200_OK)
    return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def visit(request, vuuid):
    if request.method == 'GET':
        try:
            v = Visit.objects.get(UUID=vuuid)
        except Visit.DoesNotExist:
            return Response("Visit not found", status=status.HTTP_404_NOT_FOUND)
        if request.user.userprofile.role == 'MPR':
            if request.user.userprofile.manager_ID == v.manager.userprofile.manager_ID:
                return JsonResponse(v.to_dict(), safe=False, status=status.HTTP_200_OK)
            else:
                return Response("You don't have permissions to get visit", status=status.HTTP_403_FORBIDDEN)
        else:
            return JsonResponse(v.to_dict(), safe=False, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        try:
            v = Visit.objects.get(UUID=vuuid)
        except Visit.DoesNotExist:
            if request.user.userprofile.role == 'MPR':
                manager = request.user
            elif request.data['managerID']:
                try:
                    manager = User.objects.get(userprofile__manager_ID=request.data['managerID'])
                except User.DoesNotExist:
                    return Response("Can't create visit: bad manger ID", status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Can't create visit: missing manger ID", status=status.HTTP_400_BAD_REQUEST)
            try:
                v = Visit.objects.create(
                    date=timezone.now(),
                    UUID=vuuid,
                    manager=manager,
                    author=request.user,
                    client_INN=request.data['clientINN']
                )
            except KeyError:
                return Response("Can't create visit: missing client INN", status=status.HTTP_400_BAD_REQUEST)

        if (request.user.userprofile.role == 'MPR'
            and request.user.userprofile.manager_ID == v.manager.userprofile.manager_ID
            and v.status != 2) \
                or request.user.userprofile.role == 'OFFICE' \
                or request.user.userprofile.role == '1S':
            try:
                jsonschema.validate(instance=request.data, schema=visit_schema)
                v.update_from_dict(request.data)
            except jsonschema.exceptions.ValidationError as e:
                print(e.message)
                return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response("Can't update visit: there is no manager with such ID, please try with another",
                                status=status.HTTP_400_BAD_REQUEST)
            return JsonResponse(v.to_dict(), status=status.HTTP_200_OK)
        else:
            return Response("You don't have permissions to put visit", status=status.HTTP_403_FORBIDDEN)

    elif request.method == 'DELETE':
        try:
            v = Visit.objects.get(UUID=vuuid)
        except Visit.DoesNotExist:
            return Response("Visit not found", status=status.HTTP_404_NOT_FOUND)
        if request.user.userprofile.role == 'OFFICE':
            v.delete()
            return Response("Visit have been deleted", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("You don't have permissions to delete visit", status=status.HTTP_403_FORBIDDEN)
    return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def visitbyid(request, vid):
    try:
        v = Visit.objects.get(pk=vid)
    except Visit.DoesNotExist:
        return Response("Visit not found", status=status.HTTP_400_BAD_REQUEST)
    return HttpResponseRedirect('/api/visits/' + v.UUID)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resetvisits(request):
    if request.user.userprofile.role == 'MPR':
        # Visit.objects.filter(
        #     manager=User.objects.get(userprofile__manager_ID=request.user.userprofile.manager_ID)).delete()
        date = timezone.now().date()
        q = Client.objects.filter(manager=request.user)
        q = q.exclude(client_type='Магазин')
        clientsinn = q.values_list('INN', flat=True)
        if not clientsinn:
            return Response("There are no clients for this manager found", status=status.HTTP_200_OK)

        for _ in range(random.randint(4, 8)):  # запланированные на сегодня визиты
            clientinn = random.choice(clientsinn)
            Visit.objects.create(
                UUID=uuid.uuid4(),
                author=User.objects.get(pk=1),
                manager=request.user,
                client_INN=clientinn,
                status=0,
                date=date,
                payment_plan=random.randint(2000, 10000))

        for _ in range(random.randint(10, 16)):  # запланированные на неделю визиты
            for days in range(1, 5):
                clientinn = random.choice(clientsinn)
                Visit.objects.create(
                    UUID=uuid.uuid4(),
                    author=User.objects.get(pk=1),
                    manager=request.user,
                    client_INN=clientinn,
                    status=0,
                    date=date + timezone.timedelta(days=days),
                    payment_plan=random.randint(2000, 10000))

        pr = Client.objects.all().filter(active=True)

        for clientinn in clientsinn:  # делаем по три оконченных визита для каждого клиента
            for delta in range(3):
                payment = random.randint(2000, 10000)
                v = Visit.objects.create(
                    UUID=uuid.uuid4(),
                    manager=request.user,
                    client_INN=clientinn,
                    status=2,
                    date=date - timezone.timedelta(days=(14 * (delta + 1) + random.randint(0, 5))),
                    delivery_date=date + timezone.timedelta(days=random.randint(6, 14)),
                    payment=payment,
                    payment_plan=payment - random.randint(0, 2000),
                    author=User.objects.get(pk=1)
                )

                for product in pr:
                    order = random.randint(3, 15)
                    Order.objects.create(
                        visit=v,
                        product_item=product['item'],
                        order=order,
                        delivered=0,
                        recommend=random.choice([order, order - 1, order - 2]),
                        balance=random.randint(0, 10),
                        sales=random.randint(0, 15)
                    )

        return Response("New visits have been added for" + str(clientsinn), status=status.HTTP_200_OK)

    else:
        Photo.objects.all().delete()
        Visit.objects.all().delete()
        return Response("All visits and photos have been deleted", status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resetonesdata(request):
    Client.objects.all().exclude(client_type='Магазин').delete()
    Product.objects.all().delete()
    Price.objects.all().delete()
    return Response("All clients, products, prices have been deleted", status=status.HTTP_200_OK)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def checklistsquestions(request, quuid=None):
    if request.method == 'GET':
        if quuid:
            question = get_object_or_404(ChecklistQuestion, UUID=quuid)
            serializer = ChecklistQuestionSerializer(question)
            return JsonResponse(serializer.data, safe=False)
        else:
            questions = ChecklistQuestion.objects.all()
            active = request.query_params.get('active', None)
            if active:
                active = True if (active == "true" or active == "True") else False
                questions = questions.filter(active=active)
            serializer = ChecklistQuestionSerializer(questions, many=True)
            return JsonResponse(serializer.data, safe=False)
    if request.method == 'PUT':
        data = JSONParser().parse(request)
        try:
            instance = ChecklistQuestion.objects.get(UUID=data['UUID'])
        except (KeyError, ChecklistQuestion.DoesNotExist):
            instance = None
        serializer = ChecklistQuestionSerializer(instance=instance, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        question = get_object_or_404(ChecklistQuestion, UUID=quuid)
        question.delete()
        return Response('Question has been deleted', status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def checklistanswers(request):
    if request.method == 'GET':
        q = ChecklistAnswer.objects.all()

        client_type = request.query_params.get('clientType', None)
        visitUUID = request.query_params.get('visit', None)
        client_INN = request.query_params.get('client', None)
        questionUUID = request.query_params.get('question', None)

        if visitUUID:
            try:
                v = Visit.objects.get(UUID=visitUUID)
            except Visit.DoesNotExist:
                return Response('Bad visit UUID', status=status.HTTP_400_BAD_REQUEST)
            q = q.filter(visit=v)

        # if client_type:
        #     q = q.filter(visit__client_type=client_type)

        if client_INN:
            q = q.filter(visit__client_INN=client_INN)

        if questionUUID:
            try:
                question = ChecklistQuestion(UUID=questionUUID)
            except ChecklistQuestion.DoesNotExist:
                return Response('Bad checklist question UUID', status=status.HTTP_400_BAD_REQUEST)
            q = q.filter(question=question)

        result = [a.to_dict() for a in q]
        return JsonResponse(result, safe=False, status=status.HTTP_200_OK)

    if request.method == 'POST':
        time.sleep(1)
        try:
            jsonschema.validate(instance=request.data, schema=checklistanswers_schema)
        except jsonschema.exceptions.ValidationError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        for answer in request.data:
            try:
                v = Visit.objects.get(UUID=answer['visitUUID'])
            except (KeyError, Visit.DoesNotExist):
                return Response('Something wrong with visit UUID', status=status.HTTP_400_BAD_REQUEST)
            try:
                q = ChecklistQuestion.objects.get(UUID=answer['questionUUID'])
            except (KeyError, ChecklistQuestion.DoesNotExist):
                return Response('Something wrong with question UUID', status=status.HTTP_400_BAD_REQUEST)
            try:
                ChecklistAnswer.objects.create(
                    # UUID=answer['UUID'],
                    question=q,
                    visit=v,
                    answer1=str(answer.get('answer1', '')),
                    answer2=answer.get('answer2', '')
                )
            except Exception:
                return Response('Something wrong with answer creation', status=status.HTTP_400_BAD_REQUEST)
        return Response('OK', status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def photos(request, vuuid):
    if request.method == 'POST':
        try:
            cvisit = Visit.objects.get(UUID=vuuid)
        except Visit.DoesNotExist:
            return Response('Visit not found', status=status.HTTP_400_BAD_REQUEST)
        try:
            Photo.objects.create(visit=cvisit, image=request.data['image'])
        except KeyError:
            return Response('Bad image content', status=status.HTTP_400_BAD_REQUEST)
        return Response('Photo have been saved', status=status.HTTP_200_OK)
    if request.method == 'GET':
        return Response('Not implemented yet', status=status.HTTP_501_NOT_IMPLEMENTED)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def tasks(request, tuuid):
    if request.method == 'GET':
        return Response('', status=status.HTTP_501_NOT_IMPLEMENTED)
    if request.method == 'PUT':
        return Response('', status=status.HTTP_501_NOT_IMPLEMENTED)
