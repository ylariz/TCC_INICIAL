const URL_RENDER = "";
const URL_BASE_API = URL_RENDER || "http://127.0.0.1:8000";
const URL_API = URL_BASE_API + "/pergunta";
const URL_EXECUTAR = URL_BASE_API + "/execute";
const CAMPO_PERGUNTA = "text";

const caixaChat = document.getElementById("chat-box");
const campoMensagem = document.getElementById("message-input");
const botaoEnviar = document.getElementById("botao-enviar");
const areaDigitacao = document.querySelector(".chat-input");

let esperandoResposta = false;

const LINGUAGENS_PYTHON = ["python", "py"];

function escreverTexto(elemento, texto) {
    elemento.textContent = "";

    const partes = String(texto).split("```");
    const ehMensagemDaYana = elemento.classList.contains("ia");

    partes.forEach(function (parte, indice) {
        const ehCodigo = indice % 2 === 1;

        if (ehCodigo) {
            const primeiraLinha = parte.match(/^([a-zA-Z0-9_+-]*)\n/);
            const linguagem = primeiraLinha ? primeiraLinha[1].toLowerCase() : "";
            const codigo = parte.replace(/^[a-zA-Z0-9_+-]*\n/, "").replace(/\n$/, "");

            const ehPython = ehMensagemDaYana && LINGUAGENS_PYTHON.includes(linguagem);
            elemento.appendChild(criarBlocoDeCodigo(codigo, ehPython));
        } else {
            const textoLimpo = parte.replace(/^\n+|\n+$/g, "");
            if (textoLimpo !== "") {
                elemento.appendChild(document.createTextNode(textoLimpo));
            }
        }
    });
}

function criarBlocoDeCodigo(codigo, ehPython) {
    const pre = document.createElement("pre");
    const code = document.createElement("code");
    pre.classList.add("codigo");
    code.textContent = codigo;
    pre.appendChild(code);

    if (!ehPython) {
        return pre;
    }

    const bloco = document.createElement("div");
    bloco.classList.add("bloco-codigo");

    const barra = document.createElement("div");
    barra.classList.add("bloco-codigo-barra");

    const rotulo = document.createElement("span");
    rotulo.classList.add("bloco-codigo-linguagem");
    rotulo.textContent = "Python";

    const botao = document.createElement("button");
    botao.type = "button";
    botao.classList.add("botao-levar-editor");
    botao.textContent = "Levar para o editor";
    botao.setAttribute("aria-label", "Levar para o editor o código deste exemplo");
    botao.addEventListener("click", function () {
        levarParaEditor(codigo, botao);
    });

    barra.appendChild(rotulo);
    barra.appendChild(botao);
    bloco.appendChild(barra);
    bloco.appendChild(pre);
    return bloco;
}

function levarParaEditor(codigo, botao) {
    const editor = document.getElementById("terminal");
    const atual = editor.value;

    if (atual.trim() !== "" && atual !== codigo) {
        const substituir = window.confirm(
            "O editor já tem um código. Deseja substituí-lo pelo exemplo da Yana?"
        );
        if (!substituir) {
            return;
        }
    }

    editor.value = codigo;
    marcarResultadoAnterior();
    abrirEntradasSePrecisar(codigo);
    editor.focus();
    editor.setSelectionRange(0, 0);
    editor.scrollTop = 0;
    editor.scrollLeft = 0;

    editor.scrollIntoView({ block: "nearest", behavior: "smooth" });

    botao.textContent = "Código no editor";
    botao.classList.add("feito");
    clearTimeout(botao.temporizador);
    botao.temporizador = setTimeout(function () {
        botao.textContent = "Levar para o editor";
        botao.classList.remove("feito");
    }, 2000);
    avisarLeitorDeTela("Código copiado para o editor.");
}

