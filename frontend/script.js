// Travas para uso em totem/kiosk touchscreen: sem menu de contexto,
// sem pinça de zoom e sem o zoom por "duplo toque" do navegador.
// (o modo kiosk do navegador em si, ex.: F11, é ligado manualmente, não por aqui)
document.addEventListener("contextmenu", (e) => e.preventDefault());
document.addEventListener(
  "gesturestart",
  (e) => e.preventDefault(),
  { passive: false }
);
document.addEventListener(
  "touchmove",
  (e) => {
    if (e.touches.length > 1) e.preventDefault();
  },
  { passive: false }
);
let ultimoToque = 0;
document.addEventListener(
  "touchend",
  (e) => {
    const agora = Date.now();
    if (agora - ultimoToque <= 300) e.preventDefault();
    ultimoToque = agora;
  },
  { passive: false }
);

// Fade de saída suave e reutilizável entre telas: tira a animação de entrada
// dos elementos, força o navegador a "assentar" isso e só então anima a
// opacidade até 0 (ver comentário da classe .saida-transicao no CSS).
function saidaSuave(elementos, duracaoMs, aoTerminar) {
  elementos.forEach((el) => el.classList.add("saida-transicao", "saida-parado"));
  void document.body.offsetHeight;
  elementos.forEach((el) => el.classList.add("saida-oculto"));
  setTimeout(() => {
    aoTerminar();
    elementos.forEach((el) => {
      el.classList.remove("saida-transicao", "saida-parado", "saida-oculto");
    });
  }, duracaoMs);
}

const telaInicio = document.getElementById("tela-inicio");
const telaMomento = document.getElementById("tela-momento");
const telaPerimenopausa = document.getElementById("tela-perimenopausa");
const telaDesafio = document.getElementById("tela-desafio");
const telaPergunta = document.getElementById("tela-pergunta");
const telaResposta = document.getElementById("tela-resposta");
const telaResposta02 = document.getElementById("tela-resposta-02");
const telaResultado = document.getElementById("tela-resultado");
const telaDecisao = document.getElementById("tela-decisao");
const telaMinibula = document.getElementById("tela-minibula");

const perguntas = [
  {
    numero: "PERGUNTA 01",
    enunciado: "Ciclos irregulares<br>significam que a mulher<br>não pode mais engravidar.",
  },
  {
    numero: "PERGUNTA 02",
    enunciado:
      "Mesmo em <strong>transição<br>menopausal</strong>, a contracepção<br>ainda deve fazer parte do<br>cuidado com Renata.",
  },
  {
    numero: "PERGUNTA 03",
    enunciado:
      "A única questão que<br>devemos levar em conta na<br>escolha do método<br>contraceptivo é a idade<br>cronológica da paciente 40+.",
  },
  {
    numero: "PERGUNTA 04",
    enunciado:
      "Pode-se dizer à mulher que<br>ela não irá mais engravidar<br>caso não menstrue por 6<br>meses seguidos.",
  },
  {
    numero: "PERGUNTA 05",
    enunciado:
      "Ao ser constatada a<br>perimenopausa, o uso de<br>métodos contraceptivos<br>combinados não é<br>recomendado.",
  },
  {
    numero: "PERGUNTA 06",
    enunciado:
      "A contracepção hormonal<br>combinada na perimenopausa<br>pode ajudar na irregularidade<br>menstrual e também no<br>controle do sangramento<br>uterino anormal.",
    enunciadoMenor: true, // no Figma esse texto usa font-size 50px, menor que o padrão de 60px
  },
];

