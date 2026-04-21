"""
╔════════════════════════════════════════════════════════════════════════════╗
║                   🤖 BOTS 3D - REPLIT - CÓDIGO FINAL                      ║
║                                                                            ║
║  BOT 1 (Marketing): Análise de mercados                                   ║
║  BOT 2 (Printer): Configurações de impressora                             ║
║                                                                            ║
║  Copia este código inteiro para o Replit main.py                         ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

import os
import asyncio
import logging
from datetime import datetime, time
from anthropic import Anthropic
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# 🔑 CONFIGURAÇÕES - JÁ PREENCHIDAS!
# ═══════════════════════════════════════════════════════════════════════════



# ═══════════════════════════════════════════════════════════════════════════

# Clientes
client = Anthropic(api_key=API_KEY_ANTHROPIC)
bot1 = Bot(token=TOKEN_BOT1)
bot2 = Bot(token=TOKEN_BOT2)

# ═════════════════════════════════════════════════════════════════════════════
# BOT 1: MARKET INTELLIGENCE - System Prompt
# ═════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_BOT1 = """Tu és um especialista em análise de mercados de produtos 3D.

Tua tarefa AGORA (Abril 2026):
1. Identifica 5 produtos 3D em ALTA DEMANDA
2. Fornece: mercados, demanda, preço, lucro, ROI
3. Inclui URLs reais de vendas
4. Explica PORQUÊ cada um vai vender bem

FORMATO COMPACTO:
📦 PRODUTO: [Nome]
🌍 Mercados: [Países]
💰 Preço: €[valor]
💵 Lucro/unidade: €[valor]
📊 Demanda: [Alto/Médio]
📁 STL: [Existe/Criar]
🔗 URL: [link]
"""

USER_PROMPT_BOT1 = """Identifica os 5 produtos 3D mais promissores AGORA (Abril 2026).

Sê MUITO ESPECÍFICO:

📦 PRODUTO 1: [Nome específico]
🌍 PT/USA/UK: [demanda]
💰 €X | 💵 Lucro €Y
📊 Demanda: Alto ⬆️
📁 STL: [Existe]
🔗 [URL]

[Repetir para 5 produtos]
"""

# ═════════════════════════════════════════════════════════════════════════════
# BOT 2: PRINTER SETTINGS - System Prompt
# ═════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT_BOT2 = """Tu és um especialista em impressão 3D FDM com 20 anos de experiência.

Quando o utilizador descreve um objeto 3D, tu:

1. ANALISA o objeto
2. RECOMENDA configurações PERFEITAS:
   • Nozzle temperature
   • Bed temperature
   • Layer height
   • Print speed
   • Infill %
   • Support type
   • Material

3. EXPLICA PORQUÊ cada configuração
4. ALERTA sobre riscos
5. FORNECE checklist pré-impressão

FORMATO COMPACTO PARA TELEGRAM:
📋 OBJETO: [Descrição]
⚙️ CONFIGURAÇÕES: [valores]
💡 PORQUÊ: [explicação breve]
⚠️ CUIDADOS: [riscos]
✅ PRÉ-IMPRESSÃO: [checklist]
"""

# ═════════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ═════════════════════════════════════════════════════════════════════════════

def partir_mensagem(texto, limite=4096):
    """Parte um texto longo em chunks para Telegram"""
    if len(texto) <= limite:
        return [texto]
    
    chunks = []
    linhas = texto.split('\n')
    chunk_atual = ""
    
    for linha in linhas:
        if len(chunk_atual) + len(linha) + 1 <= limite:
            chunk_atual += linha + '\n'
        else:
            if chunk_atual:
                chunks.append(chunk_atual)
            chunk_atual = linha + '\n'
    
    if chunk_atual:
        chunks.append(chunk_atual)
    
    return chunks

async def analisar_mercados(chat_id):
    """Executa análise de mercados (BOT 1)"""
    print("[BOT1] Iniciando análise de mercados...")
    
    try:
        # Enviar mensagem de início
        await bot1.send_message(
            chat_id=chat_id,
            text="🔍 *BOT MARKETING: Market Intelligence*\nAnalisando mercados globais...\n⏳ Por favor aguarda (~30 segundos)",
            parse_mode='Markdown'
        )
        
        # Chamar Claude
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2000,
            system=SYSTEM_PROMPT_BOT1,
            messages=[{"role": "user", "content": USER_PROMPT_BOT1}]
        )
        
        resposta = response.content[0].text
        chunks = partir_mensagem(resposta, 4096)
        
        # Enviar em chunks
        for chunk in chunks:
            await bot1.send_message(
                chat_id=chat_id,
                text=f"📊 *PRODUTOS COM POTENCIAL:*\n\n{chunk}",
                parse_mode='Markdown'
            )
            await asyncio.sleep(0.5)
        
        # Mensagem final
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        mensagem_final = f"""
✅ *Análise Completa!*

⏰ {timestamp}
🔔 Próxima análise: Amanhã às 18h30