function avisarLeitorDeTela(mensagem) {
    const aviso = document.getElementById("aviso-leitor");
    if (!aviso) {
        return;
    }
    aviso.textContent = "";
    setTimeout(function () { aviso.textContent = mensagem; }, 50);
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
    areaDigitacao.classList.remove("vazio");
    void areaDigitacao.offsetWidth;
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

function atualizarBotaoMenu() {
    const aberto = document.getElementById("menu-lateral").classList.contains("menu-aberto");
    const botao = document.getElementById("botao-menu");
    botao.setAttribute("aria-expanded", aberto ? "true" : "false");
    botao.setAttribute("aria-label", aberto ? "Fechar menu" : "Abrir menu");
}

function moverFocoDoMenu() {
    const menu = document.getElementById("menu-lateral");

    if (menu.classList.contains("menu-aberto")) {
        document.getElementById("botao-fechar-menu").focus();
    } else if (menu.contains(document.activeElement)) {
        document.getElementById("botao-menu").focus();
    }
}

function abrirMenu() {
    document.getElementById("menu-lateral").classList.toggle("menu-aberto");
    atualizarBotaoMenu();
    moverFocoDoMenu();
}

document.addEventListener("click", function (evento) {
    const menu = document.getElementById("menu-lateral");
    const clicouNoMenu = menu.contains(evento.target);
    const clicouNoBotao = evento.target.closest(".menu-button");

    if (menu.classList.contains("menu-aberto") && !clicouNoMenu && !clicouNoBotao) {
        menu.classList.remove("menu-aberto");
        atualizarBotaoMenu();
    }
});

document.addEventListener("keydown", function (evento) {
    const menu = document.getElementById("menu-lateral");

    if (evento.key === "Escape" && menu.classList.contains("menu-aberto")) {
        menu.classList.remove("menu-aberto");
        atualizarBotaoMenu();
        moverFocoDoMenu();
    }
});

const terminal = document.getElementById("terminal");
const dicaEditor = document.getElementById("dica-editor");
const INDENTACAO = "    ";

let tabSaiDoEditor = false;

function ligarSaidaPorTab(ligado) {
    tabSaiDoEditor = ligado;
    if (dicaEditor) {
        dicaEditor.classList.toggle("destaque", ligado);
    }
}

function substituirNoTerminal(inicio, fim, novo, selInicio, selFim) {
    terminal.focus();
    terminal.setSelectionRange(inicio, fim);
    let feito = false;
    try {
        feito = document.execCommand("insertText", false, novo);
    } catch (e) {
        feito = false;
    }
    if (!feito) {
        terminal.setRangeText(novo, inicio, fim, "end");
        terminal.dispatchEvent(new Event("input", { bubbles: true }));
    }
    terminal.setSelectionRange(selInicio, selFim);
}

function linhasDaSelecao() {
    const texto = terminal.value;
    const ini = terminal.selectionStart;
    let fim = terminal.selectionEnd;
    if (fim > ini && texto[fim - 1] === "\n") {
        fim -= 1;
    }
    const inicioBloco = texto.lastIndexOf("\n", ini - 1) + 1;
    let fimBloco = texto.indexOf("\n", fim);
    if (fimBloco === -1) {
        fimBloco = texto.length;
    }
    return { ini: ini, fim: terminal.selectionEnd, inicioBloco: inicioBloco, fimBloco: fimBloco };
}

function indentar() {
    const s = linhasDaSelecao();
    const texto = terminal.value;
    const temSelecao = s.ini !== s.fim;
    const antesDoCursor = texto.slice(s.inicioBloco, s.ini);

    if (!temSelecao && /^ *$/.test(antesDoCursor)) {
        substituirNoTerminal(s.ini, s.ini, INDENTACAO, s.ini + 4, s.ini + 4);
        return;
    }

    const linhas = texto.slice(s.inicioBloco, s.fimBloco).split("\n");
    let antesDoInicio = 0;
    let total = 0;
    const novas = linhas.map(function (linha, i) {
        if (linha === "") {
            return linha;
        }
        if (i === 0) {
            antesDoInicio = 4;
        }
        total += 4;
        return INDENTACAO + linha;
    });

    const varias = linhas.length > 1;
    const novoBloco = novas.join("\n");
    if (varias) {
        substituirNoTerminal(s.inicioBloco, s.fimBloco, novoBloco, s.inicioBloco, s.inicioBloco + novoBloco.length);
    } else {
        substituirNoTerminal(s.inicioBloco, s.fimBloco, novoBloco, s.ini + antesDoInicio, s.fim + total);
    }
}

function desindentar() {
    const s = linhasDaSelecao();
    const texto = terminal.value;
    const linhas = texto.slice(s.inicioBloco, s.fimBloco).split("\n");
    let removidosTotal = 0;
    let removidosPrimeira = 0;

    const novas = linhas.map(function (linha, i) {
        const espacos = linha.match(/^ {0,4}/)[0].length;
        if (i === 0) {
            removidosPrimeira = espacos;
        }
        removidosTotal += espacos;
        return linha.slice(espacos);
    });

    if (removidosTotal === 0) {
        return;
    }

    const novoBloco = novas.join("\n");
    if (linhas.length > 1) {
        substituirNoTerminal(s.inicioBloco, s.fimBloco, novoBloco, s.inicioBloco, s.inicioBloco + novoBloco.length);
    } else {
        const ini = Math.max(s.inicioBloco, s.ini - removidosPrimeira);
        const fim = Math.max(ini, s.fim - removidosPrimeira);
        substituirNoTerminal(s.inicioBloco, s.fimBloco, novoBloco, ini, fim);
    }
}

terminal.addEventListener("keydown", function (evento) {
    if (evento.key === "Enter" && (evento.ctrlKey || evento.metaKey)) {
        evento.preventDefault();
        executarCodigo();
        return;
    }

    if (evento.key === "Escape") {
        ligarSaidaPorTab(true);
        avisarLeitorDeTela("Tab agora sai do editor.");
        return;
    }

    if (evento.key === "Tab" && !evento.ctrlKey && !evento.altKey && !evento.metaKey) {
        if (tabSaiDoEditor) {
            ligarSaidaPorTab(false);
            return;
        }
        evento.preventDefault();
        if (evento.shiftKey) {
            desindentar();
        } else {
            indentar();
        }
        return;
    }

    if (!["Shift", "Control", "Alt", "Meta"].includes(evento.key)) {
        ligarSaidaPorTab(false);
    }
});

terminal.addEventListener("blur", function () {
    ligarSaidaPorTab(false);
});


const TEMPO_MAXIMO_ESPERA = 15000;

const botaoExecutar = document.getElementById("botao-executar");
const campoEntradas = document.getElementById("entradas");
const painelEntradas = document.getElementById("painel-entradas");
const campoResultado = document.getElementById("feedback");
const statusExecucao = document.getElementById("status-execucao");

const MENSAGEM_TIMEOUT_API = "Execução interrompida: limite de tempo excedido.";

let executando = false;

let codigoDoResultado = null;

function abrirEntradasSePrecisar(codigo) {
    if (/\binput\s*\(/.test(codigo)) {
        painelEntradas.open = true;
    }
}

function mostrarStatus(texto, tipo) {
    statusExecucao.textContent = texto;
    statusExecucao.dataset.tipo = tipo || "";
}

function respostaValida(dados) {
    return dados !== null
        && typeof dados === "object"
        && typeof dados.sucesso === "boolean"
        && typeof dados.saida === "string"
        && (dados.erro === null || dados.erro === undefined || typeof dados.erro === "string");
}

function mostrarRespostaInvalida(motivo) {
    campoResultado.value = motivo + "\nO código pode não ter sido executado.";
    mostrarStatus("Resposta inválida da API", "erro");
}

function marcarResultadoAnterior() {
    if (codigoDoResultado !== null && !executando && terminal.value !== codigoDoResultado) {
        mostrarStatus("Resultado da execução anterior", "anterior");
        codigoDoResultado = null;
    }
}

terminal.addEventListener("input", marcarResultadoAnterior);

function mostrarResultado(dados, codigo) {
    const saida = dados.saida;
    const erro = typeof dados.erro === "string" ? dados.erro : "";

    let texto = saida;
    if (erro !== "" && erro !== saida) {
        texto = saida === "" ? erro : saida.replace(/\n?$/, "\n") + erro;
    }

    campoResultado.value = texto;
    campoResultado.scrollTop = 0;

    codigoDoResultado = codigo;

    if (dados.sucesso === false) {
        const foiTimeout = erro.trim() === MENSAGEM_TIMEOUT_API;
        mostrarStatus(foiTimeout ? "Interrompido: tempo limite" : "A execução falhou", "erro");
    } else if (saida.includes("Traceback (most recent call last)")) {
        mostrarStatus("O programa terminou com erro", "erro");
    } else if (texto === "") {
        mostrarStatus("Executado, sem nada impresso", "ok");
    } else {
        mostrarStatus("Execução concluída", "ok");
    }
}

async function executarCodigo() {
    if (executando) {
        return;
    }

    const codigo = terminal.value;

    if (codigo.trim() === "") {
        mostrarStatus("Escreva um código no terminal primeiro", "aviso");
        terminal.focus();
        return;
    }

    abrirEntradasSePrecisar(codigo);

    codigoDoResultado = null;
    executando = true;
    botaoExecutar.disabled = true;
    botaoExecutar.textContent = "Executando...";
    campoResultado.value = "";
    campoResultado.setAttribute("aria-busy", "true");
    mostrarStatus("Executando...", "carregando");

    const controle = new AbortController();
    const temporizador = setTimeout(function () { controle.abort(); }, TEMPO_MAXIMO_ESPERA);

    try {
        const resposta = await fetch(URL_EXECUTAR, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ codigo: codigo, entrada: campoEntradas.value }),
            signal: controle.signal,
        });

        if (!resposta.ok) {
            const corpo = await resposta.text().catch(function () { return ""; });
            campoResultado.value =
                "O servidor respondeu com erro HTTP " + resposta.status + "." +
                (corpo ? "\n\nResposta do servidor:\n" + corpo.slice(0, 500) : "");
            mostrarStatus("Erro HTTP " + resposta.status, "erro");
            return;
        }

        let dados;
        try {
            dados = await resposta.json();
        } catch (erroFormato) {
            mostrarRespostaInvalida("A API respondeu em um formato que não é JSON.");
            return;
        }

        if (!respostaValida(dados)) {
            mostrarRespostaInvalida("A API respondeu sem os campos esperados (sucesso e saida).");
            return;
        }

        mostrarResultado(dados, codigo);
    } catch (erro) {
        if (erro.name === "AbortError") {
            campoResultado.value =
                "A API não respondeu em " + (TEMPO_MAXIMO_ESPERA / 1000) + " segundos. Tente de novo.";
            mostrarStatus("Sem resposta da API", "erro");
        } else {
            campoResultado.value =
                "Não foi possível conectar à API em " + URL_BASE_API + ".\n" +
                "Verifique se o servidor do back-end está rodando.";
            mostrarStatus("Sem conexão com a API", "erro");
        }
        console.error(erro);
    } finally {
        clearTimeout(temporizador);
        executando = false;
        botaoExecutar.disabled = false;
        botaoExecutar.textContent = "Executar código";
        campoResultado.removeAttribute("aria-busy");
    }
}