// Respostas que usam a tela padrão (#tela-resposta) trazem o conteúdo aqui;
// as que têm layout próprio (popup maior etc.) apontam só para a sua tela.
const respostas = [
  {
    tela: telaResposta,
    titulo: "MITO",
    numero: "RESPOSTA 01",
    explicacao:
      "A perimenopausa é uma fase de<br>transição que antecede a<br>menopausa. Nela, os ciclos podem<br>se tornar irregulares, mas a vida<br>reprodutiva não se encerra<br>imediatamente.",
    estatisticaTop: "59.53%",
    fonte:
      "O'Connor KA, Ferrell R, Brindle E, et al. Progesterone and ovulation across stages of the transition to menopause. Menopause. 2009 Nov-Dec;16(6):1178-1187.",
    fonteTop: "64.06%",
  },
  {
    tela: telaResposta02,
    titulo: "VERDADE",
  },
  {
    tela: telaResposta,
    titulo: "MITO",
    numero: "RESPOSTA 03",
    explicacao:
      "A idade isolada não é<br>contraindicação a nenhum<br>método. A escolha também deve<br>considerar histórico clínico, fatores<br>de risco cardiovascular, sintomas<br>climatéricos e prioridades<br>pessoais.",
    estatisticaTop: "62.29%",
    fonte:
      "Allen RH, Cwiak CA, Kaunitz AM. Contraception in women over 40 years of age. CMAJ. 2013;185(7):565-573.",
    fonteTop: "67.08%",
  },
  {
    tela: telaResposta,
    titulo: "MITO",
    numero: "RESPOSTA 04",
    explicacao:
      "O critério de segurança contra<br>gravidez é mais rigoroso: 12 meses<br>consecutivos sem menstruar após<br>os 50 anos, ou 24 meses sem<br>menstruar antes dos 50 anos.",
    estatisticaTop: "56.77%",
    fonte:
      "The Menopause Society. Perimenopause [Internet]. Cleveland (OH): The Menopause<br>Society; [acesso em 9 Set 2026]. Disponível em: https://menopause.org/patient-<br>education/menopausetopics/perimenopause<br><br>Australasian Menopause Society. Contraception: information sheet [Internet].<br>Melbourne: Australasian Menopause Society; [acesso em 9 Set 2026]. Disponível em:<br>https://hub.menopause.org.au/Play?pId=5ab2ab96-b8ea-4f9a-9e71-eab16812935c",
    fonteTop: "61.56%",
  },
  {
    tela: telaResposta,
    titulo: "MITO",
    numero: "RESPOSTA 05",
    popup: "assets/tela-06-resposta/popup-resposta-05.png",
    explicacao:
      "Além dos métodos combinados<br>não serem contraindicados, eles<br>desempenham um papel positivo<br>no controle de sangramento e<br>podem atenuar sintomas<br>climatéricos nessa fase.",
    estatisticaTop: "59.53%",
    fonte:
      "Fidecicchi T, Caretto M, Chen G, et al. Hormonal Contraception in Perimenopause: What<br>to Consider to Guide the Choice. Semin Reprod Med. 2025;43(2):134-144.",
    fonteTop: "64.06%",
    botaoTop: "72.40%",
  },
  {
    tela: telaResposta,
    titulo: "VERDADE",
    numero: "RESPOSTA 06",
    popup: "assets/tela-06-resposta/popup-resposta-06.png",
    explicacao:
      "A contracepção hormonal<br>combinada na perimenopausa<br>também pode reduzir sintomas<br>vasomotores, como ondas de calor.",
    estatisticaTop: "54.01%",
    fonte:
      "Fidecicchi T, Caretto M, Chen G, et al. Hormonal Contraception in Perimenopause: What<br>to Consider to Guide the Choice. Semin Reprod Med. 2025;43(2):134-144.",
    fonteTop: "58.80%",
    botaoTop: "70.73%",
  },
];

const POPUP_PADRAO = "assets/tela-06-resposta/popup-resposta.png";
const BOTAO_TOP_PADRAO = "75.16%";

let perguntaAtual = 0;
let usuarioAtualAcertos = 0;
let usuarioId;
let registroUsuario;