💡 Dica: Clica nos URLs para verificar preços actuais!
        """
        
        await bot1.send_message(
            chat_id=chat_id,
            text=mensagem_final,
            parse_mode='Markdown'
        )
        
        print("[BOT1] ✅ Análise enviada com sucesso!")
    
    except Exception as e:
        print(f"[BOT1] ❌ Erro: {e}")
        try:
            await bot1.send_message(
                chat_id=chat_id,
                text=f"❌ Erro ao processar análise: {str(e)}"
            )
        except:
            pass

# ═════════════════════════════════════════════════════════════════════════════
# BOT 2: HANDLERS
# ═════════════════════════════════════════════════════════════════════════════

async def comando_start_bot2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start do BOT 2"""
    mensagem = """
👋 *Olá! Bem-vindo ao Bot Printer: Settings Optimizer*

Este bot gera as configurações PERFEITAS para tua impressora 3D!

*Como usar:*
1. Descreve o objeto que queres imprimir
2. Recebe configurações ideais
3. Podes fazer perguntas follow-up

*Exemplos:*
• "Miniatura D&D de dragão, 8cm, muito detalhado"
• "Suporte para telemóvel, resistente"
• "Vaso decorativo com padrão"

Começa escrevendo a descrição do teu objeto!
    """
    await update.message.reply_text(mensagem, parse_mode='Markdown')

async def comando_ajuda_bot2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /ajuda do BOT 2"""
    mensagem = """
*BOT PRINTER: SETTINGS OPTIMIZER*

*O que faz?*
Gera configurações PERFEITAS para tua impressora 3D

*Fornece:*
✅ Temperatura do nozzle
✅ Temperatura da cama
✅ Altura da camada (layer height)
✅ Velocidade de impressão
✅ Tipo e % de enchimento
✅ Tipo de suporte
✅ Material recomendado
✅ Explicação de cada configuração
✅ Cuidados e riscos

Digita /novo para começar nova conversa
    """
    await update.message.reply_text(mensagem, parse_mode='Markdown')

async def comando_novo_bot2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /novo do BOT 2"""
    context.user_data['conversation'] = []
    await update.message.reply_text("✅ Conversa reiniciada! Descreve o novo objeto.")

async def processar_mensagem_bot2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa mensagens do BOT 2"""
    texto_usuario = update.message.text
    
    # Inicializar conversa
    if 'conversation' not in context.user_data:
        context.user_data['conversation'] = []
    
    # Mostrar typing
    await update.message.chat.send_action("typing")
    
    # Adicionar à conversa
    context.user_data['conversation'].append({
        "role": "user",
        "content": texto_usuario
    })
    
    try:
        # Chamar Claude
        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1500,
            system=SYSTEM_PROMPT_BOT2,
            messages=context.user_data['conversation']
        )
        
        resposta = response.content[0].text
        
        # Adicionar resposta
        context.user_data['conversation'].append({
            "role": "assistant",
            "content": resposta
        })
        
        # Enviar em chunks
        chunks = partir_mensagem(resposta, 4096)
        
        for chunk in chunks:
            await update.message.reply_text(chunk, parse_mode='Markdown')
    
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {str(e)}")
        print(f"[BOT2] Erro: {e}")

# ═════════════════════════════════════════════════════════════════════════════
# JOB: Executa BOT 1 às 18h30
# ═════════════════════════════════════════════════════════════════════════════

async def job_18h30():
    """Job que executa BOT 1 às 18h30"""
    print("[SCHEDULER] Aguardando 18h30 para executar análise...")
    
    while True:
        agora = datetime.now()
        
        # Se é 18h30, executa
        if agora.hour == 18 and agora.minute == 30:
            print(f"[SCHEDULER] ⏰ São 18h30! Executando análise...")
            await analisar_mercados(CHAT_ID)
            
            # Espera 1 minuto para não executar novamente no mesmo minuto
            await asyncio.sleep(60)
        
        # Verifica a cada 10 segundos
        await asyncio.sleep(10)

# ═════════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════════

async def main():
    """Função principal"""
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    🤖 BOTS 3D - REPLIT - INICIANDO                        ║
║                                                                            ║
║  ✅ BOT 1 (MARKETING): Análise de mercados às 18h30                       ║
║  ✅ BOT 2 (PRINTER): Chat de configurações 3D                            ║
║                                                                            ║
║  Ambos estão VIVOS e funcionando! 🚀☁️                                    ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Criar application para BOT 2
    app = Application.builder().token(TOKEN_BOT2).build()
    
    # Handlers para BOT 2
    app.add_handler(CommandHandler("start", comando_start_bot2))
    app.add_handler(CommandHandler("ajuda", comando_ajuda_bot2))
    app.add_handler(CommandHandler("novo", comando_novo_bot2))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, processar_mensagem_bot2))
    
    # Iniciar job para BOT 1 (18h30)
    asyncio.create_task(job_18h30())
    
    # Iniciar application
    await app.initialize()
    await app.start()
    
    print("\n[✅] BOT 1 (MARKETING) iniciado!")
    print("    └─ Executa automaticamente às 18h30")
    print("    └─ Análise de 5 produtos 3D em alta")
    print("    └─ Envia para Telegram automaticamente")
    
    print("\n[✅] BOT 2 (PRINTER) iniciado!")
    print("    └─ Chat contínuo no Telegram")
    print("    └─ Responde em tempo real")
    print("    └─ Configurações de impressora 3D")
    
    print("\n[📍] Deixa este Replit a correr 24/7!")
    print("[🔔] Os bots funcionam enquanto este script estiver ativo")
    
    # Keep running
    try:
        await app.run_polling()
    except KeyboardInterrupt:
        print("\n\n❌ Bots parados")
        await app.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Adeus!")
