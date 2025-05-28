import os, sys, io, asyncio, nest_asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

print("Python executable:", sys.executable)
print("VIRTUAL_ENV:", os.environ.get("VIRTUAL_ENV"))

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("Không tìm thấy biến môi trường BOT_TOKEN")

qr_image_path = r"C:\Users\Administrator\BAOBOISHOP\GITHUB\qr_vietcombank.jpg"
account_name, account_no, bank_name = "Nguyễn Văn A", "123456789", "Vietcombank"
users, orders, qr_image_data = {}, {}, None

def get_main_inline_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Telegram Premium", callback_data='premium')],
        [InlineKeyboardButton("🏦 Bank Online", callback_data='bank')],
        [
            InlineKeyboardButton("🎯 Báo Lỗi", url='https://t.me/lamgicoloi'),
            InlineKeyboardButton("💰 Nạp Tiền", callback_data='nap_tien'),
            InlineKeyboardButton("☎️ ADMIN", url='https://t.me/boibank6789'),
        ]
    ])

def get_reply_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🏠 Home")],
        [KeyboardButton("🆔 Check ID"), KeyboardButton("🛟 Support 24/7")]
    ], resize_keyboard=True)

async def load_qr_image():
    global qr_image_data
    if qr_image_data is None:
        with open(qr_image_path, 'rb') as f:
            qr_image_data = io.BytesIO(f.read())
    qr_image_data.seek(0)
    return qr_image_data

async def safe_edit_message_text(query, text, reply_markup=None, parse_mode=None):
    try:
        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        if 'Message is not modified' not in str(e):
            raise

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    users[user.id] = {"username": user.username, "balance": users.get(user.id, {}).get("balance", 0)}
    text = (
        "👋 *Shop Bảo Bối*  _xin chào!_...\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
        "• Ngoài bán mình cho tư bản ra thì nay em Bối còn bán thêm cả Bank Online & Tele Premium.\n"
        "🔰 Bank Online: Giao dịch nhanh chóng, an toàn, giá rẻ!\n"
        "🔰 Tele Premium: Nick xịn, mõm hay, nâng tầm đẳng cấp!\n"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=get_main_inline_menu(), parse_mode='Markdown')
        await update.message.reply_text(" ", reply_markup=get_reply_keyboard())
    elif update.callback_query:
        try:
            await update.callback_query.message.edit_text(text, reply_markup=get_main_inline_menu(), parse_mode='Markdown')
        except Exception as e:
            # Nếu lỗi do không phải tin nhắn text, gửi tin nhắn mới thay thế
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                reply_markup=get_main_inline_menu(),
                parse_mode='Markdown'
            )
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=" ",
            reply_markup=get_reply_keyboard()
        )

