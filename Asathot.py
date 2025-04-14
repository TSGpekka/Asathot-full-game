import time
import os
import random

# Estado global
installed_os = None
hostname = "localhost"
wifi_networks = ["HackNet_24G", "CoffeeShop_FreeWiFi", "Corporativo_5G"]
wifi_hacked = []
darknet_sites = {
    "bitcoinhub.onion": "Visualizar saldo de Bitcoin",
    "darkchat.onion": "Chat global da Darknet, encontre perfis e receba tarefas",
    "champions.onion": "Site para campeonatos de Bitcoin",
    "shopnet.onion": "Loja de malware, ransomware, spyware e mais",
}
darknet_chat = {"user1": "Cuidado, polícia está caçando você."}
vpn_active = False
bitcoin_balance = 0
system_files = {"root": [], "Workplace": ["List.txt"]}
current_user = "hacker"
current_task = None
current_directory = "root"

# Função para criar o ransomware
def ransomware_attack(target_folder):
    print(f"[+] Ransomware iniciado em '{target_folder}'...")
    time.sleep(2)
    print("[+] Criptografando arquivos...")
    time.sleep(3)
    encrypted_files = []
    for i in range(10):  # Simulando criptografia de 10 arquivos
        encrypted_files.append(f"file_{i}.txt.enc")
    print("[+] Arquivos criptografados com sucesso!\n")
    print("[!] PARA DESCRIPTOGRAFAR OS ARQUIVOS, PAGUE 500 BTC PARA A CONTA: 1HCKrR4NsomWar3Xyz")

# Funções de instalação
def show_installer():
    global installed_os, hostname
    print("="*50)
    print("            INSTALADOR DO ASATHOT")
    print("="*50)
    print("Escolha um sistema para instalar:")
    print("1. ParanoiaOS - Máxima privacidade")
    print("2. HomeOS - Uso pessoal")
    print("3. GeoforceOS - Focado em hacking")
    print("4. Instalar todos (triple boot)")
    choice = input("Opção: ")
    if choice == "4":
        installed_os = ["ParanoiaOS", "HomeOS", "GeoforceOS"]
    elif choice == "1":
        installed_os = ["ParanoiaOS"]
    elif choice == "2":
        installed_os = ["HomeOS"]
    elif choice == "3":
        installed_os = ["GeoforceOS"]
    else:
        print("Opção inválida. Instalando GeoforceOS por padrão.")
        installed_os = ["GeoforceOS"]

    hostname = input("Nome do host: ") or "asathot-machine"
    print("\nInstalando sistemas...")
    for osys in installed_os:
        print(f"Instalando {osys}...")
        time.sleep(1)
    print("\nInstalação concluída!")
    input("Pressione ENTER para iniciar o terminal...")
    start_terminal()

