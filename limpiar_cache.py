import shutil
import os
import moviepy.config as mpy_config

# Forzar la configuración correcta
mpy_config.IMAGEMAGICK_BINARY = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"

# Eliminar el archivo de caché si existe
cache_file = os.path.join(os.path.dirname(mpy_config.__file__), 'config.cache')
if os.path.exists(cache_file):
    os.remove(cache_file)
    print("Caché de MoviePy eliminada correctamente.")
else:
    print("No se encontró archivo de caché, continuando...")

print("Ruta de ImageMagick configurada:", mpy_config.IMAGEMAGICK_BINARY)