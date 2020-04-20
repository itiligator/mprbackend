from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone

from .models import Price, PriceType, Product, Client, OrderItem, Order
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def productsjson(request):
    products_dicts = [{'item': product.item, 'name': product.name, 'description': product.description,
                       'price': {price.price_type.name(): price.value for price in
                                 Price.objects.filter(product=product)}}
                      for product in Product.objects.all()]
    return JsonResponse(products_dicts, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def clientsjson(request):
    clients_dicts = [{'pk': client.pk,
                      'name': client.name,
                      'inn': client.inn,
                      'manager': client.manager.first_name + ' ' + client.manager.last_name,
                      'client_type': client.client_type.name(),
                      'price_type': client.price_type.name()}
                     for client in Client.objects.filter(is_active=True)]

    return JsonResponse(clients_dicts, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def orderlist(request):
    orderlist_dicts = [
        {'order_pk': order.pk,
         'client_pk': order.client.pk,
         'client_name': order.client.name,
         'creation_date': order.creation_date,
         'delivery_date': order.delivery_date,
         'processed': order.processed}
        for order in Order.objects.filter(manager=request.user).order_by('-creation_date')
    ]

    return JsonResponse(orderlist_dicts, safe=False)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getorder(request, pk):
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return HttpResponseNotFound('<h1>Order not found</h1>')
    order_dict = {
        'order_pk': order.pk,
        'client_pk': order.client.pk,
        'client_name': order.client.name,
        'creation_date': order.creation_date,
        'delivery_date': order.delivery_date,
        'processed': order.processed,
        'orderitems': [{
            'item': orderitem.product.item,
            'name': orderitem.product.name,
            'quantity': orderitem.quantity
        } for orderitem in OrderItem.objects.filter(order=order)]
    }
    return JsonResponse(order_dict, safe=False)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def putorder(request):
    try:
        pk = int(request.data["order_pk"])  # PK заказа
    except ValueError:
        return Response({}, status=status.HTTP_400_BAD_REQUEST)  # если PK заказа невалидный

    if pk != -1:  # если передан PK заказа отличный от -1, т.е. заказ уже существует

        try:  # попытаться отыскать существующий заказ
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        if request.user != order.manager:  # если заказ создан другим пользователем, то вернуть ответ 401
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)

        if order.processed:  # если заказ уже ушел в обработку
            return Response({}, status=status.HTTP_304_NOT_MODIFIED)

    else:  # если PK заказа -1, т.е. должен быть создан новый заказ
        try:
            client_pk = int(request.data["client_pk"])
            client = Client.objects.get(pk=client_pk)
            order = Order.objects.create(
                client=client,
                manager=request.user,
                creation_date=timezone.now(),
                delivery_date=timezone.now(),
            )  # TODO: сделать таки установку даты доставки заказа

        except (ValueError, Client.DoesNotExist):
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

    orderitems = OrderItem.objects.filter(order=order)  # QuerySet существующих элементов заказа
    req_orderitems = request.data['orderitems']  # словарь принятых элементов заказа

    for item in req_orderitems:  # обход словаря принятых элементов заказа

        try:  # попытаться отыскать в базе элемент заказа соответствующий принятому элементу
            orderitem = orderitems.get(product__pk=req_orderitems[item]['item'])
        except (OrderItem.DoesNotExist, KeyError):  # если таковой не найден
            try:  # попытаться отыскать в базе соответствующий элементу заказа продукт и создать элемент заказа
                req_product = Product.objects.get(pk=req_orderitems[item]['item'])
                orderitem = OrderItem.objects.create(order=order, product=req_product, quantity=0)
            except (Product.DoesNotExist, KeyError):  # если продукт не найден, то вернуть 400
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

        # TODO: сделать таки установку даты доставки заказа

        orderitem.quantity = req_orderitems[item]['quantity']  # присвоить новое количество продукта в элементе
        orderitem.save()  # заказа и сохранить этот элемент

    if pk != 1:
        return Response({}, status=status.HTTP_200_OK)
    else:
        return Response({}, status=status.HTTP_201_CREATED)
