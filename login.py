#fazer algumas partes separado para ir fazendo aos pouquinhos, ai quando terminar juntar com no main.py

#login de verificacao dos medicos
logins = {}

def forca_opcao(msg, opcao_validas, msg2):
    while True:
        escolha = input(msg).strip()
        if escolha in opcoes_validas:
            return escolha
        print(msg2)

def login_medico():
    while True:
        pedir_id = input("Digite sua identificacao (ou sair para voltar): ").strip()
        if pedir_login.lower() == 'sair':
            return False
        if pedir_id == logins:
            pedir_senha = input("Digitre sua senha: ").strip()
            if pedir_senha == login[pedir_id]['senha']:
                print(f"Login bem-sucedido! Bem vindo {login[pedir_id]}")
                return True 
            else:
                print("Senha incorreta. Tente Novamente.")
        else:
            print("ID nao encontrado. Tente novamente.")

def registrar_medico():
    novo_id = input("Digite um novo ID para o medico: ")
    if novo_id in logins:
        print("Este ID ja esta em uso. Escolha outro.")
        return
    nome = input("Digite o nome do medico: ").strip()
    crm = input("Digite o CRM: ").strip()
    senha = input("Digite a senha: ").strip()
    hierarquia = input("Digite a hierarquia: ").strip()
    area = intup("Digite a area de atuacao: ").strip()
    cpf = input("Digite o CPF (sem espacos ou simbolos: )").strip()
    
    logins[novo_id] = {
        'Nome': nome, 'CRM': crm, 'senha': senha, 'hierarquia': hierarquia, 'Area': area, 'CPF': cpf
    }
    print("Medico cadastrado no sistema!")
