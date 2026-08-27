function enviarMensagem() {
    var campoMensagem = document.getElementById("message-input");
    var caixaChat = document.getElementById("chat-box");
    var texto = campoMensagem.value;

    if (texto == "") {
        alert("Digite uma mensagem!");
    } else {
        caixaChat.innerHTML +=
            '<div class="message user">' + texto + "</div>";
        campoMensagem.value = "";
        respostaSimulada();
    }
}

function respostaSimulada() {
    var caixaChat = document.getElementById("chat-box");

    caixaChat.innerHTML +=
        '<div class="message ia">' +
        "Esta é uma resposta de teste. A rede neural ainda vai ser implementada" +
        "</div>";
}

function abrirMenu() {
    var menu = document.getElementById("menu-lateral");
    menu.classList.toggle("menu-aberto");
}