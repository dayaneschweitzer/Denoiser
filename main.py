import os
import time
import pyinotify
import shutil
import pydicom
from pydicom.errors import InvalidDicomError
import pet.main as PET

ROOT_FOLDER = os.environ.get('ROOT_WM_FOLDER')
PET_TERMNOLOGY = os.environ.get('PET_DESCRIPTION')
TMP_FOLDER = './tmp'

# Classe para lidar com os eventos de novos arquivos do PACS
class DcmEventHandler(pyinotify.ProcessEvent):
    def denoise_file(self, key):
        try:
            ds = pydicom.read_file(key, force=False)
            series_description = ds.SeriesDescription
        except InvalidDicomError:
            print(f'Pulando arquivo {key} pois não é um DCM válido')
            return

        print(f'Series description: {series_description}')

        if ('Denoising' in series_description 
            or PET_TERMNOLOGY not in series_description):
            print('Os parametros do conjunto não devem ser processados...')
            self.remove_watch(os.path.dirname(key))
        else:
            time.sleep(5) # Delay para aguardar o conjunto ser enviado por completo
            source_folder = os.path.dirname(key)
            pet_slices_folder = source_folder.split('/')[-1]
            pet_folder = os.path.join(TMP_FOLDER, pet_slices_folder)
            if (os.path.exists(pet_folder)):
                shutil.rmtree(pet_folder)
            shutil.copytree(source_folder, pet_folder)
            try:
                print(f'PET - Processando a pasta {pet_folder}')
                PET.process_folder(pet_folder)
            except Exception as ex:
                print(f'A imagem não foi processada. {ex}')
                print(f'Ignorando processamento atual da pasta {pet_folder}')
            finally:
                self.remove_watch(source_folder)
                shutil.rmtree(pet_folder)

    def process_IN_CLOSE_WRITE(self, event):
        if not event.dir:
            print(f"Arquivo criado: {event.pathname}")
            self.denoise_file(event.pathname)

    def process_IN_MOVED_TO(self, event):
        if not event.dir:
            print(f"Arquivo movido: {event.pathname}")
            self.denoise_file(event.pathname)

    def process_IN_CREATE(self, event):
        if event.dir:
            self.add_watch(event.pathname)

    def add_watch(self, directory):
        # Adiciona um novo diretório ao WatchManager
        mask = pyinotify.IN_CREATE | pyinotify.IN_MOVED_TO | pyinotify.IN_CLOSE_WRITE | pyinotify.IN_ISDIR
        wm.add_watch(directory, mask, rec=False)

    def remove_watch(self, directory):
        # Remove o diretório do WatchManager
        watch = wm.get_wd(directory)
        if watch:
            wm.rm_watch(watch)
            print(f"Monitoramento removido: {directory}")

if not (os.path.exists(TMP_FOLDER)):
    os.mkdir(TMP_FOLDER)

wm = pyinotify.WatchManager()
mask = pyinotify.IN_CREATE | pyinotify.IN_MOVED_TO | pyinotify.IN_CLOSE_WRITE | pyinotify.IN_ISDIR
handler = DcmEventHandler()
wm.add_watch(ROOT_FOLDER, mask, rec=True)
notifier = pyinotify.Notifier(wm, handler)

print(f'Iniciando monitoramento recursivo da pasta {ROOT_FOLDER}')
notifier.loop()
