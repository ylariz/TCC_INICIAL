# YaPy LSTM - Projeto de TCC

## Tecnologias

- **Python:** linguagem principal do backend e dos componentes de inteligência artificial.
- **PyTorch:** biblioteca utilizada na implementação e execução da rede neural.
- **LSTM (Long Short-Term Memory):** arquitetura de rede neural recorrente utilizada pelo modelo.
- **FastAPI:** framework utilizado para disponibilizar as funcionalidades por meio de uma API.
- **Uvicorn:** servidor ASGI responsável por executar a aplicação FastAPI.
- **Pydantic:** biblioteca utilizada para validação e estruturação de dados.
- **HTML, CSS e JavaScript:** tecnologias utilizadas na construção da interface web.

## Estrutura do projeto

O projeto é organizado em módulos para separar a interface, a API, o processamento dos dados e os componentes de inteligência artificial.

- `backEnd/API/` — aplicação FastAPI, rotas, controladores, serviços e tratamento de erros.
- `backEnd/IA/dados/` — organização e preparação dos dados utilizados pelo modelo.
- `backEnd/IA/modelo/` — implementação da arquitetura da rede neural.
- `backEnd/IA/treino/` — código responsável pelo treinamento do modelo.
- `backEnd/IA/inferencia/` — processamento das entradas e geração de respostas durante a execução.
- `backEnd/IA/pesos/` — armazenamento dos parâmetros do modelo treinado.
- `frontEnd/` — interface web, estilos, chat e recursos visuais.

## Modelo de inteligência artificial

A estrutura de inteligência artificial contempla diferentes etapas do desenvolvimento de um modelo:

- **Preparação dos dados:** organização dos dados utilizados no treinamento.
- **Implementação da arquitetura:** definição da rede neural recorrente LSTM.
- **Treinamento:** código dedicado ao ajuste dos parâmetros do modelo.
- **Persistência:** armazenamento dos pesos treinados para utilização posterior.
- **Inferência:** carregamento do modelo e processamento das entradas durante a execução da aplicação.

O treinamento e a inferência são organizados separadamente, permitindo que o modelo treinado seja utilizado pela aplicação sem precisar executar o treinamento a cada inicialização.

## Backend e API

O backend utiliza FastAPI para disponibilizar as funcionalidades da aplicação. A estrutura inclui rotas, controladores e serviços responsáveis pelo processamento das requisições, integração com os componentes de IA e tratamento de erros.

## Interface web

O frontend utiliza HTML, CSS e JavaScript para fornecer a interface de interação com o sistema. Inclui a interface de conversa, os estilos visuais e os recursos gráficos próprios do projeto.

## Requisitos

Antes de executar o projeto, é necessário ter:

- **Python 3.12 ou versão compatível** com as dependências especificadas no projeto.
- **Git**, para clonar o repositório.
- Um navegador atualizado.
- Conexão com a internet para instalar as dependências.
- Os arquivos do modelo treinado presentes em `backEnd/IA/pesos/`.

Os comandos abaixo utilizam o PowerShell no Windows. Para outros sistemas operacionais, os comandos de ativação do ambiente virtual podem ser diferentes.

## Instalação e execução

### 1. Clonar o repositório

Abra o terminal e execute:

```powershell
git clone https://github.com/ylariz/TCC_INICIAL.git
cd TCC_INICIAL
```

Se o repositório já estiver clonado, entre diretamente na pasta local do projeto.

### 2. Criar o ambiente virtual

Acesse a pasta do backend:

```powershell
cd backEnd
python -m venv .venv
```

O ambiente virtual mantém as dependências do projeto isoladas das demais instalações do Python.

### 3. Ativar o ambiente virtual

No Windows com PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Se a execução de scripts estiver bloqueada, utilize o Prompt de Comando (CMD) e execute:

```bat
.venv\Scripts\activate.bat
```

### 4. Instalar as dependências

Com o ambiente virtual ativado, execute:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

O arquivo `requirements.txt` especifica as bibliotecas e versões necessárias ao backend, incluindo FastAPI, Uvicorn, Pydantic e PyTorch. A instalação do PyTorch pode exigir o download de um pacote grande.

### 5. Iniciar o backend

Ainda na pasta `backEnd`, com o ambiente virtual ativado, execute:

```powershell
python -m uvicorn API.app:app --host 127.0.0.1 --port 8000
```

Mantenha esse terminal aberto enquanto utilizar a aplicação.

A documentação interativa da API ficará disponível em:

`http://127.0.0.1:8000/docs`

### 6. Iniciar o frontend

Abra um **segundo terminal**. A partir da raiz do repositório, execute:

```powershell
cd frontEnd
python -m http.server 5500
```

Mantenha esse terminal aberto e acesse no navegador:

`http://localhost:5500`

### 7. Encerrar a aplicação

Para encerrar cada servidor, volte ao terminal correspondente e pressione `Ctrl + C`.