async def handle_home(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Xóa tin nhắn người dùng (nếu có thể)
    try:
        await update.message.delete()
    except Exception:
        pass
    # Gửi bảng menu chính
    text = (
        "👋 *Shop Bảo Bối*  _xin chào!_...\n"
        "➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
        "• Ngoài bán mình cho tư bản ra thì nay em Bối còn bán thêm cả Bank Online & Tele Premium.\n"
        "🔰 Bank Online: Giao dịch nhanh chóng, an toàn, giá rẻ!\n"
        "🔰 Tele Premium: Nick xịn, mõm hay, nâng tầm đẳng cấp!\n"
    )
    await update.message.reply_text(
        text,
        reply_markup=get_main_inline_menu(),
        parse_mode='Markdown'
    )

async def handle_check_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.delete()
    except Exception:
        pass
    user = update.effective_user
    user_data = users.get(user.id, {"balance": 0})
    profile = (
        "👤 *Hồ Sơ Của Bạn* 👤\n\n"
        f"🔹 Tên: {user.first_name}\n"
        f"🔹 Username: @{user.username}\n"
        f"🔹 ID: {user.id}\n"
        f"🔹 Số dư TK: {user_data.get('balance', 0)}\n"
        "🔹 Lịch sử mua hàng: ...\n"
    )
    keyboard = [[InlineKeyboardButton("↩️ Quay lại", callback_data='main_menu')]]
    await update.message.reply_text(
        profile,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.delete()
    except Exception:
        pass
    support = (
        "📚 *Hướng dẫn sử dụng Bot* 📚\n\n"
        "• Shop mình không chắc hàng rẻ nhất, nhưng dịch vụ thì đỉnh cao , cam kết không làm bạn đợi quá 5 giây là “done tiền” nha! 😎\n"
        "1️⃣ Chọn đúng sản phẩm mình muốn (đừng nhầm sang món khác nha!)\n"
        "2️⃣ Xác nhận thanh toán hóa đơn (đừng quên nhá, kẻo Shop buồn!)\n"
        "3️⃣ Quét QR hoặc thanh toán thủ công, cái nào tiện thì làm thôi!\n"
        "4️⃣ Kiểm tra kỹ lại: số tài khoản, tên người nhận, số tiền cho chuẩn nhé!\n"
        "_Lưu ý: Nội dung chuyển khoản là 10 số ID của bạn (bấm nút Check ID để lấy liền)!_\n"
        "5️⃣ Hoàn tất thanh toán, xong rồi bạn chỉ việc hóng hàng về thôi! 🎉\n\n"
        "Nếu “lỡ tay” sai sót gì, nhắn ngay ADMIN @boi39 để được cứu trợ kịp thời!\n"
    )
    keyboard = [[InlineKeyboardButton("↩️ Quay lại", callback_data='main_menu')]]
    await update.message.reply_text(
        support,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_nap_tien(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    photo = await load_qr_image()
    bank_info = (
        "💳 Thông tin chuyển khoản:\n"
        f"- Số tài khoản: {account_no}\n"
        f"- Chủ tài khoản: {account_name}\n"
        f"- Ngân hàng: {bank_name}\n\n"
        "⚠️ Vui lòng quét mã QR hoặc dùng thông tin trên để chuyển khoản !!.\n"
    )
    keyboard = [[InlineKeyboardButton("✅   DONE   ✅", callback_data='main_menu')]]
    await context.bot.send_photo(
        chat_id=query.message.chat.id,
        photo=photo,
        caption=bank_info,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = (
        "🚀*TELEGRAM PREMIUM–LỢI ÍCH SIÊU XỊN*🚀\n\n"
        "• 📤 *Gửi file 4GB* – tha hồ gửi phim dài tập không lo bóp file.\n"
        "• ⚡️ *Tải xuống nhanh* – không giới hạn, khỏi đợi mòn mỏi.\n"
        "• 🎙️ *Voice thành chữ* – lười nghe? Đọc luôn cho tiện mình toàn thế.\n"
        "• 🖼️ *Avatar động đậy* – nổi bật giữa rừng avatar đứng im.\n"
        "• 🧼 *Không quảng cáo* – tám chuyện không bị làm phiền.\n"
        "• 🤫 *Ẩn nhãn bot* – chuyển tiếp trông như “tự nghĩ ra”, sang xịn hẳn.\n"
        "• 💎 *Sticker xịn, emoji chất* – tung ra là đối phương cười xỉu.\n"
        "• 📈 *Tăng giới hạn nhóm, kênh, ghim,...* – dành cho hội nhiều bạn, nhiều drama.\n"
    )
    keyboard = [
        [
            InlineKeyboardButton("1 Tháng", callback_data='order_premium_1'),
            InlineKeyboardButton("3 Tháng", callback_data='order_premium_3'),
            InlineKeyboardButton("6 Tháng", callback_data='order_premium_6'),
        ],
        [
            InlineKeyboardButton("12 Tháng", callback_data='order_premium_12'),
            InlineKeyboardButton("Kênh Sao", url='https://t.me/boibanvip'),
            InlineKeyboardButton("↩️ Quay lại", callback_data='main_menu')
        ],
    ]
    await safe_edit_message_text(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def handle_order_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    period = query.data.split('_')[-1]
    prices = {'1': '169.000đ', '3': '369.000đ', '6': '569.000đ', '12': '869.000đ'}
    descriptions = {
        '1': "      💎 *Gói 1 tháng cao cấp* 💎\n• Tốc độ tải xuống nhanh hơn\n• Tăng giới hạn gửi tin nhắn và tệp tin\n• Biểu tượng siêu ngầu, huy hiệu VIP\n• Tăng giới hạn gửi tin nhắn và tệp tin\n• *Thanh Toán  :  169.000 VND*\n",
        '3': "      💎 *Gói 3 tháng cao cấp* 💎 \n• Tốc độ tải xuống nhanh hơn\n• Tăng giới hạn gửi tin nhắn và tệp tin\n• Biểu tượng siêu ngầu, huy hiệu VIP\n• Tăng giới hạn gửi tin nhắn và tệp tin\n• *Thanh Toán  :  369.000 VND*\n",
        '6': "      💎 *Gói 6 tháng cao cấp* 💎\n• Tốc độ tải xuống nhanh hơn\n• Tăng giới hạn gửi tin nhắn và tệp tin\n• Biểu tượng siêu ngầu, huy hiệu VIP\n• Tăng giới hạn gửi tin nhắn và tệp tin\n• *Thanh Toán  :  569.000 VND*\n",
        '12': "      💎 *Gói 12 tháng cao cấp* 💎\n• Tốc độ tải xuống nhanh hơn\n• Tăng giới hạn gửi tin nhắn và tệp tin\n• Biểu tượng siêu ngầu, huy hiệu VIP\n• Tăng giới hạn gửi tin nhắn và tệp tin\n• *Thanh Toán  :  869.000 VND*\n",
    }
    text = f"*♦️Gói được chọn:* *{period} Tháng Premium  ♦️* \n\n{descriptions.get(period, 'Không có mô tả cho gói này.')}"
    keyboard = [
        [
            InlineKeyboardButton("✅ Mua Ngay", callback_data=f'confirm_order_{period}'),
            InlineKeyboardButton("💰 Nạp Tiền", callback_data='nap_tien')
        ],
        [InlineKeyboardButton("↩️ Quay lại", callback_data='premium')]
    ]
    await safe_edit_message_text(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def handle_bank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    text = (
        "           𝐁𝐀𝐍𝐊 𝐆𝐈𝐀́ 𝐑𝐄̉ & 𝐀𝐍 𝐓𝐎𝐀̀𝐍\n\n"
        "🔹 Bank Online với hạn mức lên đến 100 triệu/tháng , 20 triệu/ngày — thoải mái giao dịch không lo giới hạn!\n"
        "🔹  Không cần giấy tờ rườm rà, chỉ cần lòng tin và… điện thoại!\n"
        "🔹 Tên CCCD random , số điện thoại của bạn sử dụng lâu dài , cực kỳ bền bỉ và riêng tư.\n"
        "🔹 Phù hợp mọi mục đích: bảo game , chạy chỉ tiêu casino , làm sạch tiền , và sử dụng cá nhân.\n"
        "🔹 Bank đã sẵn SINH TRẮC HỌC, khi nhận bank bạn chỉ cần Login và Dùng, ko cần động tác thừa nào nữa 😉"
    )
    keyboard = [
        [
            InlineKeyboardButton("Bank Web", callback_data='bank_web'),
            InlineKeyboardButton("Bank App", callback_data='bank_app'),
        ],
        [InlineKeyboardButton(" 🏡 Back Home", callback_data='main_menu')],
    ]
    await safe_edit_message_text(query, text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    print("Callback data:", query.data)  # Thêm dòng này để log callback
    await query.answer()
    data = query.data
    if data == 'nap_tien':
        await handle_nap_tien(update, context)
    elif data == 'main_menu':
        await start(update, context)
    elif data == 'check_id':
        await handle_check_id(update, context)
    elif data == 'support':
        await handle_support(update, context)
    elif data == 'premium':
        await handle_premium(update, context)
    elif data and data.startswith('order_premium_'):
        await handle_order_premium(update, context)
    elif data and data.startswith('confirm_order_'):
        keyboard = [[InlineKeyboardButton("🏡 Back Home", callback_data='main_menu')]]
        await safe_edit_message_text(
            query,
            "🎉 *Giao dịch thành công!* Cảm ơn bạn đã mua hàng tại Shop Bảo Bối.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    elif data == 'bank':
        await handle_bank(update, context)
    elif data == 'bank_web':
        await safe_edit_message_text(
            query,
            "Bạn đã chọn Bank Web.\nThông tin chi tiết sẽ được cập nhật sau.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("↩️ Quay lại", callback_data='bank')]]),
            parse_mode='Markdown'
        )
    elif data == 'bank_app':
        await safe_edit_message_text(
            query,
            "Bạn đã chọn Bank App.\nThông tin chi tiết sẽ được cập nhật sau.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("↩️ Quay lại", callback_data='bank')]]),
            parse_mode='Markdown'
        )
    else:
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="Chức năng chưa hỗ trợ.",
        )

async def main():
    nest_asyncio.apply()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^🏠 Home$"), handle_home))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^🆔 Check ID$"), handle_check_id))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^🛟 Support 24/7$"), handle_support))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bảo Bối Shop đang chạy 24/7...")
    await app.run_polling(poll_interval=0.5, timeout=10)

if __name__ == '__main__':
    asyncio.run(main())
