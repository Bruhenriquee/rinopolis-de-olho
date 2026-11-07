# Roteiro de incidentes — Rinópolis de Olho

Base: Art. 48 LGPD + Resolução CD/ANPD nº 15/2024. Regime ATPP (Res. 2/2022): prazos em dobro, **6 dias úteis**,
salvo risco à integridade física ou moral (aí volta a ser 3 dias úteis).

**Incidente** = qualquer coisa que exponha, altere, apague ou deixe alguém ver dados que não devia.
Exemplos aqui: chave secreta do Supabase vazada, alguém da equipe com senha roubada, banco aberto por erro de regra,
foto com rosto publicada por engano, backup copiado por quem não devia, HD do projeto perdido.

---

## 1. Na hora (primeiras horas)

1. **Anote a data e a hora** em que você soube que dados pessoais foram afetados. É desse momento que conta o prazo.
2. **Pare o vazamento** (o que se aplicar):
   - Chave secreta vazada → Supabase → Project Settings → API Keys → **gerar nova e revogar a antiga**.
   - Conta da equipe invadida → Supabase → Authentication → Users → **trocar a senha / apagar o usuário**;
     no painel do site, aba Equipe, remover o moderador.
   - Regra do banco errada → rodar de novo o `supabase-seguranca.sql` e conferir o Security Advisor.
   - Foto ou frase indevida publicada → apagar pelo painel na hora.
   - Chave dos avisos (VAPID) vazada → gerar par novo, trocar em `config.js` e nos Secrets da função `avisar`.
   - HD perdido → trocar todas as senhas e chaves que estão em `Chaves\` e nos `.env`.
3. **Não apague provas**: antes de mexer, tire prints e baixe o histórico (painel → Histórico) e os logs do Supabase
   (Logs → API / Auth).
4. Abra uma entrada nova em `log.md` (copie o modelo do fim do arquivo).

## 2. No primeiro dia: avaliar

Responda por escrito em `log.md`:
- Que dados? (marcações, fotos, frases, denúncias, pedidos de aviso, e-mails da equipe…)
- Quantas pessoas, mais ou menos? (aparelhos distintos na tabela afetada)
- Tem criança, adolescente ou idoso identificável? (fotos, frases)
- Como aconteceu?

**Teste do Art. 5º da Res. 15/2024** — só precisa avisar a ANPD se as DUAS respostas forem "sim":
- **A.** Pode causar dano relevante às pessoas? (ex.: expor quem denunciou algo, foto com rosto, e-mail da equipe junto com senha)
- **B.** Envolve pelo menos um destes: dado sensível · criança/adolescente/idoso · dado financeiro · **senha/login** ·
  dado sob sigilo · larga escala.

No Rinópolis, o caso mais provável de "sim + sim" é **vazamento de login e senha da equipe** (item B-IV).
Marcações sem nome, sozinhas, dificilmente passam no teste A.

Se não precisar avisar: **registre mesmo assim** em `log.md`. O registro vale por 5 anos (Art. 10).

## 3. Até o 6º dia útil: avisar (se o teste deu sim + sim)

- **ANPD**: pelo formulário de comunicação de incidente no site gov.br/anpd. Modelo em `templates/anpd.md`.
  Diga que é Agente de Tratamento de Pequeno Porte.
- **Pessoas afetadas**: o mapa não tem e-mail nem telefone dos moradores, então a comunicação é **coletiva**:
  aviso fixo no topo do site por **pelo menos 3 meses** + post no Instagram do projeto.
  Moderadores afetados: e-mail individual. Modelo em `templates/titular.md`.
- Em até **20 dias úteis** depois, mande à ANPD o complemento se descobrir algo novo.

## 4. Depois

- Descubra a causa e corrija (se for no banco, rode a auditoria de novo).
- Atualize este roteiro com o que aprendeu.
- Feche a entrada no `log.md` com a data de fim da guarda (5 anos depois).

## Treino (1 vez por ano)

Pegue um cenário e simule com o relógio: "a chave secreta do Supabase apareceu num print público",
"um moderador perdeu o celular logado no painel". Se demorar mais que 6 dias úteis para decidir e avisar, o roteiro
precisa melhorar. **Próximo treino sugerido: maio de 2027.**
