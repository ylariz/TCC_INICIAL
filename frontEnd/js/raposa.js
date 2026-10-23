// ============================================================
// Raposa mascote da Yana
//
// Fica sentada na caixa de mensagem esperando a pergunta.
// Pisca e inclina a cabeça de vez em quando. Se ninguém falar
// nada por um tempo, deita e dorme. Quando chega uma mensagem,
// abre os olhos, espreguiça e volta a sentar.
//
// Este arquivo funciona sozinho: ele observa o chat (#chat-box e
// #message-input) sem precisar mudar o chat.js. Para tirar a
// raposa do site, basta remover o <script> dela no index.html.
// ============================================================

(function () {
    // Tempo sem conversa até ela dormir (em milissegundos)
    const TEMPO_PARA_DORMIR = 60 * 1000;

    const PASTA = "./assets/img/raposa/";
    const QUADROS = ["sentada", "piscando", "feliz", "deitada", "dormindo", "espreguicando"];

    const botao = document.getElementById("raposa");
    const imagem = document.getElementById("raposa-imagem");
    const caixaChat = document.getElementById("chat-box");
    const campoMensagem = document.getElementById("message-input");

    if (!botao || !imagem || !caixaChat) {
        return;
    }

    // Carrega todas as poses antes, para não piscar ao trocar
    QUADROS.forEach(function (nome) {
        const img = new Image();
        img.src = PASTA + nome + ".png";
    });

    let estado = "acordada";          // "acordada" ou "dormindo"
    let ultimoContato = Date.now();
    let travaAnimacao = 0;            // até quando uma animação está rodando
    let idSequencia = 0;
    let proximaAcao = Date.now() + 2000;

    function mostrar(nome) {
        imagem.src = PASTA + nome + ".png";
    }

    function animarClasse(classe, duracao) {
        botao.classList.remove(classe);
        void botao.offsetWidth; // reinicia a animação
        botao.classList.add(classe);
        setTimeout(function () { botao.classList.remove(classe); }, duracao);
    }

    function balao(classe, texto) {
        const el = document.createElement("span");
        el.className = "raposa-balao " + classe;
        el.textContent = texto;
        el.setAttribute("aria-hidden", "true");
        botao.appendChild(el);
        return el;
    }

    function limparBaloes() {
        botao.querySelectorAll(".raposa-balao").forEach(function (b) { b.remove(); });
    }

    // Toca uma sequência de poses. Se outra começar no meio
    // (ex.: acordar enquanto ainda está deitando), a anterior é cancelada.
    function tocarSequencia(passos) {
        const id = ++idSequencia;
        let tempo = 0;
        passos.forEach(function (passo) {
            setTimeout(function () { if (id === idSequencia) passo[0](); }, tempo);
            tempo += passo[1];
        });
        return tempo;
    }

    // Animações curtas enquanto está sentada (piscar, ficar feliz)
    function animacaoCurta(poses, passo) {
        const id = idSequencia;
        travaAnimacao = Date.now() + poses.length * passo + 50;
        poses.forEach(function (pose, i) {
            setTimeout(function () {
                if (estado === "acordada" && id === idSequencia) mostrar(pose);
            }, i * passo);
        });
        setTimeout(function () {
            if (estado === "acordada" && id === idSequencia) mostrar("sentada");
        }, poses.length * passo);
    }

    function inclinar() {
        travaAnimacao = Date.now() + 750;
        animarClasse("inclinando", 700);
    }

    function dormir() {
        if (estado === "dormindo") return;
        estado = "dormindo";
        limparBaloes();
        botao.setAttribute("aria-label", "Raposa mascote dormindo. Clique para acordar.");
        // fecha os olhos -> deita ainda acordada -> dorme enrolada
        tocarSequencia([
            [function () { mostrar("piscando"); }, 450],
            [function () { animarClasse("deitando", 350); mostrar("deitada"); }, 800],
            [function () {
                mostrar("dormindo");
                botao.classList.add("dormindo");
                balao("zzz", "z"); balao("zzz", "z"); balao("zzz", "z");
            }, 0],
        ]);
    }

    function acordar() {
        ultimoContato = Date.now();
        if (estado !== "dormindo") return;
        estado = "acordada";
        botao.classList.remove("dormindo");
        botao.setAttribute("aria-label", "Raposa mascote. Clique para fazer carinho.");
        limparBaloes();
        // abre os olhos deitada -> espreguiça -> senta com um pulinho
        const duracao = tocarSequencia([
            [function () {
                mostrar("deitada");
                const exclamacao = balao("exclamacao", "!");
                setTimeout(function () { exclamacao.remove(); }, 950);
            }, 600],
            [function () { mostrar("espreguicando"); }, 800],
            [function () { mostrar("sentada"); animarClasse("pulando", 450); }, 0],
        ]);
        travaAnimacao = Date.now() + duracao + 500;
    }

    // Alguém mandou mensagem: acorda ou, se já estava acordada, dá um pulinho
    function novaMensagem() {
        if (estado === "dormindo") {
            acordar();
        } else {
            ultimoContato = Date.now();
            if (Date.now() > travaAnimacao) animarClasse("pulando", 450);
        }
    }

    // ---------- relógio: decide quando piscar, inclinar ou dormir ----------
    setInterval(function () {
        const agora = Date.now();
        if (estado !== "acordada") return;

        if (agora - ultimoContato >= TEMPO_PARA_DORMIR) {
            dormir();
            return;
        }

        if (agora > proximaAcao && agora > travaAnimacao) {
            const sorteio = Math.random();
            if (sorteio < 0.6) animacaoCurta(["piscando"], 170);
            else if (sorteio < 0.8) animacaoCurta(["piscando", "sentada", "piscando"], 150);
            else inclinar();
            proximaAcao = agora + 2200 + Math.random() * 2800;
        }
    }, 1000);

    // ---------- ligações com o chat ----------

    // Nova mensagem do usuário no chat (sem precisar mudar o chat.js)
    new MutationObserver(function (mudancas) {
        mudancas.forEach(function (mudanca) {
            mudanca.addedNodes.forEach(function (no) {
                if (no.classList && no.classList.contains("user")) novaMensagem();
                if (no.classList && no.classList.contains("ia")) ultimoContato = Date.now();
            });
        });
    }).observe(caixaChat, { childList: true });

    // Digitar conta como "alguém está aqui": adia o sono e inclina a cabeça
    if (campoMensagem) {
        let ultimaInclinada = 0;
        campoMensagem.addEventListener("input", function () {
            if (estado !== "acordada") return;
            ultimoContato = Date.now();
            if (Date.now() - ultimaInclinada > 1500 && Date.now() > travaAnimacao) {
                ultimaInclinada = Date.now();
                inclinar();
            }
        });
    }

    // Carinho: clique na raposa
    botao.addEventListener("click", function () {
        if (estado === "dormindo") {
            acordar();
            return;
        }
        ultimoContato = Date.now();
        if (Date.now() < travaAnimacao) return;
        animarClasse("pulando", 450);
        animacaoCurta(["feliz", "feliz", "feliz"], 300);
    });

    mostrar("sentada");
})();