async function api(caminho, dados) {
  const response = await fetch(`/api/${caminho}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(dados),
    signal: AbortSignal.timeout(15000),
  });
  if (!response.ok) throw new Error("Falha ao salvar os dados");
  return response.json();
}

function registrarInicio() {
  usuarioId = crypto.randomUUID();
  perguntasRespondidas.clear();
  atualizarPontuacao(0);
  perguntaAtual = 0;
  registroUsuario = api("usuarios", { usuario_id: usuarioId });
  // A tentativa pode ser repetida com o mesmo ID, sem contar outra visita.
  registroUsuario.catch(() => {});
}

async function garantirUsuario() {
  try {
    await registroUsuario;
  } catch {
    registroUsuario = api("usuarios", { usuario_id: usuarioId });
    await registroUsuario;
  }
}
const perguntasRespondidas = new Set();

function atualizarPontuacao(acertos) {
  usuarioAtualAcertos = acertos;
  document.querySelector(".resultado-acertos").textContent = acertos;
}

atualizarPontuacao(0);

function irPara(telaDestino) {
  // Toda vez que volta pro início (mesmo no meio do quiz, ex.: ícone de casa),
  // começa uma participação nova. Sem isso, respostas de uma tentativa anterior
  // ficavam presas ao mesmo usuário e uma pergunta já respondida não atualizava
  // o resultado (o servidor ignora reenvio da mesma pergunta pelo mesmo usuário).
  if (telaDestino === telaInicio) {
    registrarInicio();
  }
  document.querySelectorAll(".tela").forEach((tela) => {
    tela.hidden = tela !== telaDestino;
  });
}

function mostrarPergunta(indice) {
  const pergunta = perguntas[indice];
  if (!pergunta) {
    irPara(telaResultado);
    return;
  }
  perguntaAtual = indice;
  document.getElementById("pergunta-numero").textContent = pergunta.numero;
  const enunciado = document.getElementById("pergunta-enunciado");
  enunciado.innerHTML = pergunta.enunciado;
  enunciado.classList.toggle("pergunta-enunciado-menor", Boolean(pergunta.enunciadoMenor));
  irPara(telaPergunta);
}

function mostrarResposta(indice) {
  const resposta = respostas[indice];
  if (!resposta) return;
  if (resposta.tela === telaResposta) {
    document.getElementById("resposta-titulo").textContent = resposta.titulo;
    document.getElementById("resposta-numero").textContent = resposta.numero;
    document.getElementById("resposta-explicacao").innerHTML = resposta.explicacao;
    document.getElementById("resposta-estatistica").style.top = resposta.estatisticaTop;
    const fonte = document.getElementById("resposta-fonte");
    fonte.innerHTML = resposta.fonte;
    fonte.style.top = resposta.fonteTop;
    document.getElementById("resposta-popup").src = resposta.popup || POPUP_PADRAO;
    document.getElementById("resposta-botao").style.top = resposta.botaoTop || BOTAO_TOP_PADRAO;
  }
  irPara(resposta.tela);
}

const TEMPO_SAIDA_INICIO = 300;
const elementosSaidaInicio = document.querySelectorAll(
  "#tela-inicio .decor, #tela-inicio .logo, #tela-inicio .titulo span, #tela-inicio .fumaca, #tela-inicio .gotas, #tela-inicio .botao-iniciar"
);

const botaoIniciar = document.querySelector(".botao-texto").closest("button");

botaoIniciar.addEventListener("click", async () => {
  if (botaoIniciar.disabled) return;
  botaoIniciar.disabled = true;
  try {
    await garantirUsuario();
  } catch {
    botaoIniciar.disabled = false;
    alert("Não foi possível iniciar. Verifique a conexão e tente novamente.");
    return;
  }
  atualizarPontuacao(usuarioAtualAcertos);
  perguntaAtual = 0;
  saidaSuave(elementosSaidaInicio, TEMPO_SAIDA_INICIO, () => {
    irPara(telaMomento);
    botaoIniciar.disabled = false;
  });
});

const ASSET_OPCAO_PADRAO = "assets/tela-02-momento/botao-opcao-fundo.png";
const ASSET_OPCAO_CERTA = "assets/tela-02-momento/botao-resposta_certa.png";
const ASSET_OPCAO_ERRADA = "assets/tela-02-momento/botao-resposta_errada.png";
const TEMPO_FEEDBACK_OPCAO = 500;
const TEMPO_SAIDA_OPCOES = 300;

const opcoesMomento = document.querySelector(".opcoes");
let respondendoMomento = false;

document.querySelectorAll(".opcao").forEach((botao) => {
  botao.addEventListener("click", () => {
    if (respondendoMomento) return;
    respondendoMomento = true;

    const correta = botao.dataset.valor === "perimenopausa";
    const fundo = botao.querySelector(".opcao-fundo");
    fundo.src = correta ? ASSET_OPCAO_CERTA : ASSET_OPCAO_ERRADA;

    if (correta) {
      // resposta certa: espera um pouco, some com as opções em opacity e segue para a próxima tela
      setTimeout(() => {
        opcoesMomento.classList.add("opcoes-saindo");
        setTimeout(() => {
          irPara(telaPerimenopausa);
          opcoesMomento.classList.remove("opcoes-saindo");
          fundo.src = ASSET_OPCAO_PADRAO;
          respondendoMomento = false;
        }, TEMPO_SAIDA_OPCOES);
      }, TEMPO_FEEDBACK_OPCAO);
    } else {
      // resposta errada: mostra o vermelho e depois volta ao normal para tentar de novo
      setTimeout(() => {
        fundo.src = ASSET_OPCAO_PADRAO;
        respondendoMomento = false;
      }, TEMPO_FEEDBACK_OPCAO);
    }
  });
});

document.getElementById("botao-continuar").addEventListener("click", () => {
  irPara(telaDesafio);
});

document.getElementById("botao-iniciar-quiz").addEventListener("click", () => {
  mostrarPergunta(0);
});

const TEMPO_FEEDBACK_RESPOSTA = 500;
const TEMPO_SAIDA_RESPOSTA = 300;

const boxPergunta = document.querySelector(".box-pergunta");
const decorSaidaPergunta = document.querySelectorAll(".tela-pergunta .decor5-sup, .tela-pergunta .decor5-inf");
let respondendoPergunta = false;

document.querySelectorAll(".resposta").forEach((botao) => {
  botao.addEventListener("click", async () => {
    if (respondendoPergunta) return;
    respondendoPergunta = true;

    let dados;
    try {
      await garantirUsuario();
      dados = await api(`perguntas/${perguntaAtual + 1}/respostas`, {
        usuario_id: usuarioId,
        resposta: botao.dataset.resposta,
      });
    } catch {
      respondendoPergunta = false;
      alert("Não foi possível salvar a resposta. Toque novamente para tentar.");
      return;
    }
    const correta = dados.correta;
    perguntasRespondidas.add(perguntaAtual);
    atualizarPontuacao(dados.acertos);
    document.querySelectorAll(".resposta-percentual").forEach((elemento) => {
      elemento.textContent = dados.percentual.toLocaleString("pt-BR", { maximumFractionDigits: 0 });
    });
    document.querySelector(".resultado-percentil").textContent =
      dados.percentil === null ? "" : dados.percentil.toLocaleString("pt-BR", { maximumFractionDigits: 2 });
    botao.classList.add(correta ? "correta" : "errada");

    // certa ou errada, mostra a cor de feedback e segue para a tela de resposta
    // (aqui, diferente da tela de momento, o erro também avança — a tela seguinte revela a resposta certa)
    setTimeout(() => {
      // as decorações dessa tela têm arte própria (diferente da tela de resposta),
      // então saem em fade antes de dar lugar às novas — em vez de sumir instantâneo
      const elementosSaida = [boxPergunta, ...decorSaidaPergunta, ...document.querySelectorAll(".resposta")];
      saidaSuave(elementosSaida, TEMPO_SAIDA_RESPOSTA, () => {
        mostrarResposta(perguntaAtual);
        elementosSaida.forEach((el) => el.classList.remove("correta", "errada"));
        respondendoPergunta = false;
      });
    }, TEMPO_FEEDBACK_RESPOSTA);
  });
});

document.querySelectorAll(".botao-proximo").forEach((botao) => {
  botao.addEventListener("click", () => {
    mostrarPergunta(perguntaAtual + 1);
  });
});

document.querySelectorAll(".icone-home").forEach((botao) => {
  botao.addEventListener("click", () => {
    if (respondendoPergunta) return;
    irPara(telaInicio);
  });
});

const TEMPO_SAIDA_RESULTADO = 300;
const elementosSaidaResultado = document.querySelectorAll(
  "#tela-resultado .bloco-vinho, #tela-resultado .decor4-base, #tela-resultado .logo4, #tela-resultado .icone-home4, #tela-resultado .etapa2-label, #tela-resultado .mulher-fundo, #tela-resultado .mito-titulo, #tela-resultado .resultado-texto, #tela-resultado .botao-iniciar-quiz"
);

document.getElementById("botao-continuar-resultado").addEventListener("click", () => {
  saidaSuave(elementosSaidaResultado, TEMPO_SAIDA_RESULTADO, () => {
    irPara(telaDecisao);
  });
});

// --- Barra "arraste para unir": a bolinha desliza da esquerda até o ponto da direita ---
(function () {
  const barra = document.getElementById("arraste-barra");
  const bolinha = document.getElementById("arraste-bolinha");
  const INICIO = 15.69; // % da largura da trilha (centro da bolinha em repouso)
  const FIM = 89.54;    // % da largura da trilha (ponto da direita)
  let arrastando = false;

  // Animação das gotas: frames 00..78 avançam em sincronia com a bolinha
  // (79..83 existem na pasta mas ficam fora: o coração já formado é o 78)
  const ULTIMO_FRAME = 78;
  const TOTAL_FRAMES = ULTIMO_FRAME + 1;
  const imagemFrames = document.getElementById("decisao-frames");
  const caminhoFrame = (i) => `assets/tela-07-decisao/frames/frame-${String(i).padStart(2, "0")}.webp`;
  const preload = [];
  for (let i = 0; i < TOTAL_FRAMES; i++) {
    const img = new Image();
    img.src = caminhoFrame(i);
    preload.push(img);
  }
  let frameAtual = 0;

  function mostrarFrame(i) {
    if (i === frameAtual) return;
    frameAtual = i;
    imagemFrames.src = caminhoFrame(i);
  }

  function posicionar(pct) {
    bolinha.style.left = pct + "%";
    const t = (pct - INICIO) / (FIM - INICIO);
    mostrarFrame(Math.round(t * (TOTAL_FRAMES - 1)));
  }

  function pctDoEvento(evento) {
    const rect = barra.getBoundingClientRect();
    const pct = ((evento.clientX - rect.left) / rect.width) * 100;
    return Math.min(FIM, Math.max(INICIO, pct));
  }

  bolinha.addEventListener("pointerdown", (evento) => {
    arrastando = true;
    bolinha.classList.add("arrastando");
    bolinha.setPointerCapture(evento.pointerId);
  });

  bolinha.addEventListener("pointermove", (evento) => {
    if (!arrastando) return;
    posicionar(pctDoEvento(evento));
  });

  function soltar(evento) {
    if (!arrastando) return;
    arrastando = false;
    bolinha.classList.remove("arrastando");
    const pct = pctDoEvento(evento);
    if (pct >= FIM - 4) {
      posicionar(FIM);
      barra.dispatchEvent(new CustomEvent("arraste-concluido"));
    } else {
      posicionar(INICIO);
    }
  }
  bolinha.addEventListener("pointerup", soltar);
  bolinha.addEventListener("pointercancel", soltar);

  // Ao unir os elementos, o vídeo toma a tela inteira; no fim, só o botão do último frame fica clicável
  const video = document.getElementById("decisao-video");
  const cta = document.getElementById("video-cta");
  barra.addEventListener("arraste-concluido", () => {
    cta.hidden = true;
    video.hidden = false;
    video.currentTime = 0;
    video.play();
  });
  // O botão "acessar minibula" já está parado na tela a partir dos 39 s (o vídeo vai até 45 s)
  const TEMPO_BOTAO = 39.5;
  function liberarBotao() {
    if (cta.hidden && !video.hidden) cta.hidden = false;
  }
  video.addEventListener("timeupdate", () => {
    if (video.currentTime >= TEMPO_BOTAO) liberarBotao();
  });
  video.addEventListener("ended", liberarBotao);
  cta.addEventListener("click", () => {
    cta.hidden = true;
    video.hidden = true;
    posicionar(INICIO);
    irPara(telaMinibula);
  });
})();

// A tela inicial já está visível no HTML no primeiro carregamento.
registrarInicio();
