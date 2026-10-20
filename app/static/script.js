
"use strict";

// ==========================================
// 1. ELEMENTOS DA PÁGINA
// ==========================================

const listaInscricoes = document.getElementById("lista-inscricoes");
const botaoMarca = document.getElementById("botao-marca");
const formulario = document.getElementById("formulario-marca");
const botaoCancelar = document.getElementById("botao-cancelar");
const botaoEnviar = document.getElementById("botao-enviar");

const campoNome = document.getElementById("nome");
const campoMensagem = document.getElementById("mensagem");

const contadorCaracteres = document.getElementById(
    "contador-caracteres"
);

const mensagemStatus = document.getElementById("mensagem-status");


// ==========================================
// 2. MOSTRAR MENSAGENS DE STATUS
// ==========================================

function mostrarStatus(mensagem, tipo = "") {
    mensagemStatus.textContent = mensagem;
    mensagemStatus.className = "mensagem-status";

    if (tipo) {
        mensagemStatus.classList.add(tipo);
    }
}


// ==========================================
// 3. FORMATAR A DATA
// ==========================================

function formatarData(dataISO) {
    const data = new Date(dataISO);

    if (Number.isNaN(data.getTime())) {
        return "Data indisponível";
    }

    return new Intl.DateTimeFormat("pt-BR", {
        dateStyle: "short",
        timeStyle: "short"
    }).format(data);
}


// ==========================================
// 4. CRIAR UM ELEMENTO DE INSCRIÇÃO
// ==========================================

function criarElementoInscricao(inscricao) {
    const artigo = document.createElement("article");
    artigo.className = "inscricao";

    const cabecalho = document.createElement("div");
    cabecalho.className = "inscricao-cabecalho";

    const nome = document.createElement("h3");
    nome.className = "inscricao-nome";
    nome.textContent = inscricao.nome;

    const data = document.createElement("time");
    data.className = "inscricao-data";
    data.dateTime = inscricao.criado_em;
    data.textContent = formatarData(inscricao.criado_em);

    const mensagem = document.createElement("p");
    mensagem.className = "inscricao-mensagem";
    mensagem.textContent = inscricao.mensagem;

    cabecalho.append(nome, data);
    artigo.append(cabecalho, mensagem);

    return artigo;
}


// ==========================================
// 5. CARREGAR AS INSCRIÇÕES
// ==========================================

async function carregarInscricoes() {
    listaInscricoes.replaceChildren();

    const carregando = document.createElement("p");
    carregando.className = "estado-lista";
    carregando.textContent = "Abrindo as páginas do grimório...";

    listaInscricoes.append(carregando);

    try {
        const resposta = await fetch("/api/inscricoes");

        if (!resposta.ok) {
            throw new Error("Não foi possível carregar as inscrições.");
        }

        const inscricoes = await resposta.json();

        listaInscricoes.replaceChildren();

        if (inscricoes.length === 0) {
            const vazio = document.createElement("p");
            vazio.className = "estado-lista";
            vazio.textContent =
                "Estas páginas ainda estão vazias. Deixe sua primeira marca.";

            listaInscricoes.append(vazio);
            return;
        }

        for (const inscricao of inscricoes) {
            listaInscricoes.append(
                criarElementoInscricao(inscricao)
            );
        }
    } catch (erro) {
        console.error(erro);

        listaInscricoes.replaceChildren();

        const falha = document.createElement("p");
        falha.className = "estado-lista";
        falha.textContent =
            "Não foi possível abrir o grimório. Tente novamente.";

        listaInscricoes.append(falha);
    }
}


// ==========================================
// 6. ABRIR E FECHAR O FORMULÁRIO
// ==========================================

function abrirFormulario() {
    formulario.hidden = false;
    botaoMarca.setAttribute("aria-expanded", "true");

    mostrarStatus("");

    campoNome.focus();

    formulario.scrollIntoView({
        behavior: "smooth",
        block: "nearest"
    });
}

function fecharFormulario() {
    formulario.hidden = true;
    botaoMarca.setAttribute("aria-expanded", "false");

    mostrarStatus("");

    botaoMarca.focus();
}

botaoMarca.addEventListener("click", () => {
    if (formulario.hidden) {
        abrirFormulario();
    } else {
        fecharFormulario();
    }
});

botaoCancelar.addEventListener("click", () => {
    fecharFormulario();
});


// ==========================================
// 7. CONTADOR DE CARACTERES
// ==========================================

function atualizarContador() {
    contadorCaracteres.textContent = campoMensagem.value.length;
}

campoMensagem.addEventListener("input", atualizarContador);


// ==========================================
// 8. ENVIAR UMA NOVA INSCRIÇÃO
// ==========================================

formulario.addEventListener("submit", async (evento) => {
    evento.preventDefault();

    const nome = campoNome.value.trim();
    const mensagem = campoMensagem.value.trim();

    if (!nome || !mensagem) {
        mostrarStatus(
            "Preencha seu nome e sua mensagem.",
            "erro"
        );
        return;
    }

    if (nome.length > 50 || mensagem.length > 100) {
        mostrarStatus(
            "Confira os limites de caracteres dos campos.",
            "erro"
        );
        return;
    }

    botaoEnviar.disabled = true;
    botaoEnviar.textContent = "Registrando...";

    mostrarStatus("");

    try {
        const resposta = await fetch("/api/inscricoes", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                nome: nome,
                mensagem: mensagem
            })
        });

        const resultado = await resposta.json();

        if (!resposta.ok) {
            const detalhe = typeof resultado.detail === "string"
                ? resultado.detail
                : "Não foi possível registrar sua marca.";

            throw new Error(detalhe);
        }

        // A inscrição só é exibida após a confirmação do servidor.
        const novaInscricao = criarElementoInscricao(resultado);

        if (
            listaInscricoes.children.length === 1 &&
            listaInscricoes.firstElementChild.classList.contains(
                "estado-lista"
            )
        ) {
            listaInscricoes.replaceChildren();
        }

        listaInscricoes.prepend(novaInscricao);

        formulario.reset();
        atualizarContador();

        mostrarStatus(
            "Sua marca foi registrada no grimório!",
            "sucesso"
        );

        fecharFormulario();
        mostrarStatus(
            "Sua marca foi registrada no grimório!",
            "sucesso"
        );

        novaInscricao.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });
    } catch (erro) {
        console.error(erro);

        mostrarStatus(
            erro.message || "Ocorreu um erro ao registrar sua marca.",
            "erro"
        );
    } finally {
        botaoEnviar.disabled = false;
        botaoEnviar.textContent = "Registrar marca";
    }
});


// ==========================================
// 9. INICIALIZAÇÃO
// ==========================================

atualizarContador();
carregarInscricoes();
