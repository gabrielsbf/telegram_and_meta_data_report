from classes.social_net import *
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackContext

async def face_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
	request_data = update.message.text.removeprefix("/request_face ")
	date = request_data.split(' ')
	print(f"the splited dates are {str(date)}")
	response = Social_Manager("section_n").face_description([date[0], date[-1]])
	message = "Algo de errado aconteceu, solicite novamente" if Social_Manager("section_n").creating_text_for_obj(response, [date[0], date[-1]]) == False else Social_Manager("section_n").creating_text_for_obj(response, [date[0], date[-1]])
	await context.bot.send_message(chat_id=update.effective_chat.id,
								   text=message)


def run():
	telegram_cred = read_config("telegram_api")
	application = ApplicationBuilder().token(telegram_cred['token']).build()
	req_face_handler = CommandHandler('request_face', face_data)
	application.add_handlers([req_face_handler])
	print("server is running now!")
	application.run_polling()

if __name__ == "__main__":
	  run()
