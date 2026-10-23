const URL_API = "http://127.0.0.1:8000/pergunta";
const CAMPO_PERGUNTA = "text";

const caixaChat = document.getElementById("chat-box");
const campoMensagem = document.getElementById("message-input");
const botaoEnviar = document.getElementById("botao-enviar");
const areaDigitacao = document.querySelector(".chat-input");

let esperandoResposta = false;

// Escreve o texto na mensagem. Trechos entre ``` viram um bloco de código.
// Usa textContent em tudo, então nenhum HTML vindo da API é executado.
function escreverTexto(elemento, texto) {
    elemento.textContent = "";

    const partes = String(texto).split("```");

    partes.forEach(function (parte, indice) {
        const ehCodigo = indice % 2 === 1;

        if (ehCodigo) {
            // Remove o nome da linguagem da primeira linha (```python)
            const codigo = parte.replace(/^[a-zA-Z]*\n/, "").replace(/\n$/, "");
            const pre = document.createElement("pre");
            const code = document.createElement("code");
            pre.classList.add("codigo");
            code.textContent = codigo;
            pre.appendChild(code);
            elemento.appendChild(pre);
        } else {
            const textoLimpo = parte.replace(/^\n+|\n+$/g, "");
            if (textoLimpo !== "") {
                elemento.appendChild(document.createTextNode(textoLimpo));
            }
        }
    });
}

function rolarParaFinal() {
    caixaChat.scrollTop = caixaChat.scrollHeight;
}

function adicionarMensagem(texto, tipo) {
    const div = document.createElement("div");
    div.classList.add("message", tipo);
    escreverTexto(div, texto);
    caixaChat.appendChild(div);
    rolarParaFinal();
    return div;
}

function avisarCampoVazio() {
    // Pequeno tremor no campo em vez do alert
    areaDigitacao.classList.remove("vazio");
    void areaDigitacao.offsetWidth; // reinicia a animação
    areaDigitacao.classList.add("vazio");
    campoMensagem.focus();
}

async function enviarMensagem() {
    if (esperandoResposta) {
        return;
    }

    const texto = campoMensagem.value.trim();

    if (texto === "") {
        avisarCampoVazio();
        return;
    }

    adicionarMensagem(texto, "user");
    campoMensagem.value = "";

    const mensagemYana = adicionarMensagem("Yana está pensando", "ia");
    mensagemYana.classList.add("pensando");

    esperandoResposta = true;
    botaoEnviar.disabled = true;

    try {
        const resposta = await fetch(URL_API, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ [CAMPO_PERGUNTA]: texto }),
        });

        if (!resposta.ok) {
            throw new Error("Erro HTTP " + resposta.status);
        }

        const dados = await resposta.json();
        escreverTexto(mensagemYana, dados.resposta);

        console.log("Intenção:", dados.intencao, "| Confiança:", dados.confianca);
    } catch (erro) {
        mensagemYana.textContent = "Não consegui falar com o servidor. A API está rodando?";
        console.error(erro);
    } finally {
        mensagemYana.classList.remove("pensando");
        esperandoResposta = false;
        botaoEnviar.disabled = false;
        campoMensagem.focus();
        rolarParaFinal();
    }
}

campoMensagem.addEventListener("keydown", function (evento) {
    if (evento.key === "Enter") {
        enviarMensagem();
    }
});

areaDigitacao.addEventListener("animationend", function () {
    areaDigitacao.classList.remove("vazio");
});

function abrirMenu() {
    document.getElementById("menu-lateral").classList.toggle("menu-aberto");
}

// Fecha o menu lateral ao clicar fora dele ou apertar Esc
document.addEventListener("click", function (evento) {
    const menu = document.getElementById("menu-lateral");
    const clicouNoMenu = menu.contains(evento.target);
    const clicouNoBotao = evento.target.closest(".menu-button");

    if (menu.classList.contains("menu-aberto") && !clicouNoMenu && !clicouNoBotao) {
        menu.classList.remove("menu-aberto");
    }
});

document.addEventListener("keydown", function (evento) {
    if (evento.key === "Escape") {
        document.getElementById("menu-lateral").classList.remove("menu-aberto");
    }
});

// No terminal, a tecla Tab coloca 4 espaços (indentação do Python)
// em vez de pular para outro campo.
const terminal = document.getElementById("terminal");

terminal.addEventListener("keydown", function (evento) {
    if (evento.key === "Tab") {
        evento.preventDefault();
        const inicio = terminal.selectionStart;
        const fim = terminal.selectionEnd;
        terminal.value = terminal.value.slice(0, inicio) + "    " + terminal.value.slice(fim);
        terminal.selectionStart = terminal.selectionEnd = inicio + 4;
    }
});
