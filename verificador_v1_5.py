import os
import sys
import requests
import shutil
import logging
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock

# Configuração de logging
logging.basicConfig(
    filename="erros.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

VERSAO_ATUAL = "1.5"
URL_JSON_ATUALIZACAO = "https://chensonbh763.github.io/controle-de-atualizacao/atualizacao.json"
EXECUTAVEL_ATUAL = os.path.basename(sys.argv[0])  # Nome do executável em execução
NOME_EXECUTAVEL_NOVO = "novo_verificador.exe"

class VerificadorApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Label de instrução
        self.label_instrucao = Label(text="Insira os links (um por linha):", size_hint=(1, 0.1))
        self.layout.add_widget(self.label_instrucao)

        # Campo de texto para links
        self.text_input = TextInput(hint_text="Digite os links aqui", multiline=True, size_hint=(1, 0.6))
        self.layout.add_widget(self.text_input)

        # Botão para carregar lista
        self.botao_carregar = Button(text="Carregar Lista e Verificar Atualização", size_hint=(1, 0.1))
        self.botao_carregar.bind(on_press=self.carregar_lista)
        self.layout.add_widget(self.botao_carregar)

        # Barra de progresso
        self.progress_bar = ProgressBar(max=100, value=0, size_hint=(1, 0.1))
        self.layout.add_widget(self.progress_bar)

        # Campo para exibir resultados
        self.resultados = TextInput(readonly=True, size_hint=(1, 0.6))
        self.layout.add_widget(self.resultados)

        # Agendar a verificação de atualizações após a construção da interface
        Clock.schedule_once(self.verificar_atualizacao, 0)

        return self.layout

    def verificar_atualizacao(self, *args):
        """Verifica se há uma nova versão e baixa o arquivo, se necessário."""
        try:
            resposta = requests.get(URL_JSON_ATUALIZACAO, timeout=10)
            if resposta.status_code == 200:
                dados = resposta.json()
                versao_remota = dados.get("versao", None)
                url_download = dados.get("url_atualizacao", None)

                if versao_remota and versao_remota != VERSAO_ATUAL:
                    self.resultados.text += "[INFO] Nova versão disponível! Baixando...\n"
                    self.baixar_e_substituir_executavel(url_download)
                else:
                    self.resultados.text += "[INFO] Já está na versão mais recente.\n"
            else:
                self.resultados.text += "[ERRO] Falha ao verificar atualizações.\n"
        except Exception as e:
            logging.error(f"Erro ao verificar atualizações: {e}")
            self.resultados.text += "[ERRO] Falha na verificação de atualizações.\n"

    def baixar_e_substituir_executavel(self, url_download):
        """Baixa o novo executável e substitui o atual."""
        try:
            # Baixar o novo executável
            response = requests.get(url_download, stream=True, timeout=30)
            if response.status_code == 200:
                novo_caminho = os.path.join(os.getcwd(), NOME_EXECUTAVEL_NOVO)
                with open(novo_caminho, "wb") as novo_arquivo:
                    shutil.copyfileobj(response.raw, novo_arquivo)
                self.resultados.text += "[INFO] Atualização baixada com sucesso!\n"

                # Substituir o executável atual
                self.substituir_executavel(novo_caminho)
            else:
                self.resultados.text += "[ERRO] Falha ao baixar nova versão.\n"
        except Exception as e:
            logging.error(f"Erro ao baixar a nova versão: {e}")
            self.resultados.text += "[ERRO] Falha ao baixar nova versão.\n"

    def substituir_executavel(self, novo_caminho):
        """Substitui o executável atual pelo novo baixado."""
        try:
            self.resultados.text += "[INFO] Substituindo executável...\n"

            # Caminho completo do executável atual
            atual_caminho = os.path.join(os.getcwd(), EXECUTAVEL_ATUAL)

            # Renomear o atual para um backup
            backup_caminho = atual_caminho.replace(".exe", "_backup.exe")
            if os.path.exists(backup_caminho):
                os.remove(backup_caminho)
            os.rename(atual_caminho, backup_caminho)

            # Renomear o novo executável para o nome atual
            os.rename(novo_caminho, atual_caminho)

            # Reiniciar o aplicativo
            self.reiniciar_aplicativo()
        except Exception as e:
            logging.error(f"Erro ao substituir executável: {e}")
            self.resultados.text += "[ERRO] Falha ao substituir executável.\n"

    def reiniciar_aplicativo(self):
        """Reinicia o aplicativo atualizado."""
        try:
            self.resultados.text += "[INFO] Reiniciando o aplicativo...\n"
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            logging.error(f"Erro ao reiniciar aplicativo: {e}")
            self.resultados.text += "[ERRO] Falha ao reiniciar o aplicativo.\n"

    def carregar_lista(self, instance):
        """Função fictícia apenas para fins de exemplo."""
        self.resultados.text += "[INFO] Função 'Carregar Lista' chamada.\n"

# Executar o app
if __name__ == "__main__":
    VerificadorApp().run()