# Terminal principal com todos os comandos
def start_terminal():
    global vpn_active, bitcoin_balance, system_files, current_task, current_directory
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"\n{hostname}@asathot:~$")
    while True:
        command = input(f"{hostname}@asathot:~$ ")
        if command == "help":
            print("\nComandos disponíveis:")
            print("scanwifi                 - Escaneia redes Wi-Fi")
            print("hackwifi <id>           - Hackeia rede Wi-Fi fictícia")
            print("netdiscover             - Descobre IPs na rede")
            print("portscan <ip>           - Escaneia portas de um IP")
            print("bruteforce <ip>         - Força bruta em um IP")
            print("deface <url>            - Simula um deface de site")
            print("connectvpn              - Conecta à uma VPN da Darknet")
            print("darknet <site>          - Acessa um site da Darknet")
            print("chat <usuario>          - Inicia um chat na Darknet")
            print("createfile              - Cria um arquivo TXT fictício")
            print("deletefile              - Deleta um arquivo fictício")
            print("createfolder            - Cria uma pasta fictícia")
            print("rmdir                   - Remove uma pasta")
            print("ls                      - Lista arquivos e pastas no diretório atual")
            print("cd <dir>                - Muda para o diretório especificado")
            print("cat                     - Lê o conteúdo de um arquivo")
            print("nano                    - Edita um arquivo com nano")
            print("clear                   - Limpa a tela do terminal")
            print("work                    - Faz um trabalho freelancer para ganhar bitcoin")
            print("buy <item>              - Compra um item da Darknet com bitcoin")
            print("ransomware <pasta>      - Simula um ataque ransomware")
            print("exit                    - Encerra o sistema\n")

        elif command == "scanwifi":
            print("\nRedes encontradas:")
            for i, net in enumerate(wifi_networks):
                status = "[HACKED]" if net in wifi_hacked else "[PROTEGIDA]"
                print(f"{i} - {net} {status}")
            print()

        elif command.startswith("hackwifi"):
            try:
                index = int(command.split(" ")[1])
                if wifi_networks[index] in wifi_hacked:
                    print("\n[!] Essa rede já foi hackeada.\n")
                else:
                    print("\n[+] Iniciando ataque à rede...")
                    time.sleep(2)
                    print("[+] Quebrando senha WPA2...")
                    time.sleep(2)
                    print("[+] Senha encontrada: cafe1234")
                    wifi_hacked.append(wifi_networks[index])
                    print("[+] Rede hackeada com sucesso!\n")
            except:
                print("\n[!] Uso: hackwifi <id da rede>\n")

        elif command == "connectvpn":
            print("\n[+] Conectando à VPN da Darknet...")
            time.sleep(2)
            vpn_active = True
            print("[+] VPN conectada com sucesso. Agora você está seguro!\n")

        elif command.startswith("darknet"):
            try:
                site = command.split(" ")[1]
                if site in darknet_sites:
                    print(f"\n[+] Acessando site {site}...")
                    time.sleep(2)
                    print(f"[+] {darknet_sites[site]}")
                    if site == "bitcoinhub.onion":
                        print(f"\n[+] Seu saldo de Bitcoin: {bitcoin_balance} BTC")
                    elif site == "darkchat.onion":
                        print("[+] Você pode conversar com outros membros ou pegar tarefas.")
                    elif site == "champions.onion":
                        print("[+] Inscreva-se para campeonatos e lute por Bitcoin.")
                    elif site == "shopnet.onion":
                        print("[+] Na loja, você pode comprar malwares e outros itens.")
                else:
                    print("\n[!] Site não encontrado na Darknet.\n")
            except:
                print("\n[!] Uso: darknet <site>. Exemplo: darknet hackersden.onion\n")

        elif command.startswith("chat"):
            user = command.split(" ")[1]
            if user in darknet_chat:
                print(f"\n[+] Iniciando chat com {user}...")
                time.sleep(2)
                print(f"{user}: {darknet_chat[user]}")
                print()
            else:
                print(f"\n[!] Usuário {user} não encontrado.\n")

        elif command == "work":
            task = random.choice(["bruteforce", "deface", "scanwifi", "hackwifi"])
            bitcoin_reward = random.randint(50, 200)
            print(f"\n[+] Você foi contratado para realizar um trabalho de {task}.")
            time.sleep(2)
            print(f"[+] Trabalho completado com sucesso! Você ganhou {bitcoin_reward} BTC.\n")
            bitcoin_balance += bitcoin_reward

        elif command.startswith("buy"):
            item = command.split(" ")[1]
            if bitcoin_balance >= 100:
                print(f"\n[+] Comprando {item} com {bitcoin_balance} BTC...")
                time.sleep(2)
                print(f"[+] {item} comprado com sucesso!")
                bitcoin_balance -= 100
            else:
                print("\n[!] Você não tem BTC suficiente para comprar isso.\n")

        elif command == "createfile":
            filename = input("Nome do arquivo: ")
            system_files["Workplace"].append(filename + ".txt")
            print(f"\n[+] Arquivo {filename}.txt criado com sucesso!\n")

        elif command == "deletefile":
            filename = input("Nome do arquivo: ")
            if filename + ".txt" in system_files["Workplace"]:
                system_files["Workplace"].remove(filename + ".txt")
                print(f"\n[+] Arquivo {filename}.txt deletado com sucesso!\n")
            else:
                print("\n[!] Arquivo não encontrado.\n")

        elif command == "createfolder":
            foldername = input("Nome da pasta: ")
            if foldername not in system_files:
                system_files[foldername] = []
                print(f"\n[+] Pasta {foldername} criada com sucesso!\n")
            else:
                print("\n[!] Pasta já existe.\n")

        elif command == "rmdir":
            foldername = input("Nome da pasta para remover: ")
            if foldername in system_files and system_files[foldername] == []:
                del system_files[foldername]
                print(f"\n[+] Pasta {foldername} removida com sucesso!\n")
            else:
                print("\n[!] Pasta não encontrada ou não está vazia.\n")

        elif command == "ls":
            print("\nConteúdo do diretório atual:")
            if current_directory == "root":
                for folder in system_files:
                    print(f"[DIR] {folder}")
                print()
            elif current_directory == "Workplace":
                for file in system_files["Workplace"]:
                    print(f"[FILE] {file}")
                print()

        elif command.startswith("cd"):
            directory = command.split(" ")[1]
            if directory in system_files:
                current_directory = directory
                print(f"\n[+] Você entrou no diretório {directory}.\n")
            else:
                print("\n[!] Diretório não encontrado.\n")

        elif command == "cat":
            filename = input("Nome do arquivo: ")
            if filename + ".txt" in system_files["Workplace"]:
                print(f"\nConteúdo de {filename}.txt:")
                time.sleep(2)
                print(f"[Arquivo de exemplo de lista: 'site1.onion', 'site2.onion', etc.']\n")
            else:
                print("\n[!] Arquivo não encontrado.\n")

        elif command == "nano":
            filename = input("Nome do arquivo: ")
            if filename + ".txt" in system_files["Workplace"]:
                print(f"\n[+] Editando {filename}.txt com nano...")
                time.sleep(2)
                print("[+] Modificações feitas com sucesso!\n")
            else:
                print("\n[!] Arquivo não encontrado.\n")

        elif command.startswith("ransomware"):
            try:
                pasta = command.split(" ")[1]
                if pasta in system_files:
                    ransomware_attack(pasta)
                else:
                    print("\n[!] Pasta não encontrada.\n")
            except:
                print("\n[!] Uso: ransomware <nome_da_pasta>\n")

        elif command == "clear":
            os.system('cls' if os.name == 'nt' else 'clear')

        elif command == "exit":
            print("\nSaindo...\n")
            break

        else:
            print("\n[!] Comando desconhecido. Use 'help' para ver os comandos.\n")

# Executando o instalador
show_installer()
