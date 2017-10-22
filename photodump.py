import vk_api
import os
from urllib.request import urlretrieve
from time import sleep

"""
by Konstantin Peskov
https://github.com/likanovkos

This script downloads all photos from vk.com dialog, or group dialog
Steps:
1) Create folder
2) Parse photos links
3) Downloads pics  
 
"""


class PhotoDump:
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.vk_session = vk_api.VkApi(login, password)
        self.timeout = 3
        self.api = self.vk_session.get_api()

    def authorization(self):
        try:
            self.vk_session.auth()
        except vk_api.AuthError as error_msg:
            print(error_msg)
            return

    def make_request(self, peer_id, media_type, count, start_from):

        if start_from:
            return self.api.messages.getHistoryAttachments(
                peer_id=peer_id,
                media_type=media_type,
                count=count,
                start_from=start_from
            )
        else:
            return self.api.messages.getHistoryAttachments(
                peer_id=peer_id,
                media_type=media_type,
                count=count,
            )

    def load_photo_links(self, dialog_id):

        links = []
        # get all of pics urls
        raw = self.make_request(dialog_id, 'photo', 200, start_from=None)
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
            raw = self.make_request(dialog_id, 'photo', 200, start_from=next_page)
            next_page = raw.get('next_from')

        return links

    def downloads_pictures(self, from_dialog):
        links = self.load_photo_links(from_dialog)
        if links:
            image_number = 0
            print('Download Progress: \n')
            with open('downloaded_images', 'w') as f:
                for link in links:
                    try:
                        urlretrieve(link, "{}.jpg".format(str(image_number)))
                        image_number += 1
                    except Exception as e:
                        print('Error!: {}'.format(e))

                    f.write(link + '\n')
                    print('Pic count: {0}, now is downloaded {1}\n'.format(
                        len(links), links.index(link)
                    ))
                return f.close()

    @staticmethod
    def create_directory(folder_name):

        try:
            os.mkdir("dump_{}".format(folder_name))
        except OSError as e:
            print("Проблемы с созданием папки 'dump_{}'\n".format(folder_name))
            print("Ошибка {}".format(e))

        if os.path.exists("dump_{}".format(folder_name)):
            os.chdir("dump_{}".format(folder_name))
        else:
            print("Не удалось создать папку\n")
            exit()


def run():
    # setting of parse
    login, password = 'mylogin', 'mypassword'
    # you can get this argument from url of your dialog, example https://vk.com/im?sel="HEREYOUID"
    dialog_id = 'myid'

    main = PhotoDump(login, password)
    main.create_directory('myfolder')
    main.authorization()
    main.downloads_pictures(from_dialog=dialog_id)


if __name__ is '__main__':
    run()
