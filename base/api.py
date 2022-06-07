import os
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from base.models import Account, Ledger


@csrf_exempt
def transfer_request(request):
    if request.method == "POST":
        body = request.body.decode("utf-8")
        data = json.loads(body)

        if 'Token' not in request.headers:
            response = {
                "message": "Provide bank token",
                "status": False
            }
            return JsonResponse(response, status=404)

        if request.headers['Token'] != os.environ['BANK_CONTROLLER_TOKEN']:
            response = {
                "message": "Not correct token",
                "status": False
            }
            return JsonResponse(response, status=405)

        transaction_id = data['id']
        bank_id = data['senderBankId']
        sender_bank_account = data['senderAccountNumber']
        account_number = data['receiverAccountNumber']
        amount = data['amount']
        message = data['message']

        try:
            credit_account = Account.objects.get(account_no=account_number)
        except:
            response = {
                "message": "Could not find account with that number",
                "status": False
            }
            return JsonResponse(response, status=400)

        try:
            Ledger.receive_external_transfer(
                credit_account=credit_account,
                amount=amount,
                message=f"{bank_id}#{sender_bank_account}: {message}",
                transaction_id=transaction_id
            )
        except:
            response = {
                "message": "Could not receive the transfer",
                "status": False
            }
            return JsonResponse(response, status=400)

        response = {
            "message": "Found account - transfer has been made",
            "status": True
        }
        return JsonResponse(response, status=200)
