import requests, json, re, config

class Updater(object):
    def update(self):
        api_method = 'getUpdates'
        response = requests.get('https://api.telegram.org/bot' + config.token + '/' + api_method)
        updates = json.loads(response.text)
        for command in updates['result'][1:]:
            if ('text' in command['message']) == False:
                continue
            id = command['message']['chat']['id']
            text = command['message']['text']
            self.__exec_command(id, text)

        requests.get('https://api.telegram.org/bot' + config.token + '/' + api_method + '?offset=-1') #clear update list    

    def __exec_command(self, id, text):
        def create_user(db):
            return db.users.insert_one({"id": id, "notes": []})
        db = config.db # get db from config file
        user = db.users.find_one({"id": id})
        if user == None:
            user = create_user(db)
        if text[0:5] == "/show":
            message_text = ''
            if user['notes'] == []:
                message_text = 'У вас нет напоминаний.'
            else:
                i = 0
                for line in user['notes']:
                    i += 1
                    message_text += str(i) + '. ' + line + '\n'       
            self.__send_message(id, message_text)    
        elif text == '/del_all':
            db.users.update({"id": id}, {"id": id, "notes": []})      
        elif text[0:4] == '/del':
            match = re.search('\d', text)
            if match:
                index = int(text[match.start():match.end()+1])
                if 0 < index <= len(user['notes']):
                    db.users.update({"id": id}, {"$pop": {"notes": -index}}) #unary minus, because mongoDB
                else:
                    self.__send_message(id, 'Вы ввели неправильные параметры.')    
        elif text == '/help':
            self.__send_message(id, 'Данный бот позволяет вам записывать небольшие заметки(до 255 символов) ' +
                'чтобы добавить заметку, просто отправте её боту, для вывода списка заметок выберите команду /show ' +
                'для удаления заметки введите \'/del <номер заметки>(без кавычек)\', номер заметки можно увидеть ' + 
                'при выводе списка заметок')    
        elif text == '/start':
            pass   #because we wan't see note '/start' in database
        else:
            db.users.update({"id": id}, {"$push": {"notes": text[0:255]}})

    def __send_message(self, id, text):
        api_method = 'sendMessage'
        requests.get('https://api.telegram.org/bot' + config.token + 
            '/' + api_method + '?chat_id=' + str(id) + '&text=' + text)