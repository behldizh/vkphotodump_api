import vk_api
import os
from urllib.request import urlretrieve
from time import sleep
"""
created by Likanov
"""
#######################################
#            oh, hello      ____      #
#  ________________________/ O  \___/ #
# <%%%%%%%%%%%%%%%%%%%%%%%%_____/   \ #
#######################################

PATH = os.getcwd()


class PhotoDump:
    def __init__(self, login=None, password=None, dialog=None):
        # init values
        self.login = login
        self.password = password
        self.dialog = dialog
        self.api = None

        # Options
        self.timeout = 1

    def auth_process(self):
        try:
            session = vk_api.VkApi(self.login, self.password)
            session.auth()
            self.api = session.get_api()
        except vk_api.AuthError as error_msg:
            raise error_msg

    def make_request(self, pagination=None):
        """
        Этот метод делает завпрос и возвращает json с информацией о вложении(в данном случае, фотки)
        TODO:
        Добавить обработчик исключений, пока не ясно, какие исключения наследуются от базового класса

        :param pagination: пагинация
        :return: json
        """

        kwargs = {
            'peer_id': self.dialog,
            'media_type': 'photo',
            'count': 200,
        }
        if self.api:
            if pagination:
                kwargs.update(start_from=pagination)
            # между запросами делам пазу
            sleep(self.timeout)
            return self.api.messages.getHistoryAttachments(**kwargs)
        else:
            raise vk_api.AuthError('Сессия устарела, либо не существует')

    def load_photo_links(self):

        links = []
        # забираем все урлы картинок
        raw = self.make_request()
        next_page = raw.get('next_from')

        while next_page:
            items = raw['items']
            for item in items:
                photo = item['attachment']['photo']
                # Выбираем размер картинки
                if photo.get('photo_1280'):
                    links.append(photo['photo_1280'])
                    continue
                elif photo.get('photo_2560'):
                    links.append(photo['photo_2560'])
                    continue

            sleep(self.timeout)
            raw = self.make_request(pagination=next_page)
            next_page = raw.get('next_from')

        return links

    def downloads_pictures(self):
        self.create_directory()

        links = self.load_photo_links()
        if links:
            image_number = 0
            print('Download Progress: \n')
            with open('downloaded_images', 'w') as f:
                for link in links:
                    try:
                        urlretrieve(link, "{}.jpg".format(str(image_number)))
                        sleep(1)
                        image_number += 1
                    except Exception as e:
                        print('Error!: {}'.format(e))

                    f.write(link + '\n')
                    print('Pic count: {0}, now is downloaded {1}\n'.format(
                        len(links), links.index(link)
                    ))
                return f.close()

    def create_directory(self):
        # Разбиваем на папки с логинами, в которых храняться под папки с идентификатором диалога
        # Всегда начинаем с основной папки
        os.chdir(PATH)
        try:
            # Если папка уже существует, переходим по данному пути и создаем там подпапку с идентификатором диалога
            if os.path.exists(self.login):
                os.chdir(self.login)
                if os.path.exists(self.dialog):
                    os.chdir(self.dialog)
                else:
                    os.mkdir(self.dialog)
                    os.chdir(self.dialog)
            else:
                # иначе создаем папку для нового пользователя
                os.mkdir(self.login)
                os.chdir(self.login)
                os.mkdir(self.dialog)
                os.chdir(self.dialog)

        except OSError as e:
            # немного крос платформенности
            if os.name == 'posix':
                current_path = os.getcwd().split('/')[-1]
            elif os.name == 'nt':
                current_path = os.getcwd().split('\\')[-1]
            else:
                raise OSError('Не делал под другие оси')

            print("Oops! Creating folder at {} failed \n".format(current_path))
            print("Error {}".format(e))

    def main(self):
        self.auth_process()
        self.downloads_pictures()


if __name__ is '__main__':
    kwargs = {
        'login': '',
        'password': '',
        'dialog': ''
    }
    download = PhotoDump(**kwargs)
    download.main()
