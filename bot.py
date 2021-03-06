import socket
import socks
import requests
import time

socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, '94.177.252.200', port=8080)
socket.socket = socks.socksocket

token = '738099463:AAHjUgagLdzp5R-6eZapoC8GhNA-oh1DM3U' #Telegram @g18_search_bot
key1 = 'AIzaSyD44YDNQGAdGbqOjZ1CrnKYEUMQ5Wct6ns' #Google
key2 = 'AIzaSyASVG3FkdlnbSoEgASpeRemHeiBYdbnSv0'
custom_search1='013695167246701378175:arrmuifq5-o'
custom_search2='013695167246701378175:awsr_yvt64y'


class Google_Search:
    def __init__(self,key,custom_search):
        self.key=key
        self.custom_search=custom_search
        self.search_api_url='https://www.googleapis.com/customsearch/v1?'

    def get_search_results(self, search):
        params = {'key': self.key, 'cx': self.custom_search, 'fields':'items(title,link)', 'q': search}
        response = requests.get(self.search_api_url, params)
        return response.json()

    def generate_result_message(self, search):
        r = self.get_search_results(search)

        i = 0
        message = ''
        if 'items' in r and len(r['items']) > 1:
          #print(len(r['items']))
          while i < 5:
            message += '\n' + str(r['items'][i]['title']) + '\n' + str(r['items'][i]['link']) + '\n'
            i += 1
        else:
          message +='Ошибка: ответ от Google пуст. Либо на запрос не найдено ответов, либо израсходован лимит запросов.'
        return message

class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = 'https://api.telegram.org/bot{}/'.format(token)

    def get_updates(self, offset, timeout=3000):
        method = str('getUpdates')
        params = {'timeout': timeout, 'offset': offset}
        url = str(self.api_url) + str(method)
        resp = requests.get(url, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self,data):
        if len(data) > 0:
            last_update = data[0]
        else:
            last_update = None

        return last_update

search_bot=BotHandler(token)
google_search=Google_Search(key2,custom_search2)

def main():
    new_offset = None
    last_update_id = None

    while True:
          upd = search_bot.get_updates(new_offset) #получаю обновления: если new_offset=None, то все (мнимум одно)
          if last_update_id != search_bot.get_last_update(upd)['update_id']: #если последнее отвеченное и есть это одно, то ничего не делаем
              last_update = search_bot.get_last_update(upd) #получаю из пачки обновдений только первое, которое пришло
              last_update_id = last_update['update_id']
              last_chat_id = last_update['message']['chat']['id']
              last_chat_name = last_update['message']['chat']['first_name']
              search_bot.get_updates(last_update) #помечаю отступом что прочитал сообщение

              if 'text' in str(last_update):
                  last_chat_text = last_update['message']['text']
                  result_message=google_search.generate_result_message(last_chat_text)
              else:
                  result_message='Ошибка: нет текста'

              search_bot.send_message(last_chat_id, last_chat_name + ', результаты поиска по Google: ' + result_message)

              if len(upd)>1:
                  new_offset = upd[1]['update_id']

          else:
              if len(upd)>1:
                  new_offset = upd[1]['update_id']
              else:
                  new_offset=None




if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
