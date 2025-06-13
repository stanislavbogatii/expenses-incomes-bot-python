from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from keyboards.keyboards import get_support_inline
from form import Form
from repositories import ReportMessagesRepository, UserRepository
from models import ReportMessageModel
from utils import get_or_create_user
from config import config

router = Router()
reports_repository = ReportMessagesRepository()
user_repository = UserRepository()

@router.message(Command(commands=['support']))
@router.message(lambda message: message.text.lower() in ['support'])
async def cmd_support(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Select option:",
        reply_markup=get_support_inline()
    )

@router.callback_query(F.data == 'support')
async def cmd_support(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Select option:",
        reply_markup=get_support_inline()
    )

@router.message(Command(commands=['reports']))
@router.message(lambda message: message.text.lower() in ['reports'])
async def cmd_show_reports(message: Message, state: FSMContext):
    await state.clear()
    reports = await reports_repository.find_all()
    for report in reports:
        user = await user_repository.find_one_by_id(report.user_id)
        report_time = report.created_at.strftime("%Y-%m-%d %H:%M:%S")
        text = (
            "🐞 *New Bug Report Received!*\n\n"
            f"👤 *User:* @{user.username or 'N/A'} (`{user.user_id}`)\n"
            f"🕒 *Time:* {report_time}\n"
            f"📝 *Message:*\n{message.text}"
        )
        await message.answer(
            text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text='DELETE', callback_data=f'delete_report_{report.id}')]
                ]
            )
        )

@router.callback_query(F.data.startswith('delete_report_'))
async def cmd_delete_report(callback: CallbackQuery, state: FSMContext):
    id = callback.data.replace('delete_report_', '')
    await reports_repository.delete_one_by_id(id)
    await callback.message.edit_text('Report deleted')


@router.message(Command(commands=['bug_report']))
@router.message(lambda message: message.text.lower() in ['bug_report'])
async def cmd_bug_report(message: Message, state: FSMContext):
    await state.set_state(Form.waiting_for_write_bug_report)
    await message.answer("Write bug report (exit with /cancel): ")


@router.callback_query(F.data == 'support_bug_report')
async def cmd_write_bug_report(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_for_write_bug_report)
    await callback.message.answer("Write bug report (exit with /cancel):")
    await callback.answer()


@router.message(Form.waiting_for_write_bug_report)
async def cmd_crate_bug_report(message: Message, state: FSMContext):
    await state.clear()
    user = await get_or_create_user(message.from_user.username, message.from_user.id)
    if message.text == "/cancel":
        await message.answer("Canceled")
        return
    report = ReportMessageModel(
        user_id=user.id,
        message=message.text
    )

    if config.admin_ids is not None:
        report_time = report.created_at.strftime("%Y-%m-%d %H:%M:%S")
        admin_msg = (
            "🐞 *New Bug Report Received!*\n\n"
            f"👤 *User:* @{message.from_user.username or 'N/A'} (`{message.from_user.id}`)\n"
            f"🕒 *Time:* {report_time}\n"
            f"📝 *Message:*\n{message.text}"
        )

        await reports_repository.store(report=report)
        await message.bot.send_message(
            chat_id=config.admin_ids[0],
            text=admin_msg,
            parse_mode="Markdown"
        )

    await message.answer("Thank you for bug report, we will fix it soon")