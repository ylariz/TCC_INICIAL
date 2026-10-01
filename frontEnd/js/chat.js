const URL_API = "http://127.0.0.1:8000/pergunta";
const CAMPO_PERGUNTA = "text";

const caixaChat = document.getElementById("chat-box");
const campoMensagem = document.getElementById("message-input");

function adicionarMensagem(texto, tipo) {
    const div = document.createElement("div");
    div.classList.add("message", tipo);
    div.textContent = texto; 
    caixaChat.appendChild(div);
    caixaChat.scrollTop = caixaChat.scrollHeight;
    return div;
}

async function enviarMensagem() {
    const texto = campoMensagem.value.trim();

    if (texto === "") {
        alert("Digite uma mensagem!");
        return;
    }

    adicionarMensagem(texto, "user");
    campoMensagem.value = "";

    const mensagemYana = adicionarMensagem("Yana está pensando...", "ia");

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
        mensagemYana.textContent = dados.resposta;

        console.log("Intenção:", dados.intencao, "| Confiança:", dados.confianca);
    } catch (erro) {
        mensagemYana.textContent = "Não consegui falar com o servidor. A API está rodando?";
        console.error(erro);
    }
}

campoMensagem.addEventListener("keydown", function (evento) {
    if (evento.key === "Enter") {
        enviarMensagem();
    }
});

function abrirMenu() {
    document.getElementById("menu-lateral").classList.toggle("menu-aberto");
}