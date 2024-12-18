from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, ConversationHandler, filters
import random

# Estados de la conversación
NOMBRE_SORTEO, DURACION_SORTEO, SELECCIONAR_PARTICIPANTE, SELECCIONAR_SORTEO = range(4)

# Diccionario para almacenar sorteos
sorteos = {}  # {chat_id: {"nombre": "sorteo", "duracion": "1 hora", "participantes": []}}

# Comando /start para iniciar la conversación
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "¡Hola! Soy tu bot de sorteos. Usa /crear_sorteo para empezar un nuevo sorteo."
    )

# Función para crear un sorteo
async def crear_sorteo(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "¡Vamos a crear un nuevo sorteo! Por favor, proporciona el nombre del sorteo."
    )
    return NOMBRE_SORTEO

# Recibir el nombre del sorteo
async def recibir_nombre(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    nombre_sorteo = update.message.text
    sorteos[chat_id] = {"nombre": nombre_sorteo, "duracion": None, "participantes": []}
    await update.message.reply_text(f"Nombre del sorteo: {nombre_sorteo}\nAhora, selecciona la duración del sorteo.")

    # Crear botones de duración
    keyboard = [
        [InlineKeyboardButton("1 hora", callback_data='1_hora')],
        [InlineKeyboardButton("2 horas", callback_data='2_horas')],
        [InlineKeyboardButton("3 horas", callback_data='3_horas')],
        [InlineKeyboardButton("1 día", callback_data='1_dia')],
        [InlineKeyboardButton("2 días", callback_data='2_dias')],
        [InlineKeyboardButton("3 días", callback_data='3_dias')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Selecciona la duración del sorteo:", reply_markup=reply_markup)

    return DURACION_SORTEO

# Función para seleccionar la duración del sorteo
async def seleccionar_duracion(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    duracion = query.data
    sorteos[chat_id]["duracion"] = duracion

    # Confirmar la creación del sorteo
    await query.edit_message_text(
        text=f"El sorteo '{sorteos[chat_id]['nombre']}' tiene una duración de {duracion}.\n\nUsa /apuntarse para unirte al sorteo."
    )

    return ConversationHandler.END

# Función para que los usuarios se apunten al sorteo
async def apuntarse(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    usuario = update.message.from_user.username

    if chat_id in sorteos and usuario not in sorteos[chat_id]["participantes"]:
        sorteos[chat_id]["participantes"].append(usuario)
        await update.message.reply_text(f"{usuario}, te has apuntado al sorteo.")
    else:
        await update.message.reply_text("Ya estás apuntado o no hay sorteos activos.")

# Función para realizar el sorteo y seleccionar un ganador
async def sortear(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    if chat_id in sorteos and sorteos[chat_id]["participantes"]:
        # Seleccionar un ganador aleatorio
        ganador = random.choice(sorteos[chat_id]["participantes"])
        await update.message.reply_text(f"¡El ganador del sorteo '{sorteos[chat_id]['nombre']}' es: @{ganador}! 🎉")
        sorteos[chat_id]["participantes"].clear()  # Limpiar lista de participantes
    else:
        await update.message.reply_text("No hay participantes para el sorteo.")

# Función para borrar un sorteo
async def borrar_sorteo(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    if sorteos:
        # Mostrar sorteos activos
        keyboard = [[InlineKeyboardButton(sorteo["nombre"], callback_data=str(chat_id))] for chat_id, sorteo in sorteos.items()]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Selecciona el sorteo que deseas borrar:", reply_markup=reply_markup)
        return SELECCIONAR_SORTEO
    else:
        await update.message.reply_text("No hay sorteos activos para borrar.")
        return ConversationHandler.END

# Función para confirmar y borrar el sorteo seleccionado
async def confirmar_borrar_sorteo(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    chat_id = int(query.data)  # El ID del chat de sorteos se guarda como string, lo convertimos a int

    if chat_id in sorteos:
        sorteos.pop(chat_id)
        await query.edit_message_text(f"El sorteo '{sorteos[chat_id]['nombre']}' ha sido borrado exitosamente.")
    else:
        await query.edit_message_text("No se pudo encontrar el sorteo.")

    return ConversationHandler.END

# Función para seleccionar y borrar un participante
async def borrar_participante(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    if chat_id in sorteos and sorteos[chat_id]["participantes"]:
        # Crear lista de botones con los participantes actuales
        participantes = sorteos[chat_id]["participantes"]
        keyboard = [[InlineKeyboardButton(f"Eliminar @{usuario}", callback_data=usuario)] for usuario in participantes]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Selecciona el participante que deseas eliminar del sorteo:", reply_markup=reply_markup)
        return SELECCIONAR_PARTICIPANTE
    else:
        await update.message.reply_text("No hay participantes en el sorteo para eliminar.")
        return ConversationHandler.END

# Función para confirmar y eliminar un participante
async def eliminar_participante(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id
    participante = query.data

    if participante in sorteos[chat_id]["participantes"]:
        sorteos[chat_id]["participantes"].remove(participante)
        await query.edit_message_text(f"Se ha eliminado al participante @{participante} del sorteo.")
    else:
        await query.edit_message_text("El participante no está en la lista de este sorteo.")
    
    return ConversationHandler.END

# Función para manejar las cancelaciones
async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("Operación cancelada.")
    return ConversationHandler.END

# Configuración de los handlers del bot
def main():
    # Aquí es donde debes agregar el token de tu bot:
    token = "8024684785:AAHRpwdSs8xgS3Hm2fTeRfLgcoFlxwGlA0M"  # Reemplaza "TU_TOKEN_AQUI" con el token real

    # Crear la aplicación y usar el token
    application = Application.builder().token(token).build()

    # Configuración de ConversationHandler
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('crear_sorteo', crear_sorteo)],
        states={
            NOMBRE_SORTEO: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_nombre)],
            DURACION_SORTEO: [CallbackQueryHandler(seleccionar_duracion)],
            SELECCIONAR_PARTICIPANTE: [CallbackQueryHandler(eliminar_participante)],
            SELECCIONAR_SORTEO: [CallbackQueryHandler(confirmar_borrar_sorteo)],  # Confirmar y borrar el sorteo
        },
        fallbacks=[CommandHandler('cancelar', cancel)],
    )

    # Agregar handlers de comandos
    application.add_handler(conversation_handler)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('apuntarse', apuntarse))
    application.add_handler(CommandHandler('sorteo', sortear))
    application.add_handler(CommandHandler('borrar_sorteo', borrar_sorteo))  # Comando para borrar sorteos
    application.add_handler(CommandHandler('borrar_participante', borrar_participante))  # Comando para borrar un participante

    # Iniciar el bot
    application.run_polling()

if __name__ == '__main__':
    main()
