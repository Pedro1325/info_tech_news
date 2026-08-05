# Radar de Tecnologia

Fontes: Hacker News, GitHub Trending, Lobsters e dev.to.

> Nota: a fonte original incluía Reddit, mas a API JSON deles hoje bloqueia
> (403) qualquer request sem OAuth, mesmo pra leitura pública. Troquei por
> Lobsters (lobste.rs), uma comunidade técnica no mesmo estilo do HN, com API
> JSON pública e sem necessidade de autenticação.

## Estrutura do projeto

```
tech-radar/
├── main.py                # orquestra tudo, roda 1x e sai
├── src/
│   ├── sources.py         # HN, GitHub Trending, Lobsters, dev.to
│   ├── digest.py          # monta o texto bruto + chama Claude pra gerar ideias
│   └── discord_sender.py  # posta no Discord (webhook, com quebra de mensagem)
├── .env.example            # copiar pra .env e preencher
├── .gitignore
├── venv/                    # ambiente isolado, libs ja instaladas
├── logs/                    # gerado no 1o run (tech-radar.log)
└── digests/                 # copia em markdown de cada resumo diario
```

## 1. Configurar

1. Crie um webhook no seu servidor/canal do Discord: Configurações do Canal →
   Integrações → Webhooks → Novo Webhook → copiar URL.
2. Pegue uma API key da Anthropic em https://console.anthropic.com/settings/keys
3. Copie `.env.example` para `.env` e preencha:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
   ```

## 2. Testar manualmente

```
venv\Scripts\python.exe main.py
```

Isso deve: coletar as fontes, gerar o resumo com Claude, salvar uma cópia em
`digests/AAAA-MM-DD.md` e postar no Discord. Logs ficam em `logs/tech-radar.log`.

## 3. Agendar (roda sozinho todo dia)

Via PowerShell (uma vez só, cria a tarefa no Agendador de Tarefas do Windows):

```powershell
$action = New-ScheduledTaskAction -Execute "C:\Users\polic\tech-radar\venv\Scripts\python.exe" -Argument "C:\Users\polic\tech-radar\main.py" -WorkingDirectory "C:\Users\polic\tech-radar"
$trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM
Register-ScheduledTask -TaskName "TechRadarDiario" -Action $action -Trigger $trigger -Description "Radar diario de tecnologia -> Discord"
```

Isso cria uma tarefa chamada `TechRadarDiario` que roda todo dia às 8h (ajuste o
horário como quiser). O PC precisa estar ligado nesse horário.

Para checar/editar depois: abra o "Agendador de Tarefas" do Windows e procure por
`TechRadarDiario`, ou rode `Get-ScheduledTask -TaskName TechRadarDiario`.

Para remover: `Unregister-ScheduledTask -TaskName TechRadarDiario -Confirm:$false`

## Por que isso é legal e o outro caminho (auto-postar no LinkedIn) não é

Esse projeto só faz requisições GET a APIs/páginas públicas (HN, GitHub,
Lobsters, dev.to) e usa a Claude API para resumir — nada disso viola termos de
uso de ninguém. Ele **não** posta nada no LinkedIn sozinho; a ideia é você ler
o resumo e postar manualmente, com mais repertório e ideias prontas.
