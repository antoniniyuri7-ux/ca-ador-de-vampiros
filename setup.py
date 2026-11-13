# Instale com: pip install pygame pyttsx3 cx_Freeze
import cx_Freeze

executaveis = [
    cx_Freeze.Executable(
        script="main.py",
        icon="assets/icone.ico",
        target_name="CacadorDeVampiros.exe"
    )
]

cx_Freeze.setup(
    name="Cacador de Vampiros",
    options={
        "build_exe": {
            "packages": ["pygame", "pyttsx3", "Recursos"],
            "include_files": ["assets"]
        }
    },
    executables=executaveis
)

# Para gerar a pasta do jogo:
# python setup.py build
