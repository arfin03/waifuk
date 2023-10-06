from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import random
from pymongo import MongoClient

# Connect to your MongoDB database
client = MongoClient('mongodb+srv://shekharhatture:kUi2wj2wKxyUbbG1@cluster0.od4v7eo.mongodb.net/?retryWrites=true&w=majority')
db = client['logoooo']
collection = db['logodbb']

# fonts daal yaha mohit
fonts = ['assets/adrip1.ttf']

# sudo daal
sudo = [6404226395, 5654523936]
def add(update: Update, context: CallbackContext) -> None:
    
    if update.message.from_user.id not in sudo:
        update.message.reply_text('Sojaa...')
        return

    
    if len(context.args) < 2:
        update.message.reply_text('/add <image_url> <category>')
        return

    image_url = context.args[0]
    category = context.args[1]

    
    response = requests.get(image_url)
    response.raise_for_status()


    try:
        collection.insert_one({'category': category, 'photo': response.content})
        update.message.reply_text('Photo added successfully.')
        
        
        with BytesIO(response.content) as photo:
            context.bot.send_photo(chat_id='-1001865838715', photo=photo, caption=f'Photo added by @{update.message.from_user.username}')
    except Exception as e:
        update.message.reply_text(f'Failed to add photo: {e}')


def logo(update: Update, context: CallbackContext) -> None:
    user_input_text = " ".join(context.args)

    if not user_input_text:
        update.message.reply_text('Please provide text to draw on the image.')
        return

    
    context.user_data['user_input_text'] = user_input_text

    keyboard = [
        [InlineKeyboardButton("Boy", callback_data='boy'),
         InlineKeyboardButton("Girl", callback_data='girl'),
         InlineKeyboardButton("Scenary", callback_data='scenary')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    
    count = collection.count_documents({'category': query.data})

    random_index = random.randint(0, count - 1)


    image_data = collection.find({'category': query.data}).skip(random_index).limit(1).next()

    
    message_to_delete = query.message.message_id

    query.edit_message_text(text="Wait for some seconds...")

    # Open image and draw text
    img = Image.open(BytesIO(image_data['photo']))
    d = ImageDraw.Draw(img)
    
    font = ImageFont.truetype(random.choice(fonts), 150)
    
    # Retrieve user_input_text from context.user_data
    user_input_text = context.user_data.get('user_input_text', '')

    # Calculate width and height of the text
    w, h = d.textsize(user_input_text, font=font)

    # Calculate x and y coordinates to center the text
    x = (img.width - w) / 2
    y = (img.height - h) / 2

    d.text((x,y), user_input_text, fill=(255,255,255), font=font)

    
    img.save('output.png')
    
    
    with open('output.png', 'rb') as photo:
        message_with_photo = query.message.reply_photo(photo=photo)
        
        context.bot.delete_message(chat_id=query.message.chat_id, message_id=message_to_delete)

def main() -> None:
    updater = Updater("6504156888:AAEg_xcxqSyYIbyCZnH6zJmwMNZm3DFTmJs", use_context=True)

    updater.dispatcher.add_handler(CommandHandler('add', add))
    updater.dispatcher.add_handler(CommandHandler('logo', logo))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()

if __name__ == '__main__':
   main()
