from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render  #daphne add 20200516

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, PostbackEvent
from module import func
from urllib.parse import parse_qsl #daphne add 20200517
from linebot import  LineBotApi 
from linebot import  WebhookHandler

from linebot.models import MessageEvent, TextMessage, TextSendMessage #daphne add 20200517
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
#parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
parser = WebhookHandler(settings.LINE_CHANNEL_SECRET)


line_bot_api.push_message('Ub8e3cf75739079f25a50f82b2cbd4c63', TextSendMessage(text='你可以開始了'))
line_bot_api.push_message('Uaa63a3f5feff2725536db7d81f09c929', TextSendMessage(text='你可以開始了'))
from hotelapi.models import users

@csrf_exempt
def index(request):  #daphne add 20200516
     return render(request,"hotel_form.html",locals())	
 
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                user_id = event.source.user_id
                if not (users.objects.filter(uid=user_id).exists()):
                    unit = users.objects.create(uid=user_id)
                    unit.save()
                mtext = event.message.text
                if mtext == '@使用說明':
                    func.sendUse(event)

                elif mtext == '@房間預約':
                    func.sendBooking(event, user_id)

                elif mtext == '@取消訂房':
                    func.sendCancel(event, user_id)

                elif mtext == '@關於我們':
                    func.sendAbout(event)

                elif mtext == '@位置資訊':
                    func.sendPosition(event)

                elif mtext == '@聯絡我們':
                    func.sendContact(event)

                elif mtext[:3] == '###' and len(mtext) > 3:  #處理LIFF傳回的FORM資料
                     func.manageForm(event, mtext, user_id)

                elif mtext[:6] == '123456' and len(mtext) > 6:  #推播給所有顧客
                     func.pushMessage(event, mtext)

            if isinstance(event, PostbackEvent):  #PostbackTemplateAction觸發此事件
                backdata = dict(parse_qsl(event.postback.data))  #取得Postback資料
                if backdata.get('action') == 'yes':
                    func.sendYes(event, event.source.user_id)

        return HttpResponse()

    else:
        return HttpResponseBadRequest()
    
#def hotelform(request):
  #return render(request,"index_form.html",locals())

